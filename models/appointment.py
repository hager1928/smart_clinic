from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
class Appointment(models.Model):
    _name = 'clinic.appointment'
    _description = 'Clinic Appointments'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    patient_id = fields.Many2one('clinic.patient',required=True, string='Patient',tracking=True)
    doctor_id = fields.Many2one('clinic.doctor',required=True, string='Doctor',tracking=True)
    start_time = fields.Datetime(string='Start From',required=True, tracking=True)
    end_time = fields.Datetime(string='End At',required=True, tracking=True)
    reason = fields.Char(string='Reason',tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed','Confirmed'),
        ('cancelled','Cancelled'),
    ], string='Status', default='draft')
    last_reminder_sent = fields.Date(string='Last Reminder Sent', tracking=True)  # New field to track last reminder sent date

    
    #draft button
    def back_to_draft(self):
        """Convert State To Draft """
        for record in self:
            record.write({'state': 'draft'})

    #confirm button
    def convert_to_confirm(self):
        for record in self:
            record.write({'state': 'confirmed'})

    #cancel button
    def convert_to_cancel(self):
        for record in self:
            record.write({'state': 'cancelled'})

#python constraint time 
    @api.constrains('start_time', 'end_time')
    def _check_appointment_time(self):
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError("Start time must be less than end time.")


#Every day, automatically find appointments scheduled for tomorrow 
# and mark them for reminder/email processing.
#cron job to send email reminder to patients for their appointments
    def _cron_auto_confirm_appointment(self):
                    """Scheduled action - if appointment is for tomorrow , confirm it """
                    today = fields.Date.today()
                    confirmation = self.search([
                        ('start_time', '>=', today + timedelta(days=1)),
                        ('start_time', '<', today + timedelta(days=2)),
                    ])
                    for confirm in confirmation:
                        confirm.write({'state': 'confirmed'})

#send email reminder to patients for their appointments
    # def _cron_send_email_reminder(self):
    #                 """Scheduled action - send email reminder to patients for their appointments"""
    #                 today = fields.Date.today()
    #                 tomorrow = today + timedelta(days=1)
    #                 appointments = self.search([
    #                     ('start_time', '>=', tomorrow),
    #                     ('start_time', '<', tomorrow + timedelta(days=1)),
    #                     ('state', '=', 'confirmed'),
    #                 ])
    #                 for appointment in appointments:
    #                     template = self.env.ref('clinic.email_template_appointment_reminder')
    #                     if template:
    #                         template.send_mail(appointment.id, force_send=True)

#===========mail reminder for upcoming appointment=========================

    def send_reminder_email(self):
        template_xml_id = 'clinic.email_template_appointment_upcoming'
        if not template_xml_id:
            return
            
        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if not template:
            return

        for appointment in self:
            if not appointment.patient_id.email:
                appointment.message_post(body="Could not send reminder: Patient has no email.")
                continue
            template.send_mail(appointment.id, force_send=True)
            appointment.last_reminder_sent = fields.Date.today()

#if next appointment tommorrow , send email reminder
    def _cron_auto_email_reminder_next_appointment_date(self):
            """Scheduled action - if next appointment date tommorrow , send email reminder """
            today = fields.Date.today()
            reminder = self.search([
                 ('end_time', '=', today + timedelta(days=1)),
             ])
            for remind in reminder:
                remind.send_reminder_email()