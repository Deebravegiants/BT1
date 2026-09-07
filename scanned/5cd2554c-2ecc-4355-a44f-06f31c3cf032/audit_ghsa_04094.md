# [C] SQLAlchemy vulnerable to SQL Injection via order_by parameter

## Summary
Severity: Critical
Advisory: GHSA-887w-45rq-vxgf
CVE: CVE-2019-7164
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-16
Source: https://github.com/advisories/GHSA-887w-45rq-vxgf
Type: github-advisory

## Affected
- PyPI: `SQLAlchemy` — affected >=0 <1.3.0b3

## Details
SQLAlchemy before 1.3.0b3 allows SQL Injection via the order_by parameter. The fix (commit 30307c4) was applied only to the main branch and was never backported to the 1.2.x release line; all 1.2.x versions remain vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7164
- https://github.com/sqlalchemy/sqlalchemy/issues/4481
- https://github.com/sqlalchemy/sqlalchemy/commit/30307c4616ad67c01ddae2e1e8e34fabf6028414
- https://access.redhat.com/errata/RHSA-2019:0981
- https://access.redhat.com/errata/RHSA-2019:0984
- https://github.com/advisories/GHSA-887w-45rq-vxgf
- https://github.com/pypa/advisory-database/tree/main/vulns/sqlalchemy/PYSEC-2019-123.yaml
- https://github.com/sqlalchemy/sqlalchemy
- https://lists.debian.org/debian-lts-announce/2019/03/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00005.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00087.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00016.html
