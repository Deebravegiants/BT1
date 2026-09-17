# [C] Coolify Vulnerable to Authenticated Remote Code Execution via Command Injection in Dynamic Proxy Configuration Filename

## Summary
Severity: Critical
Advisory: CVE-2025-66212
Aliases: GHSA-q7rg-2j7p-83gp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-66212
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.451, an authenticated command injection vulnerability in the Dynamic Proxy Configuration Filename handling allows users with application/service management permissions to execute arbitrary commands as root on managed servers. Proxy configuration filenames are passed to shell commands without proper escaping, enabling full remote code execution. Version 4.0.0-beta.451 fixes the issue.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.451
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66212.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-q7rg-2j7p-83gp
- https://nvd.nist.gov/vuln/detail/CVE-2025-66212
- https://github.com/coollabsio/coolify/pull/7375
- https://github.com/0xrakan/coolify-cve-2025-66209-66213
