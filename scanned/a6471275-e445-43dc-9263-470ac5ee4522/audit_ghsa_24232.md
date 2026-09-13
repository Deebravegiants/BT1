# [C] SaltStack Salt Remote command execution and incorrect access control when using salt-api

## Summary
Severity: Critical
Advisory: GHSA-x549-r7m8-gv63
CVE: CVE-2018-15751
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x549-r7m8-gv63
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=2017.7.0 <2017.7.8
- PyPI: `salt` — affected >=2018.3.0 <2018.3.3
- PyPI: `salt` — affected >=2016.11.0 <2016.11.10

## Details
SaltStack Salt 2016.11.x before 2016.11.10, 2017.7.x before 2017.7.8 and 2018.3.x before 2018.3.3 allow remote attackers to bypass authentication and execute arbitrary commands via salt-api(netapi).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15751
- https://docs.saltstack.com/en/2017.7/topics/releases/2017.7.8.html
- https://docs.saltstack.com/en/latest/topics/releases/2018.3.3.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2018-30.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/2016.11.10.rst#L13
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/2017.7.8.rst#L26
- https://github.com/saltstack/salt/blob/8f9405cf8e6f7d7776d5000841c886dec6d96250/doc/topics/releases/2018.3.3.rst#L56
- https://groups.google.com/d/msg/salt-users/L9xqcJ0UXxs/qgDj42obBQAJ
- https://groups.google.com/d/msg/salt-users/dimVF7rpphY/jn3Xv3MbBQAJ
- https://lists.debian.org/debian-lts-announce/2020/07/msg00024.html
- https://usn.ubuntu.com/4459-1
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00070.html
