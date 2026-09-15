# [M] Chameleon in Plone allows Authentication Bypass

## Summary
Severity: Medium
Advisory: GHSA-6h8x-73fx-q2h9
CVE: CVE-2016-4043
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6h8x-73fx-q2h9
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=5.0rc1
- PyPI: `Plone` — affected 5.1a1

## Details
Chameleon (five.pt) in Plone 5.0rc1 through 5.1a1 allows remote authenticated users to bypass Restricted Python by leveraging permissions to create or edit templates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4043
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2017-57.yaml
- https://plone.org/security/hotfix/20160419/bypass-restricted-python
- http://www.openwall.com/lists/oss-security/2016/04/20/3
