# [H] Apache DolphinScheduler: Users are able to use tenants that are not defined on the platform during workflow execution.

## Summary
Severity: High
Advisory: CVE-2026-23902
Aliases: GHSA-72mv-wwvm-vgp5
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-23902
Type: osv

## Details
Incorrect Authorization vulnerability in Apache DolphinScheduler allows authenticated users with system login permissions to use tenants that are not defined on the platform during workflow execution.

This issue affects Apache DolphinScheduler versions prior to 3.4.1. 

Users are recommended to upgrade to version 3.4.1, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/24/1
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23902.json
- https://lists.apache.org/thread/hy4ntb2gys8150zfmnxhsd5ph0hoh7s9
- https://nvd.nist.gov/vuln/detail/CVE-2026-23902
