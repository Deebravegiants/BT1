# [M] Pillow Integer overflow in Map.c

## Summary
Severity: Medium
Advisory: GHSA-rwr3-c2q8-gm56
CVE: CVE-2016-9189
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-rwr3-c2q8-gm56
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <3.3.2

## Details
Pillow before 3.3.2 allows context-dependent attackers to obtain sensitive information by using the "crafted image file" approach, related to an "Integer Overflow" issue affecting the `Image.core.map_buffer` in `map.c` component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9189
- https://github.com/python-pillow/Pillow/issues/2105
- https://github.com/python-pillow/Pillow/pull/2146/commits/c50ebe6459a131a1ea8ca531f10da616d3ceaa0f
- https://github.com/advisories/GHSA-rwr3-c2q8-gm56
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2016-8.yaml
- https://github.com/python-pillow/Pillow
- https://security.gentoo.org/glsa/201612-52
- http://pillow.readthedocs.io/en/3.4.x/releasenotes/3.3.2.html
- http://www.debian.org/security/2016/dsa-3710
- http://www.securityfocus.com/bid/94234
