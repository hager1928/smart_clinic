from odoo import models, fields, api
class Patient(models.Model):
    _name = 'clinic.patient'
    _description='Clinic Patients'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name=fields.Char(string='Patient Name' , required=True, index=True,tracking=True)
    date_of_birth=fields.Date(string='Date Of Birth', required=True,tracking=True)
    age=fields.Integer(string="Age", compute="_compute_age" , store=True)
    gender=fields.Selection([
        ('male','Male'),
        ('female','Female'),
    ], string='Gender' , required=True,tracking=True)
    email=fields.Char(string="Email",tracking=True, required=True)
    job=fields.Char(string="Patient's Job",tracking=True)
    phone=fields.Char(string="Phone",tracking=True,required=True)
    image=fields.Image(string="Patient Photo")
    blood_group=fields.Selection([
        ('a_pos','A+'),('a_neg','A-'),
        ('b_pos','B+'),('b_neg','B-'),
        ('ab_pos','AB+'),('ab_neg','AB-'),
        ('o_pos','O+'),('o_neg','O-'),     
    ], string="Blood Type",tracking=True)
    emergency_contact_name=fields.Char(string='Emergency Contact Name',tracking=True)
    emergency_contact_phone=fields.Char(string='Emergency Contact Phone',tracking=True)
    medical_history=fields.Html(string='Medical History & Notes',tracking=True)
    active=fields.Boolean(string='Active',default=True,tracking=True)
    appointment_ids = fields.One2many('clinic.appointment', 'patient_id', string='Appointments')
    user_id = fields.Many2one('res.users', string='User', tracking=True, required=True)
    #compute age depend on DOB    
    @api.depends('date_of_birth')
    def _compute_age(self):
        for patient in self:
            if patient.date_of_birth:
                today = fields.Date.today()
                dob = fields.Date.from_string(patient.date_of_birth)
                # Calculate age considering leap years/months
                patient.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                patient.age = 0

    #for the smart button action_open_patient's apponitments
    def action_open_patient_appointments(self):
        self.ensure_one()
        return {
            'name': 'Patients',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.patient', 
            'domain': [('appointment_ids.patient_id', '=', self.id)], 
            'view_mode': 'list,form',
            'target': 'current',
        }