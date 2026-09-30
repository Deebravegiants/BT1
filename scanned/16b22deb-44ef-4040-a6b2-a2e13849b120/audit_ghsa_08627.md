# [M] Apache Thrift has a Memory Allocation with Excessive Size Value Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2f9f-gq7v-9h6m
CVE: CVE-2026-43868
CWE: CWE-1285, CWE-789
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-2f9f-gq7v-9h6m
Type: github-advisory

## Affected
- crates.io: `thrift` — affected >=0 <0.23.0

## Details
Memory Allocation with Excessive Size Value vulnerability in Apache Thrift.

This issue affects Apache Thrift: before 0.23.0.

Users are recommended to upgrade to version [0.23.0](https://github.com/apache/thrift/releases/tag/v0.23.0), which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43868
- https://github.com/apache/thrift/commit/d5152211af61f850ec393604316804096dd4632e
- https://access.redhat.com/errata/RHSA-2026:26586
- https://access.redhat.com/errata/RHSA-2026:42644
- https://access.redhat.com/security/cve/CVE-2026-43868
- https://bugzilla.redhat.com/show_bug.cgi?id=2466670
- https://github.com/apache/thrift
- https://lists.apache.org/thread/zj76dtwnbbs1m7z3focf4wd51pqpsmn9
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43868.json
