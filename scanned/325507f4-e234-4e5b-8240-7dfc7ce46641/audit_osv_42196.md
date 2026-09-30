# [H] Apache Impala: RCE via External Data Source Class Loading

## Summary
Severity: High
Advisory: CVE-2026-65181
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-65181
Type: osv

## Details
Insufficient authorization of Data Source tables in Impala 2.7-4.5 allows a client with privileges to upload a file to remote storage and create a table to execute arbitrary Java code.
Users are recommended to upgrade to version 4.5.2, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/09/08/24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65181.json
- https://lists.apache.org/thread/2ty3srsh96j86xxg4g1hbo5rwvszwcnl
- https://nvd.nist.gov/vuln/detail/CVE-2026-65181
