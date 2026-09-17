# [H] Paramiko Authentication Bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-f2j6-wrhh-v25m
CVE: CVE-2018-1000805
CWE: CWE-732, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-f2j6-wrhh-v25m
Type: github-advisory

## Affected
- PyPI: `paramiko` — affected >=2.4.0 <2.4.2
- PyPI: `paramiko` — affected >=2.3.0 <2.3.3
- PyPI: `paramiko` — affected >=2.2.0 <2.2.4
- PyPI: `paramiko` — affected >=2.1.0 <2.1.6
- PyPI: `paramiko` — affected >=1.5.1 <2.0.9

## Details
Paramiko version 2.4.1, 2.3.2, 2.2.3, 2.1.5, 2.0.8, 1.18.5, 1.17.6 contains a Incorrect Access Control vulnerability in SSH server that can result in RCE. This attack appear to be exploitable via network connectivity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000805
- https://github.com/paramiko/paramiko/issues/1283
- https://access.redhat.com/errata/RHBA-2018:3497
- https://access.redhat.com/errata/RHSA-2018:3347
- https://access.redhat.com/errata/RHSA-2018:3406
- https://access.redhat.com/errata/RHSA-2018:3505
- https://github.com/advisories/GHSA-f2j6-wrhh-v25m
- https://github.com/paramiko/paramiko
- https://github.com/pypa/advisory-database/tree/main/vulns/paramiko/PYSEC-2018-69.yaml
- https://herolab.usd.de/wp-content/uploads/sites/4/usd20180023.txt
- https://lists.debian.org/debian-lts-announce/2018/10/msg00018.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00025.html
- https://usn.ubuntu.com/3796-1
- https://usn.ubuntu.com/3796-2
- https://usn.ubuntu.com/3796-3
