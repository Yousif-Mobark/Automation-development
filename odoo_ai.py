import os
import json
import argparse
from odoo_model import OdooModelCreator
from odoo_report import OdooReportGenerator
from xml_generator import OdooXMLGenerator

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
            "verify_resolution": true,  // Optional for Image fields
            "sanitize": true,  // Optional for Html fields
            "sanitize_overridable": false,  // Optional for Html fields
            "sanitize_tags": true,  // Optional for Html fields
            "sanitize_attributes": true,  // Optional for Html fields
            "sanitize_style": false,  // Optional for Html fields
            "strip_style": false,  // Optional for Html fields
            "strip_classes": false  // Optional for Html fields
        }
    ],
    "report": true  // Optional, indicates if a report should be generated
}""")
    print("Ensure that all required fields are present and correctly formatted.")

def main(data_file, module_path):
    with open(data_file, 'r') as json_file:
        data = json.load(json_file)
    
    model_name = data.get('model_name')
    fields = data.get('fields')
    report_enabled = data.get('report', False)  # Default to False if not present
    views_enabled = data.get('views', True)  # Default to False if not present
    access_rights = data.get('access_rights', [])

    if not model_name or not isinstance(fields, list):
        print("Error: 'model_name' must be a string and 'fields' must be a list.")
        print_documentation()
        return

    # Create model file
    model_creator = OdooModelCreator(model_name, fields, module_path)
    model_creator.create_model_file(access_rights=access_rights)
    if views_enabled:
        views_generator = OdooXMLGenerator(model_name, fields, module_path)
        views_generator.create_xml_file()
    # If report is enabled, initialize the report generator
    if report_enabled:
        report_generator = OdooReportGenerator(model_name, data.get('module_name', 'your_module_name'), module_path)
        report_generator.create_report_file()

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