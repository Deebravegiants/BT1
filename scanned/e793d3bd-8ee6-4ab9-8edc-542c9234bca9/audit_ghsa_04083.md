# [H] Improper Certificate Validation in urllib3

## Summary
Severity: High
Advisory: GHSA-mh33-7rrq-662w
CVE: CVE-2019-11324
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-04-19
Source: https://github.com/advisories/GHSA-mh33-7rrq-662w
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=0 <1.24.2

## Details
The urllib3 library before 1.24.2 for Python mishandles certain cases where the desired set of CA certificates is different from the OS store of CA certificates, which results in SSL connections succeeding in situations where a verification failure is the correct outcome. This is related to use of the `ssl_context`, `ca_certs`, or `ca_certs_dir` argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11324
- https://github.com/urllib3/urllib3/commit/1efadf43dc63317cd9eaa3e0fdb9e05ab07254b1
- https://access.redhat.com/errata/RHSA-2019:3335
- https://access.redhat.com/errata/RHSA-2019:3590
- https://github.com/advisories/GHSA-mh33-7rrq-662w
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2019-133.yaml
- https://github.com/urllib3/urllib3
- https://github.com/urllib3/urllib3/compare/a6ec68a...1efadf4
- https://lists.debian.org/debian-lts-announce/2021/06/msg00015.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NKGPJLVLVYCL4L4B4G5TIOTVK4BKPG72
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XOSA2NT4DUQDBEIWE6O7KKD24XND7TE2
- https://pypi.org/project/urllib3/1.24.2
- https://usn.ubuntu.com/3990-1
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00041.html
- http://www.openwall.com/lists/oss-security/2019/04/19/1
