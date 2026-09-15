# [H] Apache Ranger: UnixAuth lacks brute-force protection

## Summary
Severity: High
Advisory: CVE-2026-65948
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-65948
Type: osv

## Details
UnixAuth lacks brute-force protection in Apache Ranger versions <= 2.8.0. 
Note:  UnixAuth is NOT a recommended option for production deployments. 
Users are recommended to upgrade to version 2.9.0, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/09/11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65948.json
- https://lists.apache.org/thread/cx53rbkxkn5hbvzv8ohwvndzrxhc06qf
- https://nvd.nist.gov/vuln/detail/CVE-2026-65948
