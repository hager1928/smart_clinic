from odoo import models, fields, api
from odoo.exceptions import UserError

class ReserveAppointmentWizard(models.TransientModel):
    _name = 'reserve.appointment.wizard'
    _description = 'Reserve Appointment Wizard'

    patient_id = fields.Many2one('clinic.patient',required=True, string='Patient')
    doctor_id = fields.Many2one('clinic.doctor',required=True, string='Doctor')
    start_time = fields.Datetime(string='Start From',required=True)
    end_time = fields.Datetime(string='End At',required=True)
    reason = fields.Char(string='Reason')

    def action_submit_request_reservation(self):
            """Create Reservation and notify clinic"""
            self.ensure_one()

            patient = self.patient_id
            if self.env.user.has_group('clinic.group_patient') and not self.env.user.has_group('clinic.group_manager'):
                patient = self.env['clinic.patient'].search(
                    [('user_id', '=', self.env.user.id)],
                    limit=1,
                )
                if not patient:
                    raise UserError("Your user account is not linked to a patient record.")

            reservation = self.env['clinic.appointment'].create({
                'patient_id': patient.id,
                'doctor_id': self.doctor_id.id,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'reason': self.reason,
            })
           
            
            # 3. Return action to close wizard and show confirmation
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Request Submitted',
                    'message': 'Your reservation has been submitted successfully and the clinic has been notified.',
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
            
            