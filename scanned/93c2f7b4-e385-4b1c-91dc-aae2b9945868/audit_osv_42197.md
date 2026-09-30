# [M] xxl-job Cross-Job-Group Log Disclosure via Missing Authorization Check in /joblog/logDetailCat

## Summary
Severity: Medium
Advisory: CVE-2026-65316
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-65316
Type: osv

## Details
XXL-Job version 2.4.2 contains an insecure direct object reference vulnerability that allows authenticated users to read execution log content from job groups they are not authorized to access by supplying arbitrary sequential log IDs to the logDetailCat endpoint. Attackers can enumerate log records across all job groups by calling the logDetailCat endpoint with incremented logId parameter values, bypassing the permission check present in the sibling logDetailPage endpoint, and retrieve sensitive log content from restricted job groups.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65316.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65316
- https://www.vulncheck.com/advisories/xxl-job-cross-job-group-log-disclosure-via-missing-authorization-check-in-joblog-logdetailcat
- https://github.com/xuxueli/xxl-job/issues/3983
- https://github.com/xuxueli/xxl-job
