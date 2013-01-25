import time
from report import report_sxw
from osv import osv

class invoice_facturae_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_facturae_html, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'set_global_data': self._set_global_data,
            'facturae_data_dict': self._facturae_data_dict,
            'split_string': self._split_string,
            'company_address': self._company_address,
            'subcompany_address': self._subcompany_address,
            'get_invoice_sequence': self._get_invoice_sequence,
            'get_approval': self._get_approval,
            'get_taxes': self._get_taxes,
            'get_taxes_ret': self._get_taxes_ret,
            'float': float,
            'exists_key': self._exists_key,
            'get_data_partner' : self._get_data_partner
        })
        self.taxes = []

    def _exists_key(self, key):
        return self.invoice._columns.has_key(key)

    def _set_global_data(self, o):
        try:
            self.setLang(o.partner_id.lang)
        except Exception, e:
            print "exception: %s"%( e )
            pass
        try:
            self._get_company_address(o.id)
        except Exception, e:
            print "exception: %s"%( e )
            pass
        try:
            self._get_facturae_data_dict(o)
        except Exception, e:
            print "exception: %s"%( e )
            pass
        return ""

    def _get_approval(self):
        #~ return self.approval
        return '77'

    def _get_invoice_sequence(self):
        return self.sequence

    def _set_invoice_sequence_and_approval(self, invoice_id):
        context = {}
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        sequence_obj = pool.get('ir.sequence')
        invoice = invoice_obj.browse(self.cr, self.uid, [invoice_id], context=context)[0]
        context.update({'number_work': invoice.number})
        sequence = invoice.invoice_sequence_id or False
        sequence_id = sequence and sequence.id or False
        self.sequence = sequence
        approval = sequence and sequence.approval_id or False
        approval_id = approval and approval.id or False
        self.approval = approval
        return sequence, approval

    def _get_taxes(self):
        return self.taxes

    def _get_taxes_ret(self):
        try:
            return self.taxes_ret
        except:
            pass
        return []

    def _split_string(self, string, length=100):
        if string:
            for i in range(0, len(string), length):
                string = string[:i] + ' ' + string[i:]
        return string

    def _get_company_address(self, invoice_id):
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        partner_obj = pool.get('res.partner')
        address_obj = pool.get('res.partner')
        invoice = invoice_obj.browse(self.cr, self.uid, invoice_id)
        partner_id = invoice.company_id.parent_id and invoice.company_id.parent_id.partner_id.id or invoice.company_id.partner_id.id
        self.invoice = invoice
        address_id = partner_obj.address_get(self.cr, self.uid, [partner_id], ['invoice'])['invoice']
        self.company_address_invoice = address_obj.browse(self.cr, self.uid, partner_id)

        subpartner_id = invoice.company_id.partner_id.id
        if partner_id == subpartner_id:
            self.subcompany_address_invoice = self.company_address_invoice
        else:
            subaddress_id = partner_obj.address_get(self.cr, self.uid, [subpartner_id], ['invoice'])['invoice']
            self.subcompany_address_invoice = address_obj.browse(self.cr, self.uid, subaddress_id)
        return ""

    def _company_address(self):
        return self.company_address_invoice

    def _subcompany_address(self):
        return self.subcompany_address_invoice

    def _facturae_data_dict(self):
        return self.invoice_data_dict

    def _get_facturae_data_dict(self, invoice):
        self._set_invoice_sequence_and_approval( invoice.id )
        self.taxes = [tax for tax in invoice.tax_line if tax.tax_percent >= 0.0]
        self.taxes_ret = [tax for tax in invoice.tax_line if tax.tax_percent < 0.0]
        return ""
        
    def _get_data_partner(self, partner_id):
        partner_obj = self.pool.get('res.partner')
        res = {}
        address_invoice_id = partner_obj.search(self.cr, self.uid, [('parent_id', '=', partner_id.id), ('type', '=', 'invoice')])
        if address_invoice_id:
            address_invoice = partner_obj.browse(self.cr, self.uid, address_invoice_id[0])
            if address_invoice:
                res.update({
                    'street' : address_invoice.street or False,
                    'street3' : address_invoice.street3 or False,
                    'street4' : address_invoice.street4 or False,
                    'street2' : address_invoice.street2 or False,
                    'city' : address_invoice.city or False,
                    'state' : address_invoice.state_id and address_invoice.state_id.name or False,
                    'city2' : address_invoice.city2 or False,
                    'zip' : address_invoice.zip or False,
                    'vat' : address_invoice._columns.has_key('vat_split') and address_invoice.vat_split or address_invoice.vat or False,
                    'phone' : address_invoice.phone or False,
                    'fax' : address_invoice.fax or False,
                    'mobile' : address_invoice.mobile or False,
                    })
        return res
        
report_sxw.report_sxw('report.account.invoice.facturae.webkit',
                       'account.invoice', 
                       'addons/l10n_mx_facturae/report/invoice_facturae_html.mako',
                       header=False,
                       parser=invoice_facturae_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
