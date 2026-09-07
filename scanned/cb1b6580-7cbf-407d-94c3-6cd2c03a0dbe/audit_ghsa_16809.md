# [M] Hugo Markdown titles do not escaped in internal render hooks

## Summary
Severity: Medium
Advisory: GHSA-ppf8-hhpp-f5hj
CVE: CVE-2024-32875
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-23
Source: https://github.com/advisories/GHSA-ppf8-hhpp-f5hj
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0.123.0 <0.125.3

## Details
### Impact

Title argument in Markdown for links and images not escaped in internal render hooks. Impacted are Hugo users who have these hooks enabled and do not trust their Markdown content files.

### Patches

Patched in v0.125.3.

### Workarounds

Replace with user defined templates or disable the internal templates: https://gohugo.io/getting-started/configuration-markup/#renderhooksimageenabledefault

### References

https://github.com/gohugoio/hugo/releases/tag/v0.125.3

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-ppf8-hhpp-f5hj
- https://nvd.nist.gov/vuln/detail/CVE-2024-32875
- https://github.com/gohugoio/hugo/commit/15a4b9b33715887001f6eff30721d41c0d4cfdd1
- https://github.com/gohugoio/hugo
- https://github.com/gohugoio/hugo/releases/tag/v0.125.3
- https://gohugo.io/getting-started/configuration-markup/#renderhooksimageenabledefault
- https://pkg.go.dev/vuln/GO-2024-2747
