# [M] Hugo: Certain markdown links are not properly escaped

## Summary
Severity: Medium
Advisory: GHSA-mcv8-8m8x-48pg
CVE: CVE-2026-35166
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-mcv8-8m8x-48pg
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0.60.0 <0.159.2

## Details
### Impact
Links and image links in the default markdown to HTML renderer are not properly escaped. Hugo users who trust their Markdown content or have custom render hooks for links and images are not affected.

### Patches
Patched in  v0.159.2

### Workarounds
Create custom render hooks for links and images in a Hugo theme/project.

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-mcv8-8m8x-48pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35166
- https://github.com/gohugoio/hugo/commit/479fe6c654937a850b65e74551dc4e857d52898f
- https://github.com/gohugoio/hugo
