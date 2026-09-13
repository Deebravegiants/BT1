# [M] Plone is vulnerable to information exposure via the object manager implementation 

## Summary
Severity: Medium
Advisory: GHSA-qphh-5fv5-2mjj
CVE: CVE-2013-4196
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qphh-5fv5-2mjj
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.1 <4.1.1
- PyPI: `Plone` — affected >=4.2 <4.2.6
- PyPI: `Plone` — affected >=4.3 <4.3.2

## Details
The object manager implementation (objectmanager.py) in Plone 2.1 through 4.1, 4.2.x through 4.2.5, and 4.3.x through 4.3.1 does not properly restrict access to internal methods, which allows remote attackers to obtain sensitive information via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4196
- https://bugzilla.redhat.com/show_bug.cgi?id=978475
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-60.yaml
- http://plone.org/products/plone-hotfix/releases/20130618
- http://plone.org/products/plone/security/advisories/20130618-announcement
- http://seclists.org/oss-sec/2013/q3/261
