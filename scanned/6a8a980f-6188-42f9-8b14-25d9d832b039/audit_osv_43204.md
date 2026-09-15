# [M] Grav 2.0.11 Path Traversal via Backup Profile Configuration

## Summary
Severity: Medium
Advisory: CVE-2026-72820
Aliases: GHSA-fch7-cpv4-w7hg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-72820
Type: osv

## Details
Grav versions before 2.0.13 fail to properly validate backup profile root paths, allowing attackers to archive directories outside GRAV_ROOT when not in the hard-coded deny-list. Attackers with profile editor access can configure backup profiles with traversal paths to expose sensitive files from locations like /opt, /mnt, or /srv.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72820.json
- https://github.com/getgrav/grav/security/advisories/GHSA-fch7-cpv4-w7hg
- https://nvd.nist.gov/vuln/detail/CVE-2026-72820
- https://www.vulncheck.com/advisories/grav-path-traversal-via-backup-profile-configuration
- https://github.com/getgrav/grav/commit/ad9709f865b09b68798fb1ac375b484a8cc1d892
