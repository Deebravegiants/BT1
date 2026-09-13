# [M] Apache Lucene.Net: Arbitrary file write from malicious server to Lucene.Net.Replicator client

## Summary
Severity: Medium
Advisory: CVE-2026-47897
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/AU:Y/RE:L)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-47897
Type: osv

## Details
Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability in Apache Lucene.Net (Lucene.Net.Replicator library).

This issue affects Apache Lucene.Net.Replicator: from 4.8.0-beta00005 before 4.8.0-beta00018.

Users are recommended to upgrade to version 4.8.0-beta00018, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/03/2
- https://www.nuget.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47897.json
- https://lists.apache.org/thread/on1j3zmvgtf8n9fw78z3lyf6dn94p5zc
- https://nvd.nist.gov/vuln/detail/CVE-2026-47897
