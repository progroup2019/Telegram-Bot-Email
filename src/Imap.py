import imaplib, email, smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

"""
Function to get all messages than not be readed
"""
def get_inbox(Email, Password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    (retcode, capabilities) = mail.login(Email, Password)
    mail.list()
    mail.select('inbox')
    n = 0
    messages = []
    response = []
    (retcode, messages_primary) = mail.search(None, 'X-GM-RAW', 'category:primary')
    (retcode, messages_unread) = mail.search(None, 'X-GM-RAW', 'in:unread')
    if retcode == 'OK':
        messages_primary = messages_primary[0].split()
        messages_unread = messages_unread[0].split()
        for message in messages_primary:
            if message in messages_unread:
                messages.append(message)
    for num in messages:
        n = n + 1
        typ, data = mail.fetch(num, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                typ, data = mail.store(num, '-FLAGS', '\\Seen')
                original = email.message_from_string(response_part[1].decode("utf-8", 'ignore'))
                response.append('[' + str(n) + '] FROM: ' + original['From'] + ' - SUBJECT:' + original['Subject'])
    mail.close()
    mail.logout()
    return response


"""
Function to send a mail
"""
def send_mail(content, to, subject, file_names, YourGmailUsername, YourGmailPassword):
    smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_port = 465
    username = YourGmailUsername
    password = YourGmailPassword
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = YourGmailUsername
    msg['To'] = to
    body = MIMEText(content)
    msg.attach(body)
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    for file in file_names:
        #left validate every file here
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        email.encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)
    try:
        server.sendmail(YourGmailUsername, to, msg.as_string())
        server.quit()
        return 1
    except:
        server.quit()
        return 0

"""
Function to verify credentials
"""
def verify_login(email,password):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        (retcode, capabilities) = mail.login(email, password)
        mail.logout()
        return True
    except:
        return False

#Using regex to obtain all urls in a text
def take_urls(text):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return urls

#verify all urls with WOT api
def verify_urls(urls):
    # reports = wot_reports_for_domains(urls, KEY)
    secure = True
    # for report in reports:
    #     print (parse_attributes_for_report(report))
    #     #validate for secure
    return secure