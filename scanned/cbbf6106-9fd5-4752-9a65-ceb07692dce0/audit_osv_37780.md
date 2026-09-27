# [H] Crash when receiving specially-crafted packets

## Summary
Severity: High
Advisory: CVE-2026-33250
Aliases: GHSA-f76g-6w3f-f6r3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-33250
Type: osv

## Details
Freeciv21 is a free open source, turn-based, empire-building strategy game. Versions prior to 3.1.1 crash with a stack overflow when receiving specially-crafted packets. A remote attacker can use this to take down any public server. A malicious server can use this to crash the game on the player's machine. Authentication is not needed and, by default, logs do not contain any useful information. All users should upgrade to Freeciv21 version 3.1.1. Running the server behind a firewall can help mitigate the issue for non-public servers. For local games, Freeciv21 restricts connections to the current user and is therefore not affected.

## References
- https://github.com/longturn/freeciv21/releases/tag/v3.1.1
- https://redmine.freeciv.org/issues/1955
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33250.json
- https://github.com/longturn/freeciv21/security/advisories/GHSA-f76g-6w3f-f6r3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33250
- https://github.com/longturn/freeciv21/commit/ad8e18ca22595529599782b2984bf44df8d69ed6
