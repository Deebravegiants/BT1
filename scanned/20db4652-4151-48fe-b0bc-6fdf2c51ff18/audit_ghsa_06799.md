# [H] Wings: Maliciously crafted packet during SFTP connection handshake causes denial of service

## Summary
Severity: High
Advisory: GHSA-ghrq-5wpp-hxx5
CVE: CVE-2026-52856
CWE: CWE-129, CWE-20, CWE-248, CWE-400, CWE-617, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-ghrq-5wpp-hxx5
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.13.0

## Details
### Summary
A maliciously crafted packet received & parsed during the SFTP connection handshake will cause a Go panic.

### Impact
All wings users with an open SFTP port.

### Workarounds
Close SFTP port.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-ghrq-5wpp-hxx5
- https://github.com/pterodactyl/wings/commit/8e49c7c0eda815d3ada171831876a1c14c493026
- https://github.com/pterodactyl/wings
- https://github.com/pterodactyl/wings/releases/tag/v1.13.0
