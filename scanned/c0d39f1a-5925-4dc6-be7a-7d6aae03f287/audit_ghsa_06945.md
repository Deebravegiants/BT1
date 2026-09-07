# [M] Wings: Maliciously or erroneously created parsed config files can cause wings process to OOM

## Summary
Severity: Medium
Advisory: GHSA-q6hh-gp44-4hcm
CVE: CVE-2026-52857
CWE: CWE-400, CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-q6hh-gp44-4hcm
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.13.0

## Details
### Summary
Config file parsers, `json`, `yaml`, `xml` etc in parser.go have no file size limit/checks, allowing for a giant config file to potentially OOM the wings process.

### Impact
All wings users who have an egg with a non-`file` parser configuration file setting.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-q6hh-gp44-4hcm
- https://github.com/pterodactyl/wings/commit/5f71f65711b6b9e6f913bec94a7b36d9a5eaae49
- https://github.com/pterodactyl/wings
- https://github.com/pterodactyl/wings/releases/tag/v1.13.0
