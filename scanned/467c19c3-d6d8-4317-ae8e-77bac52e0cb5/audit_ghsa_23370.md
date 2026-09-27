# [C] SaltStack Salt eauth tokens can be used once after expiration

## Summary
Severity: Critical
Advisory: GHSA-w2hr-3mc8-46gh
CVE: CVE-2021-3144
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w2hr-3mc8-46gh
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2015.8.13
- PyPI: `salt` — affected >=2016.3.0 <2016.11.5
- PyPI: `salt` — affected >=2016.11.7 <2016.11.10
- PyPI: `salt` — affected >=2017.5.0 <2017.7.8
- PyPI: `salt` — affected >=2018.2.0
- PyPI: `salt` — affected >=3000 <3000.7
- PyPI: `salt` — affected >=3001 <3001.5
- PyPI: `salt` — affected >=3002 <3002.3
- PyPI: `salt` — affected >=2019.2.0 <2019.2.8

## Details
In SaltStack Salt before 3002.5, eauth tokens can be used once after expiration. (They might be used to run command against the salt master or minions.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3144
- https://www.debian.org/security/2021/dsa-5011
- https://security.gentoo.org/glsa/202310-22
- https://security.gentoo.org/glsa/202103-01
- https://saltproject.io/security_announcements/active-saltstack-cve-release-2021-feb-25
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YOGNT2XWPOYV7YT75DN7PS4GIYWFKOK5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FUGLOJ6NXLCIFRD2JTXBYQEMAEF2B6XH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7GRVZ5WAEI3XFN2BDTL6DDXFS5HYSDVB
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YOGNT2XWPOYV7YT75DN7PS4GIYWFKOK5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FUGLOJ6NXLCIFRD2JTXBYQEMAEF2B6XH
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7GRVZ5WAEI3XFN2BDTL6DDXFS5HYSDVB
- https://lists.debian.org/debian-lts-announce/2021/11/msg00009.html
- https://github.com/saltstack/salt/releases
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3002.3.rst#L26
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3001.5.rst#L26
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3000.7.rst#L26
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/CHANGELOG.md?plain=1#L2373
- https://github.com/saltstack/salt
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2021-54.yaml
