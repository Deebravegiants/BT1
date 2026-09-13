# [M] Hugo does not escape some attributes in internal templates

## Summary
Severity: Medium
Advisory: GHSA-c2xf-9v2r-r2rx
CVE: CVE-2024-55601
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-c2xf-9v2r-r2rx
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0.123.0 <0.139.4

## Details
## Impact

Some HTML attributes in Markdown in the internal templates listed below not escaped. Impacted are Hugo users who do not trust their Markdown content files and are using one or more of these templates.

* `_default/_markup/render-link.html` from `v0.123.0`
* `_default/_markup/render-image.html` from `v0.123.0`
* `_default/_markup/render-table.html` from `v0.134.0`
* `shortcodes/youtube.html` from `v0.125.0`

## Patches

Patched in v0.139.4.

## Workarounds

Replace with user defined templates or disable the internal templates: https://gohugo.io/getting-started/configuration-markup/#renderhooksimageenabledefault

## References

* https://github.com/gohugoio/hugo/releases/tag/v0.139.4
* https://gohugo.io/about/security/

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-c2xf-9v2r-r2rx
- https://nvd.nist.gov/vuln/detail/CVE-2024-55601
- https://github.com/gohugoio/hugo/commit/54398f8d572c689f9785d59e907fd910a23401b0
- https://github.com/gohugoio/hugo
- https://github.com/gohugoio/hugo/releases/tag/v0.139.4
- https://gohugo.io/getting-started/configuration-markup/#renderhooksimageenabledefault
