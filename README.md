# SMTP Newsletter Python

A robust Python application for managing and sending bulk email campaigns using SMTP with template support and comprehensive logging.

## Features

- Secure SMTP email sending with TLS support
- CSV database integration for recipient management
- Templated email content using Jinja2 with sandbox security
- Customizable email headers and body content
- Comprehensive logging system with multiple log levels
- Verbose mode for detailed operation tracking

## Prerequisites

- Python 3.x
- Required Python packages:
  - jinja2
  - typing

## Installation

```bash
git clone https://github.com/hoytnix/SMTP-Newsletter-Python.git
cd SMTP-Newsletter-Python
```

## Usage

```bash
python3 send.py \
  --smtp-host <smtp_server> \
  --smtp-port <port_number> \
  --smtp-user <username> \
  --smtp-password <password> \
  --sender-email <sender@example.com> \
  --csv <path_to_csv> \
  -H <email_header_template> \
  -B <email_body_template> \
  [-v] \
  [--log <log_file_path>] \
  [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
```

### Required Arguments

- `--smtp-host`: SMTP server hostname
- `--smtp-port`: SMTP server port number
- `--smtp-user`: SMTP authentication username
- `--smtp-password`: SMTP authentication password
- `--sender-email`: Email address used as sender
- `--csv`: Path to CSV file containing recipient data
- `-H, --header`: Path to email title/subject template
- `-B, --body`: Path to email body template file

### Optional Arguments

- `-v, --verbose`: Enable verbose output
- `--log`: Path to log file (if not specified, logs to console)
- `--log-level`: Set logging level (default: INFO)

## CSV Format

The CSV file should contain at least an 'Email' column. Additional columns can be used as template variables.

Example:
```csv
Email,Name,Company
user@example.com,John Doe,ACME Inc.
```

## Template Format

The application uses Jinja2 templates for both email subject and body. Variables from the CSV can be used in templates.

Example header template:
```
Welcome to {{ Company }}, {{ Name }}!
```

Example body template:
```html
<html>
<body>
<h1>Hello {{ Name }},</h1>
<p>Welcome to {{ Company }}!</p>
</body>
</html>
```

## Security

- Uses TLS for SMTP connections
- Implements Jinja2 sandbox for template rendering
- Sanitizes template variables
- Secure error handling and logging

## Error Handling

The application includes comprehensive error handling:
- CSV loading errors
- Template parsing errors
- SMTP connection issues
- Individual email sending failures

All errors are logged according to the specified log level.

## Version

Current version: 2.0.6
