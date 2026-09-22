# [M] Plone is vulnerable to Information Exposure when generating zip archives

## Summary
Severity: Medium
Advisory: GHSA-grwx-4p5v-9g2g
CVE: CVE-2013-4191
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-grwx-4p5v-9g2g
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.1 <4.1.1
- PyPI: `Plone` — affected >=4.2 <4.2.6
- PyPI: `Plone` — affected >=4.3 <4.3.2

## Details
zip.py in Plone 2.1 through 4.1, 4.2.x through 4.2.5, and 4.3.x through 4.3.1 does not properly enforce access restrictions when including content in a zip archive, which allows remote attackers to obtain sensitive information by reading a generated archive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4191
- https://bugzilla.redhat.com/show_bug.cgi?id=978453
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-55.yaml
- http://plone.org/products/plone-hotfix/releases/20130618
- http://plone.org/products/plone/security/advisories/20130618-announcement
- http://seclists.org/oss-sec/2013/q3/261
