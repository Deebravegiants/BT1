# [H] ALPINE-CVE-2019-12447

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12447
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2019-05-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12447
Type: osv

## Affected
- Alpine:v3.7: `gvfs` — affected >=1.29.4 <1.34.1-r1
- Alpine:v3.8: `gvfs` — affected >=1.29.4 <1.36.1-r1

## Details
An issue was discovered in GNOME gvfs 1.29.4 through 1.41.2. daemon/gvfsbackendadmin.c mishandles file ownership because setfsuid is not used.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12447
