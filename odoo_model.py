import os
import json
import argparse
import csv

class OdooModelCreator:
    def __init__(self, model_name, fields, module_path):
        self.model_name = model_name
        self.fields = fields
        self.module_path = module_path
        self.model_code = ""
        self.compute_methods = []

    def create_model_file(self, access_rights=None):
        model_file_name = f"{self.model_name.replace('.', '_')}.py"
        model_file_path = os.path.join(self.module_path, 'models', model_file_name)

        self.generate_model_code()

        with open(model_file_path, 'w') as model_file:
            model_file.write(self.model_code)

        print(f"Model file created: {model_file_path}")

        if access_rights:
            access_code = self.add_access_rights(self.model_name, access_rights)
            self.write_access_rights_file(access_code)

        self.update_init_file(model_file_name)

    def generate_model_code(self):
        self.model_code = f"""from odoo import models, fields

class {self.model_name.replace('.', '_').capitalize()}(models.Model):
    _name = '{self.model_name}'
    _description = '{self.model_name.replace(".", " ").capitalize()}'

"""
        for field in self.fields:
            self.validate_field(field)
            self.add_field_to_model(field)

        if self.compute_methods:
            self.model_code += "\n" + "\n".join(self.compute_methods)

    def validate_field(self, field):
        if field['type'] == 'Selection' and 'options' not in field:
            raise ValueError(f"Field '{field['name']}' of type 'Selection' must have 'options' defined.")
        if field['type'] in ['Many2one', 'One2many', 'Many2many'] and not field.get('options'):
            raise ValueError(f"Field '{field['name']}' of type '{field['type']}' must have a valid relation defined in 'options'.")

    def add_field_to_model(self, field):
        field_type = field['type']
        if hasattr(self, f'add_{field_type.lower()}'):
            method = getattr(self, f'add_{field_type.lower()}')
            self.model_code += method(field)
        else:
            raise ValueError(f"Unsupported field type: {field_type}")

    def add_html(self, field):
        field_name = field['name']
        return (f"    {field_name} = fields.Html("
                f"string='{field.get('string')}', "
                f"sanitize={field.get('sanitize', True)}, "
                f"sanitize_overridable={field.get('sanitize_overridable', False)}, "
                f"sanitize_tags={field.get('sanitize_tags', True)}, "
                f"sanitize_attributes={field.get('sanitize_attributes', True)}, "
                f"sanitize_style={field.get('sanitize_style', False)}, "
                f"strip_style={field.get('strip_style', False)}, "
                f"strip_classes={field.get('strip_classes', False)})\n")

    def add_image(self, field):
        field_name = field['name']
        return (f"    {field_name} = fields.Image("
                f"string='{field.get('string')}', "
                f"max_width={field.get('max_width', 0)}, "
                f"max_height={field.get('max_height', 0)}, "
                f"verify_resolution={field.get('verify_resolution', True)})\n")

    def add_selection(self, field):
        field_name = field['name']
        options = ", ".join([f"('{opt}', '{opt.capitalize()}')" for opt in field.get('options', [])])
        return f"    {field_name} = fields.Selection([\n        {options}\n    ], string='{field.get('string')}', default='{field.get('default')}', help='{field.get('help')}', readonly={field.get('readonly', False)}, required={field.get('required', False)})\n"

    def add_many2one(self, field):
        field_name = field['name']
        relation_model = field.get('options', ['model.related'])[0]
        return f"    {field_name} = fields.Many2one('{relation_model}', string='{field.get('string')}', readonly={field.get('readonly', False)}, required={field.get('required', False)})\n"

    def add_one2many(self, field):
        field_name = field['name']
        comodel_name = field.get('options', ['model.related'])[0]
        inverse_name = field['inverse_name']
        domain = field.get('domain', '[]')
        context = field.get('context', '{}')
        auto_join = field.get('auto_join', False)

        return (f"    {field_name} = fields.One2many("
                f"comodel_name='{comodel_name}', "
                f"inverse_name='{inverse_name}', "
                f"domain={domain}, "
                f"context={context}, "
                f"auto_join={auto_join}, "
                f"string='{field.get('string')}')\n")

    def add_many2many(self, field):
        field_name = field['name']
        comodel_name = field.get('options', ['model.related'])[0]

        parameters = [f"comodel_name='{comodel_name}'"]

        if 'relation' in field:
            parameters.append(f"relation='{field['relation']}'")
        else:
            parameters.append(f"relation='{self.model_name.replace('.', '_')}_{field_name}_rel'")

        if 'column1' in field:
            parameters.append(f"column1='{field['column1']}'")
        else:
            parameters.append(f"column1='{self.model_name.replace('.', '_')}_id'")

        if 'column2' in field:
            parameters.append(f"column2='{field['column2']}'")
        else:
            parameters.append(f"column2='{comodel_name.replace('.', '_')}_id'")

        if 'domain' in field:
            parameters.append(f"domain={field['domain']}")
        if 'context' in field:
            parameters.append(f"context={field['context']}")
        if 'check_company' in field:
            parameters.append(f"check_company={field['check_company']}")

        return (f"    {field_name} = fields.Many2many("
                f"{', '.join(parameters)}, "
                f"string='{field.get('string')}'"
                f")\n")

    def add_float(self, field):
        field_name = field['name']
        return f"    {field_name} = fields.Float(string='{field.get('string')}', default={field.get('default', 0)}, readonly={field.get('readonly', False)}, required={field.get('required', False)})\n"

    def add_text(self, field):
        field_name = field['name']
        return (
            f"    {field_name} = fields.Text("
            f"string='{field.get('string', '')}', "
            f"default='{field.get('default', '')}', "
            f"readonly={field.get('readonly', False)}, "
            f"required={field.get('required', False)}"
            f")\n"
        )

    def add_char(self, field):
        field_name = field['name']
        return (
            f"    {field_name} = fields.Char("
            f"string='{field.get('string', '')}', "
            f"default='{field.get('default', '')}', "
            f"readonly={field.get('readonly', False)}, "
            f"required={field.get('required', False)}"
            f")\n"
        )

    def add_integer(self, field):
        field_name = field['name']
        return f"    {field_name} = fields.Integer(string='{field.get('string')}', default={field.get('default', 0)}, readonly={field.get('readonly', False)}, required={field.get('required', False)})\n"

    def add_boolean(self, field):
        field_name = field['name']
        return f"    {field_name} = fields.Boolean(string='{field.get('string')}', default={field.get('default', False)})\n"

    def add_binary(self, field):
        field_name = field['name']
        return f"    {field_name} = fields.Binary(string='{field.get('string')}')\n"

    def add_monetary(self, field):
        field_name = field['name']
        currency_field = field.get('currency_field', 'currency_id')  # default currency field
        return f"    {field_name} = fields.Monetary(string='{field.get('string')}', currency_field='{currency_field}')\n"

    def add_date(self, field):
        field_name = field['name']
        return f"    {field_name} = fields.Date(string='{field.get('string')}', readonly={field.get('readonly', False)})\n"

    def add_datetime(self, field):
        field_name = field['name']
        return f"    {field_name} = fields.Datetime(string='{field.get('string')}', readonly={field.get('readonly', False)})\n"

    def add_access_rights(self, model_name, access_rights):
        """Generate access rights for the new model."""
        access_rows = []
        for access in access_rights:
            group = access.get('group', 'base.group_user')  # Default group
            access_rows.append([
                f"access_{model_name}_{access['name']}",
                group,
                f"{access['name'].capitalize()} Access",
                access.get('read', 0),
                access.get('write', 0),
                access.get('create', 0),
                access.get('unlink', 0)
            ])
        return access_rows

    def write_access_rights_file(self, access_rows):
        access_file_path = os.path.join(self.module_path, 'security', 'ir.model.access.csv')
        header = ["id", "group_id", "name", "perm_read", "perm_write", "perm_create", "perm_unlink"]

        # Check if the file exists and has content
        if os.path.exists(access_file_path):
            with open(access_file_path, newline='', mode='r') as access_file:
                reader = csv.reader(access_file)
                existing_header = next(reader)

                # Check if headers match regardless of order
                if set(existing_header) != set(header):
                    print(f"Warning: Header mismatch in {access_file_path}. Writing new header.")
                    access_file.seek(0)  # Reset cursor to beginning
                    access_file.truncate()  # Clear the file
                    writer = csv.writer(access_file)
                    writer.writerow(header)

        # Append new access rights
        with open(access_file_path, mode='a', newline='') as access_file:
            writer = csv.writer(access_file)
            writer.writerows(access_rows)

        print(f"Access rights updated in: {access_file_path}")
    
    def update_init_file(self, model_file_name):
        init_file_path = os.path.join(self.module_path, 'models', '__init__.py')
        with open(init_file_path, 'a') as init_file:
            init_file.write(f"\nfrom . import {model_file_name[:-3]}\n")
        
        print(f"Updated __init__.py to import: {model_file_name[:-3]}")
