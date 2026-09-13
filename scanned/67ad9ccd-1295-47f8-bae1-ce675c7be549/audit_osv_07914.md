# [M] STARTTLS protocol injection via MITM

## Summary
Severity: Medium
Advisory: CURL-CVE-2021-22947
Aliases: CVE-2021-22947
Published: 2021-09-15
Source: https://osv.dev/vulnerability/CURL-CVE-2021-22947
Type: osv

## Details
When curl connects to an IMAP, POP3, SMTP or FTP server to exchange data
securely using STARTTLS to upgrade the connection to TLS level, the server can
still respond and send back multiple responses before the TLS upgrade. Such
multiple *pipelined* responses are cached by curl. curl would then upgrade to
TLS but not flush the in-queue of cached responses and instead use and trust
the responses it got *before* the TLS handshake as if they were authenticated.

Using this flaw, it allows a Man-In-The-Middle attacker to first inject the
fake responses, then pass-through the TLS traffic from the legitimate server
and trick curl into sending data back to the user thinking the attacker's
injected data comes from the TLS-protected server.

Over POP3 and IMAP an attacker can inject fake response data.
