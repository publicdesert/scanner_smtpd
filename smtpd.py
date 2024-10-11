import os
import logging
import sys
import json
from aiosmtpd.controller import Controller
from email import message_from_bytes
from email.policy import default

CONFIG_FILE = 'config.json'

def create_default_config():
    config_data = {
        'WHITELISTED_IPS': ['127.0.0.1'],
        'ATTACHMENTS_DIR': 'attachments',
        'LOG_FILE': 'log.txt',
        'LISTEN_ADDRESS': '0.0.0.0',
        'LISTEN_PORT': 2525
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)
    print(f"Configuration file '{CONFIG_FILE}' created. Please review the file and restart the script.")
    sys.exit(1)

def read_config():
    if not os.path.exists(CONFIG_FILE):
        create_default_config()

    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    return config_data

config = read_config()

WHITELISTED_IPS = config.get('WHITELISTED_IPS', [])
ATTACHMENTS_DIR = config.get('ATTACHMENTS_DIR', 'attachments')
LOG_FILE = config.get('LOG_FILE', 'email_log.txt')
LISTEN_ADDRESS = config.get('LISTEN_ADDRESS', '0.0.0.0')
LISTEN_PORT = config.get('LISTEN_PORT', 2525)

if not os.path.exists(ATTACHMENTS_DIR):
    os.makedirs(ATTACHMENTS_DIR)

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])

class EmailHandler:
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        ip, port = peer
        
        if ip not in WHITELISTED_IPS:
            logging.warning(f"Rejected email from non-whitelisted IP: {ip}")
            return '550 IP address not allowed'

        logging.info(f"Accepted email from {mailfrom} to {rcpttos}, from IP: {ip}")

        msg = message_from_bytes(data, policy=default)

        if msg.is_multipart():
            for part in msg.iter_attachments():
                content_disposition = part.get('Content-Disposition', None)
                if content_disposition and 'attachment' in content_disposition:
                    filename = part.get_filename()

                    if filename:
                        filepath = os.path.join(ATTACHMENTS_DIR, filename)
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        logging.info(f"Saved attachment: {filename}")
        else:
            logging.info("No attachments found.")

        return '250 Message accepted'

if __name__ == '__main__':
    handler = EmailHandler()
    controller = Controller(handler, hostname=LISTEN_ADDRESS, port=LISTEN_PORT)
    controller.start()

    logging.info("SMTP server is running. Press Ctrl+C to stop.")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Stopping SMTP server.")
        controller.stop()

