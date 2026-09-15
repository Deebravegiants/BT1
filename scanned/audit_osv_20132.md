# [H] CVE-2021-31292

## Summary
Severity: High
Advisory: CVE-2021-31292
Aliases: PYSEC-2021-877
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-26
Source: https://osv.dev/vulnerability/CVE-2021-31292
Type: osv

## Details
An integer overflow in CrwMap::encode0x1810 of Exiv2 0.27.3 allows attackers to trigger a heap-based buffer overflow and cause a denial of service (DOS) via crafted metadata.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FMDT4PJB7P43WSOM3TRQIY3J33BAFVVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UYGDELIFFJWKUU7SO3QATCIXCZJERGAC/
- https://lists.debian.org/debian-lts-announce/2021/08/msg00028.html
- https://security.gentoo.org/glsa/202312-06
- https://www.debian.org/security/2021/dsa-4958
- https://github.com/Exiv2/exiv2/issues/1530
