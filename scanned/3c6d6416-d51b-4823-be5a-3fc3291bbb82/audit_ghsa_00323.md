# [H] Pillow buffer overflow in ImagingPcdDecode

## Summary
Severity: High
Advisory: GHSA-3c5c-7235-994j
CVE: CVE-2016-2533
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-3c5c-7235-994j
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <3.1.1

## Details
Buffer overflow in the `ImagingPcdDecode` function in `PcdDecode.c` in Pillow before 3.1.1 and Python Imaging Library (PIL) 1.1.7 and earlier allows remote attackers to cause a denial of service (crash) via a crafted PhotoCD file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2533
- https://github.com/python-pillow/Pillow/pull/1706
- https://github.com/python-pillow/Pillow/commit/5bdf54b5a76b54fb00bd05f2d733e0a4173eefc9#diff-8ff6909c159597e22288ad818938fd6b
- https://github.com/python-pillow/Pillow/commit/ae453aa18b66af54e7ff716f4ccb33adca60afd4#diff-8ff6909c159597e22288ad818938fd6b
- https://github.com/advisories/GHSA-3c5c-7235-994j
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2016-19.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/c3cb690fed5d4bf0c45576759de55d054916c165/CHANGES.rst
- https://github.com/python-pillow/Pillow/blob/c3cb690fed5d4bf0c45576759de55d054916c165/CHANGES.rst?plain=1#L53
- https://security.gentoo.org/glsa/201612-52
- http://www.debian.org/security/2016/dsa-3499
- http://www.openwall.com/lists/oss-security/2016/02/02/5
- http://www.openwall.com/lists/oss-security/2016/02/22/2
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
