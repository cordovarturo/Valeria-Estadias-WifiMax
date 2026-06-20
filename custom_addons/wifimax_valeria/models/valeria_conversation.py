from odoo import models, fields


class ValeriaConversation(models.Model):
    _name = 'wifimax.valeria.conversation'
    _description = 'Conversación de Valeria con un cliente'
    _order = 'create_date desc'

    name = fields.Char(
        string='Referencia',
        required=True,
        default='Nueva conversación',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
    )
    channel = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp'),
            ('call', 'Llamada telefónica'),
        ],
        string='Canal',
        required=True,
        default='call',
    )
    phone_number = fields.Char(
        string='Número de teléfono',
    )
    start_datetime = fields.Datetime(
        string='Inicio',
        default=fields.Datetime.now,
    )
    end_datetime = fields.Datetime(
        string='Fin',
    )
    resolved = fields.Boolean(
        string='Resuelta por Valeria',
        default=False,
    )
    escalated = fields.Boolean(
        string='Escalada a humano',
        default=False,
    )
    summary = fields.Text(
        string='Resumen de la conversación',
    )