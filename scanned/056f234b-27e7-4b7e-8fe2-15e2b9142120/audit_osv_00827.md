# [M] ALPINE-CVE-2017-9545

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-9545
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9545
Type: osv

## Affected
- Alpine:v3.3: `mpg123` — affected >=0 <1.25.4-r0
- Alpine:v3.4: `mpg123` — affected >=0 <1.25.4-r0
- Alpine:v3.5: `mpg123` — affected >=0 <1.25.4-r0
- Alpine:v3.6: `mpg123` — affected >=0 <1.25.4-r0

## Details
The next_text function in src/libmpg123/id3.c in mpg123 1.24.0 allows remote attackers to cause a denial of service (buffer over-read) via a crafted mp3 file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9545
