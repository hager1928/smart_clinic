# from odoo import http
# from odoo.http import request

# #odoo provide http system so we can use (http.Controller)

# class ClinicAPI(http.Controller):   #creating odoo controller called ClinicAPI
#     @http.route('/api/hello', type='json', auth='public', methods=['POST'])
#     #Create an endpoint called /api/hello
#     def hello(self, name):
#         return {
#             'message': f'Hello, {name}! Welcome to the Odoo API.'
#         }

#     #finding patient by id
#     @http.route('/api/patient/<int:patient_id>', type='json', auth='user', methods=['GET'])
#     def get_patient(self, patient_id):  
#         patient = request.env['clinic.patient'].browse(patient_id)
#         if not patient.exists():
#             return {'error': 'Patient not found'}
        
#         return {
#                 'id': patient.id,
#                 'name': patient.name,
#                 'phone': patient.phone,
#                 'blood_group': patient.blood_group,
#                 'age': patient.age,
#             }

###########n8n##############
from odoo import http
from odoo.http import request
import re

API_BEARER_TOKEN = '1478523690AQWERTNKM'  # Replace with your secret token

class DoctorAPIController(http.Controller):

    @http.route('/api/clinic/doctors', type='json', auth='public', methods=['POST'], csrf=False)
    def create_doctor(self, **kwargs):
        # 1. Get Authorization header
        auth_header = request.httprequest.headers.get('Authorization')
        
        # 2. Check Bearer Token
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'status': 'error', 'message': 'Missing or invalid Authorization header'}
        
        token = auth_header.split('Bearer ')[1].strip()
        if token != API_BEARER_TOKEN:
            return {'status': 'error', 'message': 'Unauthorized: Invalid Bearer Token'}

        # 3. Read JSON data (Odoo 17 compatible)
        data = request.get_json_data() or kwargs
        
        required_fields = ['name', 'specialization', 'license_number', 'user_id']
        for field in required_fields:
            if field not in data:
                return {'status': 'error', 'message': f'Missing required field: {field}'}

        # Helper to safely clean and convert float inputs
        def parse_float(val, default=0.0):
            if val is None or val == '':
                return default
            if isinstance(val, (int, float)):
                return float(val)
            # Remove '=' and extra whitespace or non-numeric characters except '.'
            cleaned = re.sub(r'[^\d.]', '', str(val))
            try:
                return float(cleaned) if cleaned else default
            except ValueError:
                return default

        # Helper to safely convert user_id to integer
        def parse_int(val):
            try:
                return int(val)
            except (ValueError, TypeError):
                return False

        # 4. Create doctor record with sanitized values
        doctor = request.env['clinic.doctor'].sudo().create({
            'name': data.get('name'),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'specialization': data.get('specialization'),
            'license_number': data.get('license_number'),
            'consultation_fee': parse_float(data.get('consultation_fee')),
            'user_id': parse_int(data.get('user_id')),
            'active': bool(data.get('active', True)),
        })

        return {
            'status': 'success',
            'id': doctor.id,
            'name': doctor.name,
            'license_number': doctor.license_number
        }