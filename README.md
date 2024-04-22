Here's an example of a README file for your project. This document includes the introduction to the project, instructions for setting up, using, and a brief description of each major function provided by the code.

---

# Project Title: Spreadsheet Order Tracking

## Introduction
This project is designed to track order statuses by interfacing with Google Sheets and Gmail to update and monitor shipping information. It utilizes Google APIs to fetch and update spreadsheets based on emails received concerning order shipments. Additionally, it logs actions and stores order statuses locally in a JSON format for reference.

## Features
- Fetch and update Google Sheets with shipping and order statuses.
- Search Gmail for shipping confirmations and tracking numbers.
- Log activities with timestamps and colored outputs for easy monitoring.
- Periodic checks and updates with multi-threading support.

## Prerequisites
- Python 3.6+
- Google API credentials for Sheets and Gmail
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client`, `colorama` Python packages

## Installation

1. Clone this repository:
   ```bash
   git clone https://your-repository-url
   cd your-project-directory
   ```

2. Install required packages:
   ```bash
   pip install --upgrade google-auth google-auth-oauthlib google-api-python-client colorama
   ```

3. Set up Google API credentials:
   - Visit the Google Cloud Console and create a new project.
   - Enable the Sheets and Gmail API.
   - Create credentials for the OAuth client ID.
   - Download the credentials JSON file and save it as `credentials.json` in your project directory.

4. Generate tokens:
   - Run the script once to generate `tokenSheet.json` and `token.json` for accessing Sheets and Gmail APIs.

## Usage

### Configuring your settings
1. Modify `settings.json` to include your specific spreadsheet IDs:
   ```json
   {
     "spreadsheets_id": ["your_spreadsheet_id_here"]
   }
   ```

### Running the application
Execute the script to start the tracking:
```bash
python your_script_name.py
```
This will continuously monitor and update the spreadsheets every hour.

## Functions Overview

- `scrap_spreadsheet()`: Main function to fetch spreadsheet data, check for orders, and update statuses.
- `create_buildSheets()` and `create_build()`: Functions to authenticate and create service builds for Google Sheets and Gmail.
- `log()`, `log_success()`, `log_error()`: Logging functions that output information with timestamps and color-coded importance.
- `save_status_to_json()`: Saves order statuses to a local JSON file for backup and offline tracking.
- `update_status()`: Updates a specific order's tracking and status in the spreadsheet.

## Additional Information

- Make sure to regularly update your `.gitignore` file to include sensitive files such as `credentials.json`, `token*.json`, and any other configuration files that contain sensitive information.
- It is recommended to set proper scopes and permissions for the Google APIs to ensure the security of your data.
