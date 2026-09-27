# [H] ALPINE-CVE-2020-35679

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-35679
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35679
Type: osv

## Affected
- Alpine:v3.11: `opensmtpd` — affected >=0 <6.6.4p1-r1
- Alpine:v3.12: `opensmtpd` — affected >=0 <6.6.4p1-r2
- Alpine:v3.13: `opensmtpd` — affected >=0 <6.7.1p1-r1

## Details
smtpd/table.c in OpenSMTPD before 6.8.0p1 lacks a certain regfree, which might allow attackers to trigger a "very significant" memory leak via messages to an instance that performs many regex lookups.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35679
