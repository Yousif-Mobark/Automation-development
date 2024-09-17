import os
import json
import argparse

class OdooModelCreator:
    def __init__(self, model_name, fields, module_path):
        self.model_name = model_name
        self.fields = fields
        self.module_path = module_path
        self.model_code = ""
        self.compute_methods = []

    def create_model_file(self):
        model_file_name = f"{self.model_name.replace('.', '_')}.py"
        model_file_path = os.path.join(self.module_path, 'models', model_file_name)

        self.generate_model_code()

        with open(model_file_path, 'w') as model_file:
            model_file.write(self.model_code)

        print(f"Model file created: {model_file_path}")
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

    # Other field methods...
    def add_float(self, field):
        field_name = field['name']
        return f"    {field_name} = fields.Float(string='{field.get('string')}', default={field.get('default', 0)}, readonly={field.get('readonly', False)}, required={field.get('required', False)})\n"

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

    def update_init_file(self, model_file_name):
        init_file_path = os.path.join(self.module_path, 'models', '__init__.py')
        with open(init_file_path, 'a') as init_file:
            init_file.write(f"\nfrom . import {model_file_name[:-3]}\n")
        
        print(f"Updated __init__.py to import: {model_file_name[:-3]}")

def print_documentation():
    print("\n### JSON Structure Documentation ###")
    print("""{
    "model_name": "your.model.name",
    "fields": [
        {
            "name": "field_name",
            "type": "field_type",  // e.g., "Char", "Image", "Many2one", etc.
            "string": "Field Label",  // Optional
            "readonly": true,  // Optional
            "required": false,  // Optional
            "default": "default_value",  // Optional
            "compute": "compute_method_name",  // Optional for computed fields
            "index": "btree",  // Optional for indexing
            "help": "Tooltip text",  // Optional tooltip
            "max_width": 1024,  // Optional for Image fields
            "max_height": 768,  // Optional for Image fields
            "verify_resolution": true  // Optional for Image fields
            "sanitize": true,  // Optional for Html fields
            "sanitize_overridable": false,  // Optional for Html fields
            "sanitize_tags": true,  // Optional for Html fields
            "sanitize_attributes": true,  // Optional for Html fields
            "sanitize_style": false,  // Optional for Html fields
            "strip_style": false,  // Optional for Html fields
            "strip_classes": false  // Optional for Html fields

        }
    ]
}""")
    print("Ensure that all required fields are present and correctly formatted.")

def main(data_file, module_path):
    with open(data_file, 'r') as json_file:
        data = json.load(json_file)
    
    model_name = data.get('model_name')
    fields = data.get('fields')

    if not model_name or not isinstance(fields, list):
        print("Error: 'model_name' must be a string and 'fields' must be a list.")
        print_documentation()
        return

    model_creator = OdooModelCreator(model_name, fields, module_path)
    model_creator.create_model_file()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an Odoo model from a JSON definition.")
    parser.add_argument('--data-file', type=str, required=True, help='Path to the JSON file containing model definition.')
    parser.add_argument('--module-path', type=str, required=True, help='Path to your Odoo module (e.g., /path/to/your/module).')
    
    try:
        args = parser.parse_args()
        main(args.data_file, args.module_path)
    except SystemExit:
        parser.print_usage()
        print("\nPlease provide the required options.")