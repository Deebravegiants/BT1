# [M] ALPINE-CVE-2022-31623

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-31623
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-31623
Type: osv

## Affected
- Alpine:v3.16: `mariadb` — affected >=10.3.0 <10.6.7-r0
- Alpine:v3.17: `mariadb` — affected >=10.3.0 <10.6.7-r0
- Alpine:v3.18: `mariadb` — affected >=10.3.0 <10.6.7-r0
- Alpine:v3.19: `mariadb` — affected >=10.3.0 <10.6.7-r0
- Alpine:v3.20: `mariadb` — affected >=10.3.0 <10.6.7-r0
- Alpine:v3.21: `mariadb` — affected >=10.3.0 <10.6.7-r0
- Alpine:v3.22: `mariadb` — affected >=10.3.0 <10.6.7-r0
- Alpine:v3.23: `mariadb` — affected >=10.3.0 <10.6.7-r0
- Alpine:v3.24: `mariadb` — affected >=10.3.0 <10.6.7-r0

## Details
MariaDB Server before 10.7 is vulnerable to Denial of Service. In extra/mariabackup/ds_compress.cc, when an error occurs (i.e., going to the err label) while executing the method create_worker_threads, the held lock thd->ctrl_mutex is not released correctly, which allows local users to trigger a denial of service due to the deadlock. Note: The vendor argues this is just an improper locking bug and not a vulnerability with adverse effects.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-31623
