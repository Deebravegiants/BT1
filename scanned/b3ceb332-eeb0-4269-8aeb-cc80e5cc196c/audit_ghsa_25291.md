# [M] Plone has stored XSS in folder contents

## Summary
Severity: Medium
Advisory: GHSA-qfhw-fv3g-v836
CVE: CVE-2021-35959
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qfhw-fv3g-v836
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=5.0

## Details
In Plone 5.0 through 5.2.4, Editors are vulnerable to XSS in the folder contents view, if a Contributor has created a folder with a SCRIPT tag in the description field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-35959
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2021-110.yaml
- https://plone.org/security/hotfix/20210518/stored-xss-in-folder-contents
- http://www.openwall.com/lists/oss-security/2021/06/30/2
