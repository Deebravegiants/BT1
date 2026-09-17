# [H] Pillow is vulnerable to Denial of Service (DOS) in the Jpeg2KImagePlugin

## Summary
Severity: High
Advisory: GHSA-j6f7-g425-4gmx
CVE: CVE-2014-3598
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j6f7-g425-4gmx
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <2.5.3

## Details
The Jpeg2KImagePlugin plugin in Pillow before 2.5.3 allows remote attackers to cause a denial of service via a crafted image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3598
- https://github.com/python-pillow/Pillow/commit/347a1d8d956f9e64af4463ee25311b60cdd5657d
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2015-15.yaml
- https://github.com/python-pillow/Pillow
- https://pypi.python.org/pypi/Pillow/2.5.3
- http://lists.opensuse.org/opensuse-updates/2015-04/msg00056.html
