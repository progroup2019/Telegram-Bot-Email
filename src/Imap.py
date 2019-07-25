import imaplib, email


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
