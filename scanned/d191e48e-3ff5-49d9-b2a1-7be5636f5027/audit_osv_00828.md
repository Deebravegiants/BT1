# [M] ALPINE-CVE-2017-9608

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-9608
Ecosystem: Alpine:v3.6
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9608
Type: osv

## Affected
- Alpine:v3.6: `ffmpeg` — affected >=3.3 <3.2.6-r0

## Details
The dnxhd decoder in FFmpeg before 3.2.6, and 3.3.x before 3.3.3 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted mov file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9608
