# [C] SaltStack Salt Command Injection in netapi ssh client

## Summary
Severity: Critical
Advisory: GHSA-qr38-h96j-2j3w
CVE: CVE-2020-16846
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qr38-h96j-2j3w
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2015.8.13
- PyPI: `salt` — affected >=2016.3.0 <2016.3.8
- PyPI: `salt` — affected >=2016.11.0 <2016.11.10
- PyPI: `salt` — affected >=2017.5.0 <2017.7.8
- PyPI: `salt` — affected >=2018.2.0 <2018.3.5
- PyPI: `salt` — affected >=2019.2.0 <2019.2.6
- PyPI: `salt` — affected >=3000.0 <3000.4
- PyPI: `salt` — affected >=3001 <3001.2
- PyPI: `salt` — affected >=3002 <3002.1

## Details
An issue was discovered in SaltStack Salt through 3002. Sending crafted web requests to the Salt API, with the SSH client enabled, can result in shell injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-16846
- https://www.zerodayinitiative.com/advisories/ZDI-20-1383
- https://www.zerodayinitiative.com/advisories/ZDI-20-1382
- https://www.zerodayinitiative.com/advisories/ZDI-20-1381
- https://www.zerodayinitiative.com/advisories/ZDI-20-1380
- https://www.zerodayinitiative.com/advisories/ZDI-20-1379
- https://www.saltstack.com/blog/on-november-3-2020-saltstack-publicly-disclosed-three-new-cves
- https://www.debian.org/security/2021/dsa-4837
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-16846
- https://security.gentoo.org/glsa/202011-13
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TPOGB2F6XUAIGFDTOCQDNB2VIXFXHWMA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TPOGB2F6XUAIGFDTOCQDNB2VIXFXHWMA
- https://lists.debian.org/debian-lts-announce/2022/01/msg00000.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00007.html
- https://github.com/saltstack/salt/releases
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3002.1.rst#L12
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3001.2.rst#L10
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3000.4.rst#L10
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/2019.2.6.rst#L10
- https://github.com/saltstack/salt
