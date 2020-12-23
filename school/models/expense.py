from odoo import  models,fields,api


class expense(models.Model):
    _name = 'school.expense'


    name = fields.Char('Expense name')
    description = fields.Text('Description of expenses')
    date = fields.Date('Date expensed')
    currency_id = fields.Many2one(
        'res.currency', string='Currency')
    amount = fields.Monetary()