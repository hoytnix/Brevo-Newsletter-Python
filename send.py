#!/usr/bin/env python3

import argparse
import csv
import logging
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from jinja2 import StrictUndefined, sandbox

class PaperCoV2:
	def __init__(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str,
			 csv_path: str = None, email_title: str = None, email_body_path: str = None, sender_email: str = None,
			 verbose: bool = False, log_path: str = None, log_level: str = 'INFO',
			 single_email: str = None, single_data: Dict = None):
		self.smtp_host = smtp_host
		self.smtp_port = smtp_port
		self.smtp_user = smtp_user
		self.smtp_password = smtp_password
		self.csv_path = csv_path
		self.email_title = email_title
		self.email_body_path = email_body_path
		self.sender_email = sender_email
		self.verbose = verbose
		self.single_email = single_email
		self.single_data = single_data or {}

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

		# Initialize Jinja2 sandbox environment
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
		"""Load email header template from file."""
		try:
			with open(self.email_title, 'r', encoding='utf-8') as file:
				template = file.read()
			self.logger.info('Successfully loaded email header template')
			return template
		except Exception as e:
			self.logger.error(f'Error loading email header template: {str(e)}')
			sys.exit(1)

	def send_single_email(self):
		"""Send a single email using provided data."""
		body_template = self.load_email_body()
		header_template = self.load_email_header()

		try:
			with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
				server.starttls()
				server.login(self.smtp_user, self.smtp_password)

				# Prepare email data
				safe_data = {k: str(v) if v is not None else '' for k, v in self.single_data.items()}
				safe_data['Email'] = self.single_email

				# Create templates using sandboxed environment
				title_template = self.env.from_string(header_template)
				body_template_obj = self.env.from_string(body_template)

				# Render templates
				subject = title_template.render(**safe_data)
				html_content = body_template_obj.render(**safe_data)

				# Create message
				msg = MIMEMultipart('alternative')
				msg['Subject'] = subject
				msg['From'] = self.sender_email
				msg['To'] = self.single_email
				msg.attach(MIMEText(html_content, 'html'))

				# Send email
				server.send_message(msg)
				self.logger.info(f'Successfully sent single email to {self.single_email}')

		except Exception as e:
			self.logger.error(f'Error sending single email: {str(e)}')
			sys.exit(1)

	def send_batch_emails(self):
		"""Send batch email campaign using SMTP."""
		data = self.load_csv_data()
		body_template = self.load_email_body()
		header_template = self.load_email_header()

		try:
			with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
				server.starttls()
				server.login(self.smtp_user, self.smtp_password)

				for row in data:
					try:
						# Convert all values in row to strings
						safe_row = {k: str(v) if v is not None else '' for k, v in row.items()}

						# Create templates using sandboxed environment
						title_template = self.env.from_string(header_template)
						body_template_obj = self.env.from_string(body_template)

						# Render templates with sanitized row data
						subject = title_template.render(**safe_row)
						html_content = body_template_obj.render(**safe_row)

						# Create message
						msg = MIMEMultipart('alternative')
						msg['Subject'] = subject
						msg['From'] = self.sender_email
						msg['To'] = row['Email']
						msg.attach(MIMEText(html_content, 'html'))

						# Send email
						server.send_message(msg)
						if self.verbose:
							self.logger.info(f'Sent email to {row["Email"]}')

					except Exception as e:
						self.logger.error(f'Error sending email to {row.get("Email")}: {str(e)}')

		except Exception as e:
			self.logger.error(f'SMTP connection error: {str(e)}')
			sys.exit(1)

	def run(self):
		"""Main execution method."""
		try:
			if self.single_email:
				self.send_single_email()
				self.logger.info('Single email sent successfully')
			else:
				self.send_batch_emails()
				self.logger.info('Email campaign completed')
		except Exception as e:
			self.logger.error(f'Campaign failed: {str(e)}')
			sys.exit(1)

def main():
	parser = argparse.ArgumentParser(description='PaperCo Version 2.0 - Email Campaign Manager')
	parser.add_argument('--smtp-host', required=True, help='SMTP server hostname')
	parser.add_argument('--smtp-port', type=int, required=True, help='SMTP server port')
	parser.add_argument('--smtp-user', required=True, help='SMTP username')
	parser.add_argument('--smtp-password', required=True, help='SMTP password')
	parser.add_argument('--sender-email', required=True, help='Sender email address')
	parser.add_argument('--csv', help='Path to CSV database')
	parser.add_argument('-H', '--header', required=True, help='Email title/subject')
	parser.add_argument('-B', '--body', required=True, help='Path to email body template file')
	parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
	parser.add_argument('-l', '--log', help='Path to log file')
	parser.add_argument('--log-level', default='INFO',
			choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
			help='Set the logging level')
	parser.add_argument('--single-email', help='Send to a single email address instead of batch sending')
	parser.add_argument('--data', help='JSON string of template data for single email', default='{}')

	args = parser.parse_args()

	# Validate arguments
	if not args.single_email and not args.csv:
		parser.error('Either --csv or --single-email must be provided')

	app = PaperCoV2(
		smtp_host=args.smtp_host,
		smtp_port=args.smtp_port,
		smtp_user=args.smtp_user,
		smtp_password=args.smtp_password,
		csv_path=args.csv,
		email_title=args.header,
		email_body_path=args.body,
		sender_email=args.sender_email,
		verbose=args.verbose,
		log_path=args.log,
		log_level=args.log_level,
		single_email=args.single_email,
		single_data=eval(args.data) if args.single_email else None
	)
	app.run()

if __name__ == '__main__':
	main()
