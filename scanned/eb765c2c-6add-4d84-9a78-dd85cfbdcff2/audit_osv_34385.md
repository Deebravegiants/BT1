# [C] Coolify has Git Repository RCE

## Summary
Severity: Critical
Advisory: CVE-2025-59157
Aliases: GHSA-5cg9-38qj-8mc3
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-59157
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.420.7, the Git Repository field during project creation is vulnerable to command injection. User input is not properly sanitized, allowing attackers to inject arbitrary shell commands that execute on the underlying server during the deployment workflow. A regular member user can exploit this vulnerability. Version 4.0.0-beta.420.7 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59157.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-5cg9-38qj-8mc3
- https://nvd.nist.gov/vuln/detail/CVE-2025-59157
