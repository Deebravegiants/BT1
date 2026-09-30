# [M] SQL injection in github.com/navidrome/navidrome

## Summary
Severity: Medium
Advisory: GHSA-pmcr-2rhp-36hr
CVE: CVE-2022-23857
CWE: CWE-89
Ecosystem: Go
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-pmcr-2rhp-36hr
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0 <0.47.5

## Details
model/criteria/criteria.go in Navidrome before 0.47.5 is vulnerable to SQL injection attacks when processing crafted Smart Playlists. An authenticated user could abuse this to extract arbitrary data from the database, including the user table (which contains sensitive information such as the users' encrypted passwords).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23857
- https://github.com/navidrome/navidrome/commit/9e79b5cbf2a48c1e4344df00fea4ed3844ea965d
- https://github.com/navidrome/navidrome
- https://github.com/navidrome/navidrome/releases/tag/v0.47.5
