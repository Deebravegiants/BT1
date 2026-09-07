# [C] Plone python code injection

## Summary
Severity: Critical
Advisory: GHSA-w6pw-5gh5-4952
CVE: CVE-2012-5495
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w6pw-5gh5-4952
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a1 <4.3b1

## Details
python_scripts.py in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to execute Python code via a crafted URL, related to "go_back."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5495
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-37.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/11
- http://www.openwall.com/lists/oss-security/2012/11/10/1
