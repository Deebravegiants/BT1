# [C] Coolify Vulnerable to Authenticated Remote Code Execution via Command Injection in Database Backup

## Summary
Severity: Critical
Advisory: CVE-2025-66209
Aliases: GHSA-vm5p-43qh-7pmq
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-66209
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.451, an authenticated command injection vulnerability in the Database Backup functionality allows users with application/service management permissions to execute arbitrary commands as root on managed servers. Database names used in backup operations are passed directly to shell commands without sanitization, enabling full remote code execution. Version 4.0.0-beta.451 fixes the issue.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.451
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66209.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-vm5p-43qh-7pmq
- https://nvd.nist.gov/vuln/detail/CVE-2025-66209
- https://github.com/coollabsio/coolify/pull/7375
- https://github.com/0xrakan/coolify-cve-2025-66209-66213
