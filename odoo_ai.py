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
        field_name = field['name']
        field_type = field['type']
        field_options = field.get('options', [])

        if field_type == 'Selection':
            options = ", ".join([f"('{opt}', '{opt.capitalize()}')" for opt in field_options])
            self.model_code += f"    {field_name} = fields.{field_type}([\n        {options}\n    ], string='{field_name.capitalize()}')\n"
        elif field_type in ['Many2one', 'One2many', 'Many2many']:
            relation_model = field_options[0] if field_options else 'model.related'
            self.model_code += f"    {field_name} = fields.{field_type}('{relation_model}', string='{field_name.capitalize()}')\n"
        elif field_type == 'Computed':
            compute_method = field.get('compute_method', 'compute_method_name')
            self.model_code += f"    {field_name} = fields.{field_type}(string='{field_name.capitalize()}', compute='{compute_method}')\n"
            self.compute_methods.append(f"    def {compute_method}(self):\n        # TODO: Implement computation for {field_name}\n        pass\n")
        elif field_type == 'Related':
            related_field = field.get('related_field', 'model.related.field')
            self.model_code += f"    {field_name} = fields.{field_type}('{related_field}', string='{field_name.capitalize()}')\n"
        else:
            self.model_code += f"    {field_name} = fields.{field_type}('{field_name.capitalize()}')\n"

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
            "type": "field_type",  // e.g., "Char", "Many2one", "Selection", etc.
            "options": ["option1", "option2"],  // Required for Selection and relation fields
            "string": "Field Label",  // Optional
            "required": true,  // Optional
            "default": "default_value",  // Optional
            "compute_method": "compute_method_name"  // Required for Computed fields
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