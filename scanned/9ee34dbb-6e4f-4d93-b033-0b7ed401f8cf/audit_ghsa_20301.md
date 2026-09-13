# [H] Salt's PAM auth fails to reject locked accounts

## Summary
Severity: High
Advisory: GHSA-fpxm-fprw-6hxj
CVE: CVE-2022-22967
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-25
Source: https://github.com/advisories/GHSA-fpxm-fprw-6hxj
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3002.9
- PyPI: `salt` — affected >=3003.0 <3003.5
- PyPI: `salt` — affected >=3004.0 <3004.2

## Details
An issue was discovered in SaltStack Salt in versions before 3002.9, 3003.5, 3004.2. PAM auth fails to reject locked accounts, which allows a previously authorized user whose account is locked still run Salt commands when their account is locked. This affects both local shell accounts with an active session and salt-api users that authenticate via PAM eauth.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22967
- https://github.com/advisories/GHSA-fpxm-fprw-6hxj
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2022-210.yaml
- https://github.com/saltstack/salt
- https://repo.saltproject.io
- https://saltproject.io/security_announcements/salt-security-advisory-release-june-21st-2022/,
- https://security.gentoo.org/glsa/202310-22
