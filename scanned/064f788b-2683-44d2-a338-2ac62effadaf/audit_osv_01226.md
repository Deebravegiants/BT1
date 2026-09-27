# [H] ALPINE-CVE-2018-6798

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-6798
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6798
Type: osv

## Affected
- Alpine:v3.10: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.11: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.12: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.13: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.14: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.15: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.16: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.17: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.18: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.19: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.20: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.21: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.22: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.23: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.24: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.5: `perl` — affected >=5.22 <5.24.4-r0
- Alpine:v3.6: `perl` — affected >=5.22 <5.24.4-r0
- Alpine:v3.7: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.8: `perl` — affected >=5.22 <5.26.2-r0
- Alpine:v3.9: `perl` — affected >=5.22 <5.26.2-r0

## Details
An issue was discovered in Perl 5.22 through 5.26. Matching a crafted locale dependent regular expression can cause a heap-based buffer over-read and potentially information disclosure.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6798
