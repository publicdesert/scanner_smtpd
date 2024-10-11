# Mock SMTP server for Document Scanning
My MFP only allows documents to be scanned using either Windows-only software, saving to a thumb drive or sending the document via an SMTP server. I wanted an easy way to access scanned documents from all my devices without having to install any special software.

This Python script provides a mock SMTP server using the `aiosmtpd` library that behaves in the following way:
* Accept all mails from a list of whitelisted IP addresses
* Ignore the recipient as it is irrelevant in this use case
* Extract the attachments from the mails and save them to a specified directory
