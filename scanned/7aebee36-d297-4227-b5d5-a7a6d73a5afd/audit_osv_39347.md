# [M] Nextcloud: Authorization bypass in approval feature allows unauthorized file sharing with approvers

## Summary
Severity: Medium
Advisory: CVE-2026-45275
Aliases: GHSA-v8q8-w6c3-3gv9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45275
Type: osv

## Details
Nextcloud is an open source content collaboration platform. Prior to version 2.7.2, a privilege escalation vulnerability exists in the Approval app that allows a user without sharing permissions to force the system to share a file with approvers. This results in an authorization bypass and privilege escalation, allowing unauthorized distribution of restricted files. This issue has been patched in version 2.7.2.

## References
- https://hackerone.com/reports/3593780
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45275.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-v8q8-w6c3-3gv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45275
- https://github.com/nextcloud/approval/pull/392
