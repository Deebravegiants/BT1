# [H] ALPINE-CVE-2019-12448

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12448
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12448
Type: osv

## Affected
- Alpine:v3.7: `gvfs` — affected >=1.29.4 <1.34.1-r1
- Alpine:v3.8: `gvfs` — affected >=1.29.4 <1.36.1-r1

## Details
An issue was discovered in GNOME gvfs 1.29.4 through 1.41.2. daemon/gvfsbackendadmin.c has race conditions because the admin backend doesn't implement query_info_on_read/write.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12448
