# [M] ALPINE-CVE-2014-10402

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2014-10402
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2014-10402
Type: osv

## Affected
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
An issue was discovered in the DBI module through 1.643 for Perl. DBD::File drivers can open files from folders other than those specifically passed via the f_dir attribute in the data source name (DSN). NOTE: this issue exists because of an incomplete fix for CVE-2014-10401.

## References
- https://security.alpinelinux.org/vuln/CVE-2014-10402
