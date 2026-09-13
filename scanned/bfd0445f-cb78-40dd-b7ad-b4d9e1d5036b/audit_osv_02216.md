# [H] ALPINE-CVE-2021-32749

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32749
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32749
Type: osv

## Affected
- Alpine:v3.15: `fail2ban` — affected >=0.10.0 <0.11.2-r1
- Alpine:v3.16: `fail2ban` — affected >=0.10.0 <0.11.2-r2
- Alpine:v3.17: `fail2ban` — affected >=0.10.0 <0.11.2-r2
- Alpine:v3.18: `fail2ban` — affected >=0.10.0 <0.11.2-r2
- Alpine:v3.19: `fail2ban` — affected >=0.10.0 <0.11.2-r2
- Alpine:v3.20: `fail2ban` — affected >=0.10.0 <0.11.2-r2
- Alpine:v3.21: `fail2ban` — affected >=0.10.0 <0.11.2-r2
- Alpine:v3.22: `fail2ban` — affected >=0.10.0 <0.11.2-r2
- Alpine:v3.23: `fail2ban` — affected >=0.10.0 <0.11.2-r2
- Alpine:v3.24: `fail2ban` — affected >=0.10.0 <0.11.2-r2

## Details
fail2ban is a daemon to ban hosts that cause multiple authentication errors. In versions 0.9.7 and prior, 0.10.0 through 0.10.6, and 0.11.0 through 0.11.2, there is a vulnerability that leads to possible remote code execution in the mailing action mail-whois. Command `mail` from mailutils package used in mail actions like `mail-whois` can execute command if unescaped sequences (`\n~`) are available in "foreign" input (for instance in whois output). To exploit the vulnerability, an attacker would need to insert malicious characters into the response sent by the whois server, either via a MITM attack or by taking over a whois server. The issue is patched in versions 0.10.7 and 0.11.3. As a workaround, one may avoid the usage of action `mail-whois` or patch the vulnerability manually.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32749
