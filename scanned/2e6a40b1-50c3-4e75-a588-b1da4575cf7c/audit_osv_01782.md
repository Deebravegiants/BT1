# [H] ALPINE-CVE-2020-14393

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14393
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14393
Type: osv

## Affected
- Alpine:v3.12: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.13: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.14: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.15: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.16: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.17: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.18: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.19: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.20: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.21: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.22: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.23: `perl-dbi` — affected >=0 <1.643-r0
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.643-r0

## Details
A buffer overflow was found in perl-DBI < 1.643 in DBI.xs. A local attacker who is able to supply a string longer than 300 characters could cause an out-of-bounds write, affecting the availability of the service or integrity of data.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14393
