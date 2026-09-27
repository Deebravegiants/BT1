# [M] ALPINE-CVE-2019-17402

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-17402
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17402
Type: osv

## Affected
- Alpine:v3.10: `exiv2` — affected >=0 <0.26-r1
- Alpine:v3.11: `exiv2` — affected >=0 <0.27.2-r2
- Alpine:v3.8: `exiv2` — affected >=0 <0.26-r1
- Alpine:v3.9: `exiv2` — affected >=0 <0.26-r1

## Details
Exiv2 0.27.2 allows attackers to trigger a crash in Exiv2::getULong in types.cpp when called from Exiv2::Internal::CiffDirectory::readDirectory in crwimage_int.cpp, because there is no validation of the relationship of the total size to the offset and size.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17402
