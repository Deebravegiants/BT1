# [C] Paramiko not properly checking authentication before processing other requests

## Summary
Severity: Critical
Advisory: GHSA-232r-66cg-79px
CVE: CVE-2018-7750
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-232r-66cg-79px
Type: github-advisory

## Affected
- PyPI: `paramiko` — affected >=2.0.0 <2.0.8
- PyPI: `paramiko` — affected >=2.1.0 <2.1.5
- PyPI: `paramiko` — affected >=2.2.0 <2.2.3
- PyPI: `paramiko` — affected >=2.3.0 <2.3.2
- PyPI: `paramiko` — affected >=2.4.0 <2.4.1
- PyPI: `paramiko` — affected >=1.18.0 <1.18.5
- PyPI: `paramiko` — affected >=0 <1.17.6

## Details
transport.py in the SSH server implementation of Paramiko before 1.17.6, 1.18.x before 1.18.5, 2.0.x before 2.0.8, 2.1.x before 2.1.5, 2.2.x before 2.2.3, 2.3.x before 2.3.2, and 2.4.x before 2.4.1 does not properly check whether authentication is completed before processing other requests, as demonstrated by channel-open. A customized SSH client can simply skip the authentication step.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7750
- https://github.com/paramiko/paramiko/issues/1175
- https://github.com/paramiko/paramiko/commit/fa29bd8446c8eab237f5187d28787727b4610516
- https://github.com/paramiko/paramiko/commit/e9dfd854bdaf8af15d7834f7502a0451d217bb8c
- https://www.exploit-db.com/exploits/45712
- https://web.archive.org/web/20190831123128/http://www.securityfocus.com/bid/103713
- https://usn.ubuntu.com/3603-2
- https://usn.ubuntu.com/3603-1
- https://lists.debian.org/debian-lts-announce/2021/12/msg00025.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00018.html
- https://github.com/pypa/advisory-database/tree/main/vulns/paramiko/PYSEC-2018-19.yaml
- https://github.com/paramiko/paramiko/blob/master/sites/www/changelog.rst
- https://github.com/paramiko/paramiko/blob/e861c7697622774071ce73b46ffe8817eacdedfa/sites/www/changelog.rst?plain=1#L759-L763
- https://github.com/paramiko/paramiko
- https://github.com/advisories/GHSA-232r-66cg-79px
- https://access.redhat.com/errata/RHSA-2018:1972
- https://access.redhat.com/errata/RHSA-2018:1525
- https://access.redhat.com/errata/RHSA-2018:1328
- https://access.redhat.com/errata/RHSA-2018:1274
- https://access.redhat.com/errata/RHSA-2018:1213
