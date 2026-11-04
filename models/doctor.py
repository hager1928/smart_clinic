from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Doctor(models.Model):
    _name='clinic.doctor'
    _description='Clinic Doctors'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Doctor Name' , required=True, index=True, tracking=True)
    phone=fields.Char(string="Phone", tracking=True)
    email=fields.Char(string="Email", tracking=True)
    specialization = fields.Selection([
        ('dermatology', 'Dermatology'),
        ('pediatrics', 'Pediatrics'),
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('gynecology', 'Gynecology'),
        ('psychiatry', 'Psychiatry'),
        ('radiology', 'Radiology'),
        ('anesthesiology', 'Anesthesiology'),
        ('ophthalmology', 'Ophthalmology'),
    ], string='Specialization', tracking=True, required=True)
    license_number=fields.Char(string="License Number", required=True, tracking=True) # constraints can be added to ensure uniqueness if needed
    active=fields.Boolean(string='Active',default=True,tracking=True)
    consultation_fee=fields.Float(string="Consultation Fee", tracking=True)
    appointment_ids = fields.One2many('clinic.appointment', 'doctor_id', string='Appointments')
    doctor_schedule_ids = fields.One2many('clinic.doctor.schedule', 'doctor_id', string='Doctor Schedules')
    user_id = fields.Many2one('res.users', string='User', tracking=True, required=True)
    #SQL constraints Can not be 2 doctors with same license number
    _sql_constraints = [
        ("license_number_unique", "unique(license_number)", "Can not be 2 doctors with same license number")
    ]
    #validation to ensure consultation fee is not negative
    @api.constrains('consultation_fee')
    def _check_consultation_fee(self):
        for doctor in self:
            if doctor.consultation_fee < 0:
                raise ValidationError("Consultation fee cannot be negative.")

    #for the smart button action_open_patient's apponitments to that doctor
    def action_open_patients(self):
        self.ensure_one()
        return {
            'name': 'Patients',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.patient', 
            'domain': [('appointment_ids.doctor_id', '=', self.id)], 
            'view_mode': 'list,form',
            'target': 'current',
        }

    #for the smart button action_open_doctor schedules to that doctor
    def action_open_doctor_schedules(self):
        self.ensure_one()
        return {
            'name': 'Doctor Schedules',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.doctor.schedule', 
            'domain': [('doctor_id', '=', self.id)], 
            'view_mode': 'list,form',
            'target': 'current',
        }
    