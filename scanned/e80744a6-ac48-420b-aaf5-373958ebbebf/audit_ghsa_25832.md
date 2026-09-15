# [H] SaltStack Salt Permissions Bypass

## Summary
Severity: High
Advisory: GHSA-qcr3-hr2f-6557
CVE: CVE-2022-22941
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-qcr3-hr2f-6557
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3002.8
- PyPI: `salt` — affected >=3003 <3003.4
- PyPI: `salt` — affected >=3004 <3004.1

## Details
An issue was discovered in SaltStack Salt in versions before 3002.8, 3003.4, 3004.1. When configured as a Master-of-Masters, with a publisher_acl, if a user configured in the publisher_acl targets any minion connected to the Syndic, the Salt Master incorrectly interpreted no valid targets as valid, allowing configured users to target any of the minions connected to the syndic with their configured commands. This requires a syndic master combined with publisher_acl configured on the Master-of-Masters, allowing users specified in the publisher_acl to bypass permissions, publishing authorized commands to any configured minion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22941
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2022-174.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3002.8.rst#L31
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3003.4.rst#L32
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3004.1.rst#L30
- https://repo.saltproject.io
- https://security.gentoo.org/glsa/202310-22
