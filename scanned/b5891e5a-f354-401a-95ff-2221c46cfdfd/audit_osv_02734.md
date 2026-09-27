# [M] ALPINE-CVE-2022-47015

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-47015
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-47015
Type: osv

## Affected
- Alpine:v3.15: `mariadb` — affected >=10.3.0 <10.6.13-r0
- Alpine:v3.16: `mariadb` — affected >=10.3.0 <10.6.13-r0
- Alpine:v3.17: `mariadb` — affected >=10.3.0 <10.6.13-r0

## Details
MariaDB Server before 10.3.34 thru 10.9.3 is vulnerable to Denial of Service. It is possible for function spider_db_mbase::print_warnings to dereference a null pointer.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-47015
