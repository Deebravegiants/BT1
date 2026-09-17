# [H] SaltStack Salt command injection via a crafted process name

## Summary
Severity: High
Advisory: GHSA-phhw-3wc9-8q75
CVE: CVE-2020-28243
CWE: CWE-77, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-phhw-3wc9-8q75
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2015.8.13
- PyPI: `salt` — affected >=2016.3.0 <2016.11.5
- PyPI: `salt` — affected >=2016.11.7 <2016.11.10
- PyPI: `salt` — affected >=2017.5.0 <2017.7.8
- PyPI: `salt` — affected >=2018.2.0
- PyPI: `salt` — affected >=2019.2.0 <2019.2.8
- PyPI: `salt` — affected >=3000 <3000.7
- PyPI: `salt` — affected >=3001 <3001.5
- PyPI: `salt` — affected >=3002 <3002.3

## Details
An issue was discovered in SaltStack Salt before 3002.5. The minion's `restartcheck` is vulnerable to command injection via a crafted process name. This allows for a local privilege escalation by any user able to create a files on the minion in a non-blacklisted directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28243
- https://www.debian.org/security/2021/dsa-5011
- https://security.gentoo.org/glsa/202310-22
- https://security.gentoo.org/glsa/202103-01
- https://sec.stealthcopter.com/cve-2020-28243
- https://saltproject.io/security_announcements/active-saltstack-cve-release-2021-feb-25
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YOGNT2XWPOYV7YT75DN7PS4GIYWFKOK5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FUGLOJ6NXLCIFRD2JTXBYQEMAEF2B6XH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7GRVZ5WAEI3XFN2BDTL6DDXFS5HYSDVB
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YOGNT2XWPOYV7YT75DN7PS4GIYWFKOK5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FUGLOJ6NXLCIFRD2JTXBYQEMAEF2B6XH
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7GRVZ5WAEI3XFN2BDTL6DDXFS5HYSDVB
- https://lists.debian.org/debian-lts-announce/2022/01/msg00000.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00009.html
- https://github.com/stealthcopter/CVE-2020-28243
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3002.3.rst#L12
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3001.5.rst#L12
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3000.7.rst#L12
- https://github.com/saltstack/salt
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2021-73.yaml
