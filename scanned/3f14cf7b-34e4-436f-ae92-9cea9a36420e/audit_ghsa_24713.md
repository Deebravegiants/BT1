# [H] Plone denial of service via Caching Bypass

## Summary
Severity: High
Advisory: GHSA-97rj-p794-wq6m
CVE: CVE-2012-5498
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-97rj-p794-wq6m
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.2.3
- PyPI: `Plone` — affected >=4.3a0 <4.3b1

## Details
queryCatalog.py in Plone before 4.2.3 and 4.3 before beta 1 allows remote attackers to bypass caching and cause a denial of service via a crafted request to a collection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5498
- https://access.redhat.com/errata/RHSA-2014:1194
- https://access.redhat.com/security/cve/CVE-2012-5498
- https://bugzilla.redhat.com/show_bug.cgi?id=874665
- https://github.com/plone/Plone
- https://github.com/plone/Products.CMFPlone/blob/4.2.3/docs/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-40.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/14
- https://web.archive.org/web/20130528001715/https://plone.org/products/plone-hotfix/releases/20121106
- https://web.archive.org/web/20131103191705/https://plone.org/products/plone/security/advisories/20121106/14
- http://rhn.redhat.com/errata/RHSA-2014-1194.html
- http://www.openwall.com/lists/oss-security/2012/11/09/7
- http://www.openwall.com/lists/oss-security/2012/11/10/1
