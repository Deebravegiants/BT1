# [H] CVE-2020-18771

## Summary
Severity: High
Advisory: CVE-2020-18771
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2020-18771
Type: osv

## Details
Exiv2 0.27.99.0 has a global buffer over-read in Exiv2::Internal::Nikon1MakerNote::print0x0088 in nikonmn_int.cpp which can result in an information leak.

## References
- https://cwe.mitre.org/data/definitions/126.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://security.gentoo.org/glsa/202312-06
- https://github.com/Exiv2/exiv2/issues/756
