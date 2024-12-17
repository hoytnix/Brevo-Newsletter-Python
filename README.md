# PaperCo Email Campaign Manager v2.0.4

A Python-based email campaign management tool that uses the Brevo API to send personalized email campaigns using CSV data and templated content.

## Features

- CSV-based recipient management
- Templated email content using Jinja2
- Secure template rendering with sandboxed environment
- Configurable logging levels and output
- Verbose mode for detailed operation tracking
- Error handling and reporting

## Prerequisites

- Python 3.x
- Brevo API key
- Required Python packages:
  - brevo_python
  - jinja2

## Installation

1. Clone the repository
2. Install required packages:

```bash
pip install brevo_python jinja2
```

## Usage

```bash
python send.py -k YOUR_API_KEY --csv recipients.csv -H email_header.txt -B email_body.txt [-v] [-l log_file.log] [--log-level LEVEL]
```

### Command Line Arguments

- `-k, --key`: Brevo API Key (required)
- `--csv`: Path to CSV database file (required)
- `-H, --header`: Email title/subject template file (required)
- `-B, --body`: Path to email body template file (required)
- `-v, --verbose`: Enable verbose output
- `-l, --log`: Path to log file (optional)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## CSV Format

The CSV file must contain at least an 'Email' column. Additional columns can be used as template variables.

Example:
```csv
Email,Name,Company
user@example.com,John Doe,ACME Inc
```

## Template Format

Both email subject and body templates support Jinja2 syntax for personalization.

Example header template:
```
Welcome to {{ Company }}, {{ Name }}!
```

Example body template:
```html
<h1>Hello {{ Name }},</h1>
<p>Welcome to {{ Company }}...</p>
```

## Logging

The application supports various logging levels and can output logs to either a file or console.

## Error Handling

The application includes comprehensive error handling for:
- CSV file loading
- Template processing
- Email sending
- API communication

## Security

- Uses Jinja2 sandboxed environment for secure template rendering
- Sanitizes template variables
- Secure API key handling
