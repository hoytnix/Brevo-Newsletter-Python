#!/usr/bin/env python3

import argparse
import csv
import logging
import sys
from typing import Dict, List

from brevo_python import Configuration, ApiClient
from brevo_python import TransactionalEmailsApi
from brevo_python import SendSmtpEmail
from jinja2 import Template, StrictUndefined, Environment, sandbox

class PaperCoV2:
    def __init__(self, api_key: str, csv_path: str, email_title: str, 
             email_body_path: str, verbose: bool, log_path: str, log_level: str):
        self.api_key = api_key
        self.csv_path = csv_path
        self.email_title = email_title
        self.email_body_path = email_body_path
        self.verbose = verbose

        # Setup logging
        log_level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        logging.basicConfig(
            level=log_level_map.get(log_level.upper(), logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path) if log_path else logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Initialize Brevo client
        self.configuration = Configuration()
        self.configuration.api_key['api-key'] = api_key
        self.api_client = ApiClient(self.configuration)
        self.api_instance = TransactionalEmailsApi(self.api_client)

        # Initialize Jinja2 sandbox environment with safe defaults
        self.env = sandbox.SandboxedEnvironment(
            undefined=StrictUndefined,
            autoescape=True,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def load_csv_data(self) -> List[Dict]:
        """Load CSV data and return list of dictionaries for rows with email."""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = [row for row in reader if row.get('Email')]
            self.logger.info(f'Loaded {len(data)} valid email entries from CSV')
            return data
        except Exception as e:
            self.logger.error(f'Error loading CSV: {str(e)}')
            sys.exit(1)

    def load_email_body(self) -> str:
        """Load email body template from file."""
        try:
            with open(self.email_body_path, 'r', encoding='utf-8') as file:
                template = file.read()
            self.logger.info('Successfully loaded email body template')
            return template
        except Exception as e:
            self.logger.error(f'Error loading email body template: {str(e)}')
            sys.exit(1)

    def load_email_header(self) -> str:
        """Load email body template from file."""
        try:
            with open(self.email_title, 'r', encoding='utf-8') as file:
                template = file.read()
            self.logger.info('Successfully loaded email body template')
            return template
        except Exception as e:
            self.logger.error(f'Error loading email body template: {str(e)}')
            sys.exit(1)

    def send_emails(self):
        """Send batch email campaign using Brevo API."""
        data = self.load_csv_data()
        body_template = self.load_email_body()
        header_template = self.load_email_header()

        for row in data:
            try:
                # Convert all values in row to strings to prevent template rendering issues
                safe_row = {k: str(v) if v is not None else '' for k, v in row.items()}

                # Create templates using sandboxed environment
                title_template = self.env.from_string(header_template)
                body_template_obj = self.env.from_string(body_template)

                # Render templates with sanitized row data
                subject = title_template.render(**safe_row)
                html_content = body_template_obj.render(**safe_row)

                # Prepare email
                email = SendSmtpEmail(
                    to=[{"email": row['Email']}],
                    subject=subject,
                    html_content=html_content
                )

                # Send email
                response = self.api_instance.send_transac_email(email)
                if self.verbose:
                    self.logger.info(f'Sent email to {row["Email"]} with message ID: {response.message_id}')

            except Exception as e:
                self.logger.error(f'Error sending email to {row.get("Email")}: {str(e)}')

    def run(self):
        """Main execution method."""
        try:
            self.send_emails()
            self.logger.info('Email campaign completed')
        except Exception as e:
            self.logger.error(f'Campaign failed: {str(e)}')
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='PaperCo Version 2.0 - Email Campaign Manager')
    parser.add_argument('-k', '--key', required=True, help='Brevo API Key')
    parser.add_argument('--csv', required=True, help='Path to CSV database')
    parser.add_argument('-H', '--header', required=True, help='Email title/subject')
    parser.add_argument('-B', '--body', required=True, help='Path to email body template file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-l', '--log', help='Path to log file')
    parser.add_argument('--log-level', default='INFO', 
                choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                help='Set the logging level')

    args = parser.parse_args()

    app = PaperCoV2(
        api_key=args.key,
        csv_path=args.csv,
        email_title=args.header,
        email_body_path=args.body,
        verbose=args.verbose,
        log_path=args.log,
        log_level=args.log_level
    )
    app.run()

if __name__ == '__main__':
    main()