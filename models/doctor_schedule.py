from odoo import models, fields, api
from odoo.exceptions import ValidationError
class DoctorSchedule(models.Model):
    _name = 'clinic.doctor.schedule'
    _description = 'Doctor Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    doctor_id = fields.Many2one('clinic.doctor', string='Doctor', required=True, tracking=True)
    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day of Week', required=True, tracking=True)
    start_time = fields.Float(string='Start Time', required=True, tracking=True)
    end_time = fields.Float(string='End Time', required=True, tracking=True)

#python constraint time 
    @api.constrains('start_time', 'end_time')
    def _constrains_time(self):
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError("Start time must be less than end time.")

