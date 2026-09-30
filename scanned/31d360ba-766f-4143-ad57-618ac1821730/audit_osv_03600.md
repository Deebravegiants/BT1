# [M] ALPINE-CVE-2026-33604

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33604
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33604
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that can get Dovecot to relay a message, for example through Sieve redirect or submission relay, can use a crafted line ending in the message body to bypass the outbound protection that prevents message content from being interpreted as SMTP commands. A downstream mail server that hasn't yet fixed the SMTP smuggling vulnerability can be tricked into treating part of the message body as new SMTP commands, allowing injection of spoofed email. This is the same vulnerability class as CVE-2023-51764 and CVE-2023-51766. Where you control the receiving mail servers, ensure they reject bare carriage returns in message data. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33604
