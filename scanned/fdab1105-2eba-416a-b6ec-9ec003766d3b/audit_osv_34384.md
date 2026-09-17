# [C] Coolify has Docker Compose Injection issue

## Summary
Severity: Critical
Advisory: CVE-2025-59156
Aliases: GHSA-h5xw-7xvp-xrxr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-59156
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.420.7, a Remote Code Execution (RCE)*vulnerability exists in Coolify's application deployment workflow. This flaw allows a low-privileged member to inject arbitrary Docker Compose directives during project creation or updates. By defining a malicious service that mounts the host filesystem, an attacker can achieve root-level command execution on the host OS, completely bypassing container isolation. Version 4.0.0-beta.420.7 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59156.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-h5xw-7xvp-xrxr
- https://nvd.nist.gov/vuln/detail/CVE-2025-59156
