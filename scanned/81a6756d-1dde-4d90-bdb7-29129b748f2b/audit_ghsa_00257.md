# [H] Arbitrary code using "crafted image file" approach affecting Pillow

## Summary
Severity: High
Advisory: GHSA-w4vg-rf63-f3j3
CVE: CVE-2016-9190
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-w4vg-rf63-f3j3
Type: github-advisory

## Affected
- PyPI: `Pillow` — affected >=0 <3.3.2

## Details
Pillow before 3.3.2 allows context-dependent attackers to execute arbitrary code by using the "crafted image file" approach, related to an "Insecure Sign Extension" issue affecting the ImagingNew in Storage.c component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9190
- https://github.com/python-pillow/Pillow/issues/2105
- https://github.com/python-pillow/Pillow/pull/2146/commits/5d8a0be45aad78c5a22c8d099118ee26ef8144af
- https://github.com/advisories/GHSA-w4vg-rf63-f3j3
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2016-9.yaml
- https://github.com/python-pillow/Pillow
- https://security.gentoo.org/glsa/201612-52
- http://pillow.readthedocs.io/en/3.4.x/releasenotes/3.3.2.html
- http://www.debian.org/security/2016/dsa-3710
- http://www.securityfocus.com/bid/94234
