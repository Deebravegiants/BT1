# [C] Apache Gravitino: URL path injection via unencoded user-supplied identifiers in MCP REST client f-string URL construction, enabling path traversal to unintended API endpoints.

## Summary
Severity: Critical
Advisory: CVE-2026-41041
Aliases: PYSEC-2026-3441
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-41041
Type: osv

## Details
URL path injection via unencoded user-supplied identifiers vulnerability in Apache Gravitino.

This issue affects Apache Gravitino: from 1.0.0 before 1.2.1.

Users are recommended to upgrade to version 1.2.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/13/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41041.json
- https://lists.apache.org/thread/4dnwg1qzb2yns1fkfmq0z45vmwyzytgz
- https://nvd.nist.gov/vuln/detail/CVE-2026-41041
