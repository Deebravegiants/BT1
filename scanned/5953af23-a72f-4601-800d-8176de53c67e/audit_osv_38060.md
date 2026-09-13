# [C] Reviactyl: OAuth account takeover via auto-linking

## Summary
Severity: Critical
Advisory: CVE-2026-34456
Aliases: GHSA-8mcf-rp68-xhfg
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34456
Type: osv

## Details
Reviactyl is an open-source game server management panel built using Laravel, React, FilamentPHP, Vite, and Go. From version 26.2.0-beta.1 to before version 26.2.0-beta.5, a vulnerability in the OAuth authentication flow allowed automatic linking of social accounts based solely on matching email addresses. An attacker could create or control a social account (e.g., Google, GitHub, Discord) using a victim’s email address and gain full access to the victim's account without knowing their password. This results in a full account takeover with no prior authentication required. This issue has been patched in version 26.2.0-beta.5.

## References
- https://github.com/reviactyl/panel/releases/tag/v26.2.0-beta.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34456.json
- https://github.com/reviactyl/panel/security/advisories/GHSA-8mcf-rp68-xhfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34456
- https://github.com/reviactyl/panel/commit/fe0c29fc62fefe354c9ab8936dfe30fdb586a896
