# [C] Cherry Studio RCE Vulnerability Disclosure

## Summary
Severity: Critical
Advisory: CVE-2025-54382
Aliases: GHSA-gjp6-9cvg-8w93
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/CVE-2025-54382
Type: osv

## Details
Cherry Studio is a desktop client that supports for multiple LLM providers. In version 1.5.1, a remote code execution (RCE) vulnerability exists in the Cherry Studio platform when connecting to streamableHttp MCP servers. The issue arises from the server’s implicit trust in the oauth auth redirection endpoints and failure to properly sanitize the URL. This issue has been patched in version 1.5.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54382.json
- https://github.com/CherryHQ/cherry-studio/security/advisories/GHSA-gjp6-9cvg-8w93
- https://nvd.nist.gov/vuln/detail/CVE-2025-54382
