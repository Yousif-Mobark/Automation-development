import os
import json
import argparse

class OdooXMLGenerator:
    def __init__(self, model_name, fields, module_path):
        self.model_name = model_name
        self.fields = fields
        self.module_path = module_path
        self.xml_content = ""

    def create_xml_file(self):
        xml_file_name = f"{self.model_name.replace('.', '_')}_views.xml"
        xml_file_path = os.path.join(self.module_path, 'views', xml_file_name)

        self.generate_xml_content()

        with open(xml_file_path, 'w') as xml_file:
            xml_file.write(self.xml_content)

        print(f"XML file created: {xml_file_path}")
        self.update_manifest_file(xml_file_name)

    def generate_xml_content(self):
        self.xml_content += "<odoo>\n"
        
        # Form View
        self.xml_content += f"""
    <record id="view_form_{self.model_name.replace('.', '_')}" model="ir.ui.view">
        <field name="name">{self.model_name} Form</field>
        <field name="model">{self.model_name}</field>
        <field name="arch" type="xml">
            <form string="{self.model_name}">
                <sheet>
                    <group>
"""
        for field in self.fields:
            self.xml_content += f"                    <field name=\"{field['name']}\"/>\n"

        self.xml_content += """
                    </group>
                </sheet>
            </form>
        </field>
    </record>
"""
        # Tree View
        self.xml_content += f"""
    <record id="view_tree_{self.model_name.replace('.', '_')}" model="ir.ui.view">
        <field name="name">{self.model_name} Tree</field>
        <field name="model">{self.model_name}</field>
        <field name="arch" type="xml">
            <tree string="{self.model_name}">
"""
        for field in self.fields:
            self.xml_content += f"                <field name=\"{field['name']}\"/>\n"

        self.xml_content += """
            </tree>
        </field>
    </record>
"""
        # Action
        self.xml_content += f"""
    <record id="action_{self.model_name.replace('.', '_')}" model="ir.actions.act_window">
        <field name="name">{self.model_name}</field>
        <field name="res_model">{self.model_name}</field>
        <field name="view_type">form</field>
        <field name="view_mode">tree,form</field>
    </record>
"""
        # Menu Item
        self.xml_content += f"""
    <menuitem id="menu_{self.model_name.replace('.', '_')}" name="{self.model_name}" action="action_{self.model_name.replace('.', '_')}" sequence="10"/>
"""
        self.xml_content += "</odoo>\n"

    def update_manifest_file(self, xml_file_name):
        manifest_file_path = os.path.join(self.module_path, '__manifest__.py')
        with open(manifest_file_path, 'r') as manifest_file:
            manifest = manifest_file.read()

        if 'data' in manifest:
            manifest = manifest.replace('data = [', f"data = [\n    '{xml_file_name}',")
        else:
            manifest = manifest.replace('\'depends\': [', f"    'data': [\n        '{xml_file_name}',\n    ],\n    'depends': [")

        with open(manifest_file_path, 'w') as manifest_file:
            manifest_file.write(manifest)

        print(f"Updated __manifest__.py to include: {xml_file_name}")