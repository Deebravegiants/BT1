# [H] Pillow denial of service via Crafted Block Size

## Summary
Severity: High
Advisory: GHSA-cfmr-38g9-f2h7
CVE: CVE-2014-3589
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cfmr-38g9-f2h7
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <2.3.2
- PyPI: `pillow` — affected >=2.5 <2.5.2

## Details
`PIL/IcnsImagePlugin.py` in Python Imaging Library (PIL) and Pillow before 2.3.2 and 2.5.x before 2.5.2 allows remote attackers to cause a denial of service via a crafted block size.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3589
- https://github.com/python-pillow/Pillow/commit/205e056f8f9b06ed7b925cf8aa0874bc4aaf8a7d
- https://github.com/python-pillow/Pillow/commit/5efeed77666bfd17708f3434b1d2daa9db1e1335
- https://github.com/python-pillow/Pillow/commit/d47611e6fbb808ea109366781dd76559ffb80bcd
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2014-10.yaml
- https://github.com/python-pillow/Pillow
- https://pypi.python.org/pypi/Pillow/2.3.2
- https://pypi.python.org/pypi/Pillow/2.5.2
- http://lists.opensuse.org/opensuse-updates/2015-04/msg00056.html
- http://www.debian.org/security/2014/dsa-3009
