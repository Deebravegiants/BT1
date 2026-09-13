# [M] ALPINE-CVE-2018-11439

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-11439
Ecosystem: Alpine:v3.10, Alpine:v3.11
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-05-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-11439
Type: osv

## Affected
- Alpine:v3.10: `taglib` — affected >=0 <1.11.1-r2
- Alpine:v3.11: `taglib` — affected >=0 <1.11.1-r2

## Details
The TagLib::Ogg::FLAC::File::scan function in oggflacfile.cpp in TagLib 1.11.1 allows remote attackers to cause information disclosure (heap-based buffer over-read) via a crafted audio file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-11439
