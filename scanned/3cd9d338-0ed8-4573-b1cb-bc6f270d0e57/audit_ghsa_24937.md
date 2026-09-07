# [M] Plone is vulnerable to File System Path Exposure

## Summary
Severity: Medium
Advisory: GHSA-mm32-jw73-9227
CVE: CVE-2013-4194
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-mm32-jw73-9227
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.1 <4.1.1
- PyPI: `Plone` — affected >=4.2 <4.2.6
- PyPI: `Plone` — affected >=4.3 <4.3.2

## Details
The WYSIWYG component (wysiwyg.py) in Plone 2.1 through 4.1, 4.2.x through 4.2.5, and 4.3.x through 4.3.1 allows remote attackers to obtain sensitive information via a crafted URL, which reveals the installation path in an error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4194
- https://bugzilla.redhat.com/show_bug.cgi?id=978470
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-58.yaml
- http://plone.org/products/plone-hotfix/releases/20130618
- http://plone.org/products/plone/security/advisories/20130618-announcement
- http://seclists.org/oss-sec/2013/q3/261
