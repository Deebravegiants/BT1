# [M] ALPINE-CVE-2023-27043

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-27043
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27043
Type: osv

## Affected
- Alpine:v3.17: `python3` — affected >=0 <3.10.15-r0
- Alpine:v3.18: `python3` — affected >=0 <3.11.10-r0
- Alpine:v3.19: `python3` — affected >=0 <3.11.10-r0
- Alpine:v3.20: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.21: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.24: `python3` — affected >=0 <3.12.6-r0

## Details
The email module of Python through 3.11.3 incorrectly parses e-mail addresses that contain a special character. The wrong portion of an RFC2822 header is identified as the value of the addr-spec. In some applications, an attacker can bypass a protection mechanism in which application access is granted only after verifying receipt of e-mail to a specific domain (e.g., only @company.example.com addresses may be used for signup). This occurs in email/_parseaddr.py in recent versions of Python.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27043
