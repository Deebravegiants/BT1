# [H] Race Condition in Paramiko

## Summary
Severity: High
Advisory: GHSA-f8q4-jwww-x3wv
CVE: CVE-2022-24302
CWE: CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-19
Source: https://github.com/advisories/GHSA-f8q4-jwww-x3wv
Type: github-advisory

## Affected
- PyPI: `paramiko` — affected >=2.10.0 <2.10.1
- PyPI: `paramiko` — affected >=2.9.0 <2.9.3

## Details
In Paramiko before 2.10.1, a race condition (between creation and chmod) in the write_private_key_file function could allow unauthorized information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24302
- https://github.com/paramiko/paramiko/commit/4c491e299c9b800358b16fa4886d8d94f45abe2e
- https://github.com/advisories/GHSA-f8q4-jwww-x3wv
- https://github.com/paramiko/paramiko
- https://github.com/paramiko/paramiko/blob/363a28d94cada17f012c1604a3c99c71a2bda003/paramiko/pkey.py#L546
- https://github.com/pypa/advisory-database/tree/main/vulns/paramiko/PYSEC-2022-166.yaml
- https://lists.debian.org/debian-lts-announce/2022/03/msg00032.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00013.html
- https://lists.debian.org/debian-lts-announce/2025/12/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LUEUEGILZ7MQXRSUF5VMMO4SWJQVPTQL
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TPMKRUS4HO3P7NR7P4Y6CLHB4MBEE3AI
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U63MJ2VOLLQ35R7CYNREUHSXYLWNPVSB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LUEUEGILZ7MQXRSUF5VMMO4SWJQVPTQL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TPMKRUS4HO3P7NR7P4Y6CLHB4MBEE3AI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U63MJ2VOLLQ35R7CYNREUHSXYLWNPVSB
- https://www.paramiko.org/changelog.html
