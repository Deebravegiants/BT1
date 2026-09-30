# [M] ALPINE-CVE-2016-3977

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-3977
Ecosystem: Alpine:v3.4
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-04-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3977
Type: osv

## Affected
- Alpine:v3.4: `giflib` — affected >=0 <5.1.4-r0

## Details
Heap-based buffer overflow in util/gif2rgb.c in gif2rgb in giflib 5.1.2 allows remote attackers to cause a denial of service (application crash) via the background color index in a GIF file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3977
