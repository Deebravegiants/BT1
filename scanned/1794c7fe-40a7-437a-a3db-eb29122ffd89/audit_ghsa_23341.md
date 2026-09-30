# [M] Improper Neutralization of CRLF Sequences in urllib3 library for Python

## Summary
Severity: Medium
Advisory: GHSA-r64q-w8jr-g9qp
CVE: CVE-2019-11236
CWE: CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r64q-w8jr-g9qp
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=0 <1.24.3

## Details
In the urllib3 library through 1.24.2 for Python, CRLF injection is possible if the attacker controls the request parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11236
- https://github.com/urllib3/urllib3/issues/1553
- https://usn.ubuntu.com/3990-2
- https://usn.ubuntu.com/3990-1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XOSA2NT4DUQDBEIWE6O7KKD24XND7TE2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TBI45HO533KYHNB5YRO43TBYKA3E3VRL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R62XGEYPUTXMRHGX5I37EBCGQ5COHGKR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NKGPJLVLVYCL4L4B4G5TIOTVK4BKPG72
- https://lists.debian.org/debian-lts-announce/2023/10/msg00012.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00015.html
- https://lists.debian.org/debian-lts-announce/2019/06/msg00016.html
- https://github.com/urllib3/urllib3
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2019-132.yaml
- https://github.com/advisories/GHSA-r64q-w8jr-g9qp
- https://access.redhat.com/errata/RHSA-2019:3590
- https://access.redhat.com/errata/RHSA-2019:3335
- https://access.redhat.com/errata/RHSA-2019:2272
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00041.html
