# [M] Apache Impala: Avro Schema URL Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: CVE-2026-54048
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-54048
Type: osv

## Details
Specifying tblproperties('avro.schema.url'=' http://...' ) or with a 'file:///' URI on a table in Impala 2.0.0 to 4.5.1 on all platforms allows an attacker to trigger a GET request to internal endpoints they may not have access to but that Impala does and the response my be exposed via parsing error messages.
Users are recommended to upgrade to version 4.5.2, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/09/08/21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54048.json
- https://lists.apache.org/thread/cn3q4s8yx924ndlm3gt04o6g4rfm980c
- https://nvd.nist.gov/vuln/detail/CVE-2026-54048
