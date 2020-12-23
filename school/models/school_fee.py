from cgi import parse

from odoo import models,fields,api
from odoo.exceptions import except_orm, UserError
from odoo.exceptions import ValidationError
from datetime import date, datetime


class School_fee(models.Model):
    _name = 'school.fee'

    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Student'''
        res = self.env['academic.year'].search([('current', '=',
                                                 True)])
        if not res:
            raise ValidationError(_('''There is no current Academic Year
                                           defined!Please contact to Administator!'''
                                    ))
        return res.id

    @api.multi
    @api.onchange('school_fees_line')
    def _compute_amount(self):
        amount = 0.0
        for rec in self:
            for a in rec.school_fees_line:
                amount = amount + a.amount_paid
            rec.amount_paid = amount
            rec.amount_due = rec.amount_to_be_paid - rec.amount_paid

    @api.multi
    def write(self, vals):
        if self.amount_due == 0:
            vals['status'] = 'paid'
        else:
            vals['status'] = 'unpaid'
        return super(School_fee, self).write(vals)

    name = fields.Char()
    year = fields.Many2one('academic.year', 'Academic Year', readonly=True,
                           default=check_current_year)
    currency_id = fields.Many2one(
        'res.currency', string='Currency')
    amount_paid = fields.Float("Amount Paid", store=True)
    amount_to_be_paid = fields.Float("Amount to be paid")
    amount_due = fields.Float("Amount due", store=True,)
    student = fields.Many2one("student.student","Student")
    school_fees_line = fields.Many2many('school.fee.line')
    status = fields.Selection([
        ('unpaid','Unpaid'),
        ('paid','Paid'),
    ],default='unpaid')


class School_fee_line(models.Model):
        _name = 'school.fee.line'

        @api.model
        def create(self, vals):
            seq = self.env['ir.sequence'].next_by_code('school.fee') or '/'
            vals['name'] = seq
            return super(School_fee_line, self).create(vals)

        name = fields.Char('ID', readonly=True)
        date = fields.Date("Date of Payment")
        amount_paid = fields.Float("Amount paid")
        currency_id = fields.Many2one(
            'res.currency', string='Currency')
        payment_method = fields.Selection([
            ('cash','Cash'),
            ('Bank','Bank deposit')
        ], "Payment Method", default='cash')


class School_receipt(models.TransientModel):
    _name= 'receipt.wizard'

    student = fields.Many2one("student.student", "Student")
    year = fields.Many2one('academic.year', 'Academic Year')

    @api.multi
    def print_report_pdf(self):
        ans = self.env['school.fee'].search([('student.id', '=', self.student.id)])
        data = {}
        data['form'] = self.read(['student', 'year'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['student', 'year'])[0])
        return self.env['report'].get_action(self, 'school.report_receipt_view', data=data)




class ReportSchoolFee(models.AbstractModel):

    _name = 'report.school.report_receipt_view'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        sales_records = []
        students = self.env['school.fee'].search([('student.id', '=', docs.student.id)])
        if docs.student and docs.year:
            for student in students:
                if parse(docs.student) <= parse(student.id) and parse(docs.year) >= parse(student.year):
                    sales_records.append(student);
                else:
                    raise UserError("Please enter student")

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': sales_records,
            'orders': sales_records
        }
        return self.env['report'].render('school.report_receipt_view', docargs)