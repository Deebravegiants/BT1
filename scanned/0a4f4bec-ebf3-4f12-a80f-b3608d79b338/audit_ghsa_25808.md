# [H] SaltStack Improper Verification of Cryptographic Signature

## Summary
Severity: High
Advisory: GHSA-2q4g-wfm6-5fpm
CVE: CVE-2022-22934
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-2q4g-wfm6-5fpm
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3002.8
- PyPI: `salt` — affected >=3004 <3004.1
- PyPI: `salt` — affected >=3003 <3003.4

## Details
An issue was discovered in SaltStack Salt in versions before 3002.8, 3003.4, 3004.1. Salt Masters do not sign pillar data with the minion’s public key, which can result in attackers substituting arbitrary pillar data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22934
- https://blog.cloudflare.com/future-proofing-saltstack
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2022-171.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/releases
- https://github.com/saltstack/salt/releases,
- https://repo.saltproject.io
- https://saltproject.io/security_announcements/salt-security-advisory-release/,
- https://security.gentoo.org/glsa/202310-22
