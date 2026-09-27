# [H] Coolify: Command Injection via Newline in Pre/Post Deployment Commands (Heredoc Transport)

## Summary
Severity: High
Advisory: CVE-2026-34152
Aliases: GHSA-5qp8-9gg7-4c86
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34152
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, pre-deployment and post-deployment commands are single-quote escaped but then sent through SSH heredoc transport that preserves newlines, allowing an authenticated user to inject additional shell statements that execute on the remote server during deployment. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34152.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-5qp8-9gg7-4c86
- https://nvd.nist.gov/vuln/detail/CVE-2026-34152
- https://github.com/coollabsio/coolify/commit/ad95d65aca064f49b38f73f88d61f842737d5463
- https://github.com/coollabsio/coolify/pull/9173
