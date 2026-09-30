# [H] ALPINE-CVE-2018-12558

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-12558
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12558
Type: osv

## Affected
- Alpine:v3.10: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.11: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.12: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.13: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.14: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.15: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.16: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.17: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.18: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.19: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.20: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.21: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.22: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.23: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.24: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.7: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.8: `perl-email-address` — affected >=0 <1.912-r0
- Alpine:v3.9: `perl-email-address` — affected >=0 <1.912-r0

## Details
The parse() method in the Email::Address module through 1.909 for Perl is vulnerable to Algorithmic complexity on specially prepared input, leading to Denial of Service. Prepared special input that caused this problem contained 30 form-field characters ("\f").

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12558
