# [H] ALPINE-CVE-2017-7668

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7668
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7668
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.3: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.4: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.5: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.26-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.26-r0

## Details
The HTTP strict parsing changes added in Apache httpd 2.2.32 and 2.4.24 introduced a bug in token list parsing, which allows ap_find_token() to search past the end of its input string. By maliciously crafting a sequence of request headers, an attacker may be able to cause a segmentation fault, or to force ap_find_token() to return an incorrect value.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7668
