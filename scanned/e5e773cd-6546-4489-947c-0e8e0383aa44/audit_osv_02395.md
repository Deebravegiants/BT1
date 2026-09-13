# [C] ALPINE-CVE-2022-1664

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-1664
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1664
Type: osv

## Affected
- Alpine:v3.13: `dpkg` — affected >=1.14.17 <1.20.10-r0
- Alpine:v3.14: `dpkg` — affected >=1.14.17 <1.20.10-r0
- Alpine:v3.15: `dpkg` — affected >=1.14.17 <1.20.10-r0
- Alpine:v3.16: `dpkg` — affected >=1.14.17 <1.21.8-r0
- Alpine:v3.17: `dpkg` — affected >=1.14.17 <1.21.8-r0
- Alpine:v3.18: `dpkg` — affected >=1.14.17 <1.21.8-r0
- Alpine:v3.19: `dpkg` — affected >=1.14.17 <1.21.8-r0
- Alpine:v3.20: `dpkg` — affected >=1.14.17 <1.21.8-r0
- Alpine:v3.21: `dpkg` — affected >=1.14.17 <1.21.8-r0
- Alpine:v3.22: `dpkg` — affected >=1.14.17 <1.21.8-r0
- Alpine:v3.23: `dpkg` — affected >=1.14.17 <1.21.8-r0
- Alpine:v3.24: `dpkg` — affected >=1.14.17 <1.21.8-r0

## Details
Dpkg::Source::Archive in dpkg, the Debian package management system, before version 1.21.8, 1.20.10, 1.19.8, 1.18.26 is prone to a directory traversal vulnerability. When extracting untrusted source packages in v2 and v3 source package formats that include a debian.tar, the in-place extraction can lead to directory traversal situations on specially crafted orig.tar and debian.tar tarballs.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1664
