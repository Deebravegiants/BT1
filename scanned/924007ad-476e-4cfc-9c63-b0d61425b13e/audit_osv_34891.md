# [C] Coolify Vulnerable to Authenticated Remote Code Execution via Command Injection in File Storage Directory Mount Path

## Summary
Severity: Critical
Advisory: CVE-2025-66213
Aliases: GHSA-cj2c-9jx8-j427
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-66213
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.451, an authenticated command injection vulnerability in the File Storage Directory Mount Path functionality allows users with application/service management permissions to execute arbitrary commands as root on managed servers. The file_storage_directory_source parameter is passed directly to shell commands without proper sanitization, enabling full remote code execution on the host system. Version 4.0.0-beta.451 fixes the issue.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.451
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66213.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-cj2c-9jx8-j427
- https://nvd.nist.gov/vuln/detail/CVE-2025-66213
- https://github.com/coollabsio/coolify/pull/7375
- https://github.com/0xrakan/coolify-cve-2025-66209-66213
