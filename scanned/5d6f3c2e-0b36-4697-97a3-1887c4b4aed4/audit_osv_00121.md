# [C] ALPINE-CVE-2016-5118

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-5118
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5118
Type: osv

## Affected
- Alpine:v3.2: `imagemagick` — affected >=0 <6.9.6.8-r0
- Alpine:v3.3: `imagemagick` — affected >=0 <6.9.6.8-r0

## Details
The OpenBlob function in blob.c in GraphicsMagick before 1.3.24 and ImageMagick allows remote attackers to execute arbitrary code via a | (pipe) character at the start of a filename.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5118
