# [C] Mjolnir v1.9.0 accepts commands from any room

## Summary
Severity: Critical
Advisory: CVE-2025-24024
Aliases: GHSA-3jq6-xc85-m394
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2025-24024
Type: osv

## Details
Mjolnir is a moderation tool for Matrix. Mjolnir v1.9.0 responds to management commands from any room the bot is member of. This can allow users who aren't operators of the bot to use the bot's functions, including server administration components if enabled. Version 1.9.1 reverts the feature that introduced the bug, and version 1.9.2 reintroduces the feature safely. Downgrading to version 1.8.3 is recommended if upgrading to 1.9.1 or higher isn't possible.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24024.json
- https://github.com/matrix-org/mjolnir/security/advisories/GHSA-3jq6-xc85-m394
- https://nvd.nist.gov/vuln/detail/CVE-2025-24024
- https://github.com/matrix-org/mjolnir/commit/b437fa16b5425985715df861987c836affd51eea
- https://github.com/matrix-org/mjolnir/commit/d0ef527a9e3eb45e17143d5295a64b775ccaa23d
