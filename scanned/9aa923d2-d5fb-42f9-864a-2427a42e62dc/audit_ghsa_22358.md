# [H] Plone DoS via Crafted URL

## Summary
Severity: High
Advisory: GHSA-gx6w-hcw3-5r37
CVE: CVE-2012-5496
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gx6w-hcw3-5r37
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.0

## Details
kupu_spellcheck.py in Kupu in Plone before 4.0 allows remote attackers to cause a denial of service (ZServer thread lock) via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5496
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-38.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/12
- http://www.openwall.com/lists/oss-security/2012/11/10/1
