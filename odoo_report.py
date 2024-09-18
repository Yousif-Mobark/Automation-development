import os
import ast

class OdooReportGenerator:
    def __init__(self, model_name, module_name, module_path):
        self.model_name = model_name
        self.module_name = module_name
        self.module_path = module_path
        self.xml_content = ""

    def create_report_file(self):
        report_file_name = f"{self.module_name}_report_{self.model_name.replace('.', '_')}.xml"
        report_file_path = os.path.join(self.module_path, 'reports', report_file_name)

        self.generate_report_content()

        with open(report_file_path, 'w') as report_file:
            report_file.write(self.xml_content)

        print(f"Report file created: {report_file_path}")
        self.update_manifest_file(report_file_name)

    def generate_report_content(self):
        self.xml_content += "<odoo>\n"
        
        # Report action
        self.xml_content += f"""
    <report
        id="action_report_{self.model_name.replace('.', '_')}"
        model="{self.model_name}"
        string="{self.model_name} Report"
        report_type="qweb-pdf"
        name="{self.module_name}.report_{self.model_name.replace('.', '_')}"
        file="{self.module_name}.report_{self.model_name.replace('.', '_')}"
    />
"""
        # Report template
        self.xml_content += f"""
    <template id="report_{self.model_name.replace('.', '_')}">
        <t t-call="web.html_container">
            <div class="page">
                <h2>{self.model_name} Report</h2>
                <t t-foreach="docs" t-as="doc">
                    <div>
                        <p>Name: <t t-esc="doc.name"/></p>
                        <p>Description: <t t-esc="doc.description"/></p>
                        <!-- Add more fields as needed -->
                    </div>
                </t>
            </div>
        </t>
    </template>
"""
        self.xml_content += "</odoo>\n"

    def update_manifest_file(self, report_file_name):
        manifest_file_path = os.path.join(self.module_path, '__manifest__.py')

        # Load the current manifest as a dictionary
        with open(manifest_file_path, 'r') as manifest_file:
            manifest_content = manifest_file.read()
        
        # Convert the manifest string to a dictionary
        manifest_dict = ast.literal_eval(manifest_content)

        # Check if 'data' key exists
        if 'data' in manifest_dict:
            # Add the report file to the existing data list if not already present
            if report_file_name not in manifest_dict['data']:
                manifest_dict['data'].append(report_file_name)
        else:
            # Create the 'data' key if it doesn't exist
            manifest_dict['data'] = [report_file_name]

        # Write the updated manifest back to the file
        with open(manifest_file_path, 'w') as manifest_file:
            manifest_file.write(str(manifest_dict).replace("'", "\"") + "\n")  # Convert dict back to string with double quotes

        print(f"Updated __manifest__.py to include: {report_file_name}")