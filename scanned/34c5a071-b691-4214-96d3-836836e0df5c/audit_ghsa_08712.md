# [H] FileBrowser Quantum: unauthenticated user share share info 

## Summary
Severity: High
Advisory: GHSA-3jmg-p96m-m328
CVE: CVE-2026-46410
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-3jmg-p96m-m328
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser/backend` — affected >=0 <0.0.0-20260514154726-1802e1281135
- Go: `github.com/gtsteffaniak/filebrowser` — affected >=0 <1.2.1-stable.0.20260514154726-1802e1281135

## Details
### Impact
Some sensitive info -- such as source and path can get exposed.

### Patches
Update to the latest version

### Workarounds
no

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-3jmg-p96m-m328
- https://github.com/gtsteffaniak/filebrowser/commit/1802e1281135cba83eb4acd86b58293fe121e2a5
- https://github.com/gtsteffaniak/filebrowser
