# [H] Termix has improper certificate validation in Electron desktop client that enables MITM credential/token theft

## Summary
Severity: High
Advisory: CVE-2026-45745
Aliases: GHSA-r9gw-3w87-mhh7
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-45745
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Starting in version 1.7.0, Termix Desktop (Electron) disables TLS certificate validation, allowing a machine-in-the-middle attacker to intercept and modify HTTPS traffic to the configured Termix server. This can lead to credential theft and JWT/session theft during login and normal use. As of time of publication, no known patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45745.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-r9gw-3w87-mhh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-45745
