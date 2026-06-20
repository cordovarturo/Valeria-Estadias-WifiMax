{
    'name': 'Wifimax Valeria - Asistente IA',
    'version': '18.0.1.0.0',
    'category': 'Customer Service',
    'summary': 'Gestión de conversaciones de Valeria, recepcionista virtual con IA',
    'description': """
Módulo de gestión para Valeria, la asistente de IA de Wifimax ISP.
Centraliza conversaciones (WhatsApp y llamadas), identificación de clientes,
tickets, escalaciones y reportes de desempeño.
    """,
    'author': 'Wifimax ISP',
    'website': 'https://wifimax.com',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/valeria_conversation_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}