# [M] Gitea allows XSS because the search input box (for creating tags and branches) is v-html instead of v-text

## Summary
Severity: Medium
Advisory: GHSA-898p-hh3p-hf9r
CVE: CVE-2025-68942
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-898p-hh3p-hf9r
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.22.2

## Details
Gitea before 1.22.2 allows XSS because the search input box (for creating tags and branches) is v-html instead of v-text.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68942
- https://github.com/go-gitea/gitea/pull/31966
- https://blog.gitea.com/release-of-1.22.2
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.22.2
