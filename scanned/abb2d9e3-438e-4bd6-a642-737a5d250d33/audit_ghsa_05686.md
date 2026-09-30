# [M] Beam Exposes sensitive information via joinCleanPath function

## Summary
Severity: Medium
Advisory: GHSA-73jg-4qh6-3f4g
CVE: CVE-2025-69820
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-73jg-4qh6-3f4g
Type: github-advisory

## Affected
- Go: `github.com/beam-cloud/beta9` — affected >=0

## Details
Directory Traversal vulnerability in Beam beta9 v.0.1.552 allows a remote attacker to obtain sensitive information via the joinCleanPath function

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69820
- https://github.com/beam-cloud/beta9
- https://github.com/beam-cloud/beta9/blob/c1cd75e813cf7d53e916157d920099e89ef45caa/pkg/abstractions/volume/multipart.go#L45
- https://github.com/ryotaromatsui/CVEs/tree/main/CVE-2025-69820
