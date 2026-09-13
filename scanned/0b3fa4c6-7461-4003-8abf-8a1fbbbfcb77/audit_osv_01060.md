# [C] ALPINE-CVE-2018-18311

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-18311
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18311
Type: osv

## Affected
- Alpine:v3.10: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.11: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.12: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.13: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.14: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.15: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.16: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.17: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.18: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.19: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.20: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.21: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.22: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.23: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.24: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.6: `perl` — affected >=5.28.0 <5.24.4-r2
- Alpine:v3.7: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.8: `perl` — affected >=5.28.0 <5.26.3-r0
- Alpine:v3.9: `perl` — affected >=5.28.0 <5.26.3-r0

## Details
Perl before 5.26.3 and 5.28.x before 5.28.1 has a buffer overflow via a crafted regular expression that triggers invalid write operations.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18311
