# [C] SaltStack Salt Improper Validation of eauth credentials and tokens in salt-netapi

## Summary
Severity: Critical
Advisory: GHSA-29j3-2446-5j4w
CVE: CVE-2020-25592
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-29j3-2446-5j4w
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2015.8.13
- PyPI: `salt` — affected >=2016.3.0 <2016.3.8
- PyPI: `salt` — affected >=2016.11.0 <2016.11.10
- PyPI: `salt` — affected >=2017.5.0 <2017.7.8
- PyPI: `salt` — affected >=2018.2.0 <2018.3.5
- PyPI: `salt` — affected >=2019.2.0 <2019.2.7
- PyPI: `salt` — affected >=3000.0 <3000.5
- PyPI: `salt` — affected >=3001.0 <3001.3
- PyPI: `salt` — affected >=3002.0 <3002.1

## Details
In SaltStack the salt-netapi improperly validates eauth credentials and tokens. A user can bypass authentication and invoke Salt SSH.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25592
- https://docs.saltstack.com/en/latest/topics/releases/index.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2020-106.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/2019.2.7.rst#L12
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3000.5.rst#L12
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3001.3.rst#L12
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/3002.1.rst#L14
- https://lists.debian.org/debian-lts-announce/2020/12/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TPOGB2F6XUAIGFDTOCQDNB2VIXFXHWMA
- https://security.gentoo.org/glsa/202011-13
- https://www.debian.org/security/2021/dsa-4837
- https://www.saltstack.com/blog/on-november-3-2020-saltstack-publicly-disclosed-three-new-cves
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00029.html
- http://packetstormsecurity.com/files/160039/SaltStack-Salt-REST-API-Arbitrary-Command-Execution.html
