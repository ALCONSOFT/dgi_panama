# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2019 AlconSoft-Sistech (<http://alconsoft.net>).
#
##############################################################################

from odoo import api, fields, models
from odoo import tools
# Clase de Datos Fiscales para maestro de Proveedores
class res_partner(models.Model):
    _inherit = 'res.partner'
    ruc = fields.Char(string='RUC')
    dv = fields.Char(string='DV', size=2)
    estado = fields.Selection([('draft','New'),('open','Started'),('done','Closed')],'EStado')
    tipo_persona = fields.Selection([('1','NATURAL'),
        ('2','JURIDICO'),
        ('3','OTROS'),
        ('4','EXTRANJERO')], 'Tipo_Persona')
    concepto = fields.Many2one('anexosconceptos', string='Concepto de Anexo por Default')
# Clase Maestro de Conceptos de Anexos DGI Panamá
class anexosconcpetos(models.Model):
    _name = 'anexosconceptos'
    _description = 'Formulario de Conceptos para Anexos Fiscales de Panama v2.0'
    name = fields.Char(string='Nombre de Comcepto de Anexo', required=True)
    concepto = fields.Char(string='Código de Concepto', size=2, required=True)
    codigo_tipo_pago = fields.Selection([('0','COMPRAS'),
                                         ('1','OTROS COSTOS'),
                                         ('2','OTROS GASTOS'),
                                         ('3','GASTOS MEDICOS')], required=True)
    anexo = fields.Char(string='Código de Anexo', size=3, required=True, help='F43: INFORME DE COMPRAS, A72: ANEXO...A79, A94')
# Clase que agrega a las lineas de la factura de proveedores el concepto de los anexos
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line" 
    concepto = fields.Many2one('anexosconceptos', string='Concepto de Anexo')

class report_anexos_consolidados(models.Model):
    #####################################
    #### IMPORTANTE: NO USAR TABULAR ####
    #####################################
    _name = 'report.anexos_consolidados'
    _auto = False    
    _description = 'Reportes de Anexos Consolidados v2019-04-21'

    anexo = fields.Char(string='Anexo',size=3,required=True)
    anio = fields.Char(string='Year',readonly=True)
    tipo_persona = fields.Selection([('1','NATURAL'),('2','JURIDICO'),('3','OTROS'),('4','EXTRANJERO')],'Tipo Persona',required=True)
    ruc = fields.Char(string='RUC', size=45)
    dv = fields.Char(string='DV', size=2)
    nombre_proveedor = fields.Char('Nombre del Proveedor',size=256)
    codigo_tipo_pago = fields.Char('Tipo Pago',size=1)    #fields.Selection([('0','COMPRAS'),('1','OTROS COSTOS'),('2','OTROS GASTOS'),('3','GASTOS MEDICOS')],'Codigo Tipo Pago',required=True)
    concepto = fields.Char(string='Concepto',size=2)
    montos = fields.Float(string='Monto', readonly=True)
    periodo_fiscal = fields.Char(string='Periodo Fiscal',size=7,required=True)    
    name = fields.Char(string='Nombre del Concepto',size=256,required=True,help='Descripcion del Nombre del Concepto')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_anexos_consolidados')
        self._cr.execute("""
            create or replace view report_anexos_consolidados as (
            SELECT to_char(date_part('year'::text, ai.date_invoice), '9999'::text) AS anio,
            ac.anexo AS anexo,
            res_partner.tipo_persona AS tipo_persona,
            res_partner.ruc AS ruc,
            res_partner.dv AS dv,
            res_partner.name AS nombre_proveedor,
            CASE
            WHEN ac.codigo_tipo_pago::text = 'OTROS COSTOS'::text THEN 1
            ELSE 2
            END AS codigo_tipo_pago,
            ac.concepto AS concepto,
            round(ai.amount_untaxed_signed, 2) AS montos,
            '1' AS periodo_fiscal,
            ai.id,
            ac.name AS name
            FROM account_invoice ai
            JOIN (res_partner
            JOIN anexosconceptos ac ON res_partner.concepto = ac.id) ON ai.partner_id = res_partner.id
            ORDER BY res_partner.name
             )
            """)