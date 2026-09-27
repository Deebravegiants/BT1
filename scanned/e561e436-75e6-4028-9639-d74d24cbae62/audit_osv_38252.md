# [M] Pi-hole FTL: CLI API sessions can import Teleporter archives and modify configuration

## Summary
Severity: Medium
Advisory: CVE-2026-35491
Aliases: GHSA-r7g8-3fj7-m5qq
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35491
Type: osv

## Details
FTLDNS (pihole-FTL) provides an interactive API and also generates statistics for Pi-hole's Web interface. From 6.0 to before 6.6, Pi-hole FTL supports a CLI password feature (webserver.api.cli_pw) that creates “CLI” API sessions intended to be read-only for configuration changes. While /api/config correctly blocks CLI sessions from mutating configuration, /api/teleporter allowed Teleporter imports for CLI sessions, enabling a CLI-scoped session to overwrite configuration via a Teleporter archive (authorization bypass). This vulnerability is fixed in 6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35491.json
- https://github.com/pi-hole/FTL/security/advisories/GHSA-r7g8-3fj7-m5qq
- https://nvd.nist.gov/vuln/detail/CVE-2026-35491
