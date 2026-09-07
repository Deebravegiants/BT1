# [H] Plone allows weak passwords

## Summary
Severity: High
Advisory: GHSA-cw58-gpgw-hwx2
CVE: CVE-2020-7940
CWE: CWE-521
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cw58-gpgw-hwx2
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=4.3 <4.3.20
- PyPI: `Plone` — affected >=5.0rc1 <5.1.7
- PyPI: `Plone` — affected >=5.2.0 <5.2.2

## Details
Missing password strength checks on some forms in Plone 4.3 through 5.2.0 allow users to set weak passwords, leading to easier cracking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7940
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2020-89.yaml
- https://plone.org/security/hotfix/20200121
- https://plone.org/security/hotfix/20200121/password-strength-checks-were-not-always-checked
- https://www.openwall.com/lists/oss-security/2020/01/22/1
- http://www.openwall.com/lists/oss-security/2020/01/24/1
