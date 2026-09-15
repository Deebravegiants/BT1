# [M] Minecraft RCON Terminal: Plain Text Password Storage in Configuration

## Summary
Severity: Medium
Advisory: CVE-2025-61680
Aliases: GHSA-4m33-hxqw-7j77
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-61680
Type: osv

## Details
Minecraft RCON Terminal is a VS Code extension that streamlines Minecraft server management. Versions 0.1.0 through 2.0.6 stores passwords using VS Code's configuration API which writes to settings.json in plaintext. This issue is fixed in version 2.1.0.

## References
- https://github.com/jaketcooper/Minecraft-rcon/releases/tag/2.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61680.json
- https://github.com/jaketcooper/Minecraft-rcon/security/advisories/GHSA-4m33-hxqw-7j77
- https://nvd.nist.gov/vuln/detail/CVE-2025-61680
- https://github.com/jaketcooper/Minecraft-rcon/commit/31272b541482d095d1578855c2b571268eb9b877
