# [H] Plone denial of service via RSS Feed Request

## Summary
Severity: High
Advisory: GHSA-79hj-474h-v4xv
CVE: CVE-2012-5506
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-79hj-474h-v4xv
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a1 <4.3b1

## Details
python_scripts.py in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to cause a denial of service (infinite loop) via an RSS feed request for a folder the user does not have permission to access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5506
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-48.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/22
- http://www.openwall.com/lists/oss-security/2012/11/10/1
