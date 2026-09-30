# [C] Coolify Vulnerable to Authenticated Remote Code Execution via Command Injection in PostgreSQL Init Script Filename

## Summary
Severity: Critical
Advisory: CVE-2025-66211
Aliases: GHSA-24mp-fc9q-c884
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-66211
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.451, an authenticated command injection vulnerability in PostgreSQL Init Script Filename handling allows users with application/service management permissions to execute arbitrary commands as root on managed servers. PostgreSQL initialization script filenames are passed to shell commands without proper validation, enabling full remote code execution. Version 4.0.0-beta.451 fixes the issue.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.451
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66211.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-24mp-fc9q-c884
- https://nvd.nist.gov/vuln/detail/CVE-2025-66211
- https://github.com/coollabsio/coolify/pull/7375
- https://github.com/0xrakan/coolify-cve-2025-66209-66213
