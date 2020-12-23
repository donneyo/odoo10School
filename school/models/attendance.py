from odoo import models,fields,api

class attendance(models.Model):
    _name = 'school.attendance'

    name = fields.Char()
    registered_by = fields.Many2one('res.users',"Registered by")
    date = fields.Date()
    attendance_line = fields.Many2many('attendance.line')



class attendance_line(models.Model):
    _name = 'attendance.line'

    class_id =  fields.Many2one('school.standard', 'Class')
    attendance_file = fields.Binary("Image", help="This field holds the image used as avatar for \
        this contact, limited to 1024x1024px",)
