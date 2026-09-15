# [H] Coolify: OS Command Injection via Persistent Volume Names - Root RCE on Managed Servers

## Summary
Severity: High
Advisory: CVE-2026-42143
Aliases: GHSA-6pmw-6m96-4v4m
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-42143
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, user-controlled persistent volume names are interpolated into shell commands executed on managed servers without escaping or validation, allowing an authenticated member to inject shell metacharacters and execute commands as root when volume operations are triggered. This issue appears to be fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42143.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-6pmw-6m96-4v4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-42143
- https://github.com/coollabsio/coolify/commit/d2064dd4998694cda2eabd00149f7c4d1e94c699
