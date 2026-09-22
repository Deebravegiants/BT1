# [H] ALPINE-CVE-2026-44171

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-44171
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44171
Type: osv

## Affected
- Alpine:v3.20: `mariadb` — affected >=10.6.1 <10.11.17-r0
- Alpine:v3.21: `mariadb` — affected >=10.6.1 <11.4.11-r0
- Alpine:v3.22: `mariadb` — affected >=10.6.1 <11.4.11-r0
- Alpine:v3.23: `mariadb` — affected >=10.6.1 <11.4.11-r0
- Alpine:v3.24: `mariadb` — affected >=10.6.1 <11.8.7-r0

## Details
MariaDB server is a community developed fork of MySQL server. From versions 10.6.1 to before 10.6.26, 10.11.1 to before 10.11.17, 11.4.1 to before 11.4.11, 11.8.1 to before 11.8.7, and 12.3.1, mbstream did not check for /../ in the path when unpacking the archive. A proper backup can never contain such paths, but a specially crafted archive could have caused mbstream to create files outside of the target-dir path. This issue has been patched in versions 10.6.26, 10.11.17, 11.4.11, 11.8.7, and 12.3.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44171
