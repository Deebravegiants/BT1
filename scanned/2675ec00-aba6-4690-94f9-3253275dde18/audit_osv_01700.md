# [H] ALPINE-CVE-2020-10543

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-10543
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2020-06-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-10543
Type: osv

## Affected
- Alpine:v3.10: `perl` — affected >=0 <5.28.3-r0
- Alpine:v3.11: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.12: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.13: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.14: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.15: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.16: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.17: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.18: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.19: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.20: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.21: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.22: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.23: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.24: `perl` — affected >=0 <5.30.3-r0
- Alpine:v3.9: `perl` — affected >=0 <5.26.3-r1

## Details
Perl before 5.30.3 on 32-bit platforms allows a heap-based buffer overflow because nested regular expression quantifiers have an integer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-10543
