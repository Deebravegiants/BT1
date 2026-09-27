# [H] Plone is vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-wrf2-2rch-cmr9
CVE: CVE-2012-5499
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wrf2-2rch-cmr9
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=4.0 <4.2.3
- PyPI: `Plone` — affected >=4.3a1 <4.3b1

## Details
python_scripts.py in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to cause a denial of service (memory consumption) via a large value, related to `formatColumns`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5499
- https://access.redhat.com/errata/RHSA-2014:1194
- https://access.redhat.com/security/cve/CVE-2012-5499
- https://bugzilla.redhat.com/show_bug.cgi?id=874657
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-41.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/15
- http://rhn.redhat.com/errata/RHSA-2014-1194.html
- http://www.openwall.com/lists/oss-security/2012/11/10/1
