# [M] ALPINE-CVE-2016-9888

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-9888
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9888
Type: osv

## Affected
- Alpine:v3.10: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.11: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.2: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.3: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.4: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.5: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.6: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.7: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.8: `libgsf` — affected >=0 <1.14.41-r0
- Alpine:v3.9: `libgsf` — affected >=0 <1.14.41-r0

## Details
An error within the "tar_directory_for_file()" function (gsf-infile-tar.c) in GNOME Structured File Library before 1.14.41 can be exploited to trigger a Null pointer dereference and subsequently cause a crash via a crafted TAR file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9888
