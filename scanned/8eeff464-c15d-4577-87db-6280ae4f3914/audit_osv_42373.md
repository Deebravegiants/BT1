# [M] Linuxfabrik monitoring-plugins: Symlink following in logfile legacy database migration

## Summary
Severity: Medium
Advisory: CVE-2026-67433
Aliases: GHSA-w2gg-hx6w-24w3
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-67433
Type: osv

## Details
Linuxfabrik monitoring-plugins provides Python monitoring plugins for Icinga, Nagios, and related monitoring systems. In version 6.0.0, the logfile check legacy database migration moved a predictable path from /tmp with os.rename() and allowed a local user controlling the plugin account to place a symlink that would be followed by sqlite3.connect() during a root-run check.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67433.json
- https://github.com/Linuxfabrik/monitoring-plugins/security/advisories/GHSA-w2gg-hx6w-24w3
- https://nvd.nist.gov/vuln/detail/CVE-2026-67433
- https://github.com/Linuxfabrik/monitoring-plugins/commit/6df1f574aa9dc6541e092f1ce482ecc1315cded0
