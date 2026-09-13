# [H] Coolify: Authenticated Remote Code Execution via Command Injection in Destination Network Management

## Summary
Severity: High
Advisory: CVE-2026-34594
Aliases: GHSA-mf8p-rj62-9f9m
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-34594
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, an authenticated command injection vulnerability in the Destination Network Management functionality allows users with destination management permissions to execute arbitrary commands as root on managed servers. The "network" parameter is passed directly to shell commands without proper sanitization, enabling full remote code execution on the host system. This vulnerability is fixed in 4.0.0-beta.471.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34594.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-mf8p-rj62-9f9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34594
