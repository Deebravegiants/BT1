# [M] Coolify unauthenticated feedback endpoint allows Discord webhook abuse

## Summary
Severity: Medium
Advisory: CVE-2026-41899
Aliases: GHSA-v64c-v633-58xp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-41899
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.474, POST /api/feedback has no authentication, no rate limiting, and no input validation, allowing arbitrary content to be forwarded directly to a Discord webhook and enabling spam, content injection, and webhook abuse. This issue is fixed in version 4.0.0-beta.474.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41899.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-v64c-v633-58xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41899
- https://github.com/coollabsio/coolify/commit/371e883c75a87d82c398bf89ee8ad6387348520d
- https://github.com/coollabsio/coolify/pull/9653
