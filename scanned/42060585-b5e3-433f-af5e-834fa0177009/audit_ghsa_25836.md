# [H] SaltStack Salt Authentication Bypass by Capture-replay

## Summary
Severity: High
Advisory: GHSA-5r3f-3m3j-wcj2
CVE: CVE-2022-22936
CWE: CWE-294
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-5r3f-3m3j-wcj2
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3002.8
- PyPI: `salt` — affected >=3003 <3003.4
- PyPI: `salt` — affected >=3004 <3004.1

## Details
An issue was discovered in SaltStack Salt in versions before 3002.8, 3003.4, 3004.1. Job publishes and file server replies are susceptible to replay attacks, which can result in an attacker replaying job publishes causing minions to run old jobs. File server replies can also be re-played. A sufficient craft attacker could gain root access on minion under certain scenarios.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22936
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2022-173.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3002.8.rst#L31
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3003.4.rst#L32
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3004.1.rst#L30
- https://github.com/saltstack/salt/releases
- https://repo.saltproject.io
- https://saltproject.io/security_announcements/salt-security-advisory-release
- https://security.gentoo.org/glsa/202310-22
