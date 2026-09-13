# [M] Grav CMS before 2.0.11 Path Traversal via watermark

## Summary
Severity: Medium
Advisory: CVE-2026-69089
Aliases: GHSA-w3f4-8pj2-599w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69089
Type: osv

## Details
Grav CMS 2.0.10 contains a path traversal vulnerability in ImageMedium::watermark(), which passes its unsanitized $image argument to RocketTheme\Toolbox\ResourceLocator\UniformResourceLocator::findResource(). Because the file:// scheme branch only lexically collapses '..' segments without a realpath/containment check, an editor authoring Markdown image syntax with traversal sequences can cause arbitrary image files outside Grav's media sandbox to be composited into a carrier image, which is then cached and served from a public, unauthenticated URL — disclosing those files to anonymous visitors.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69089.json
- https://github.com/getgrav/grav/security/advisories/GHSA-w3f4-8pj2-599w
- https://nvd.nist.gov/vuln/detail/CVE-2026-69089
- https://www.vulncheck.com/advisories/grav-cms-before-path-traversal-via-watermark
- https://github.com/getgrav/grav/commit/b282200a65ce979377963180629babd2335212ba
- https://github.com/getgrav/grav/commit/c569a53304cd7d95ff21bffa6fc590adcf0be83d
- https://github.com/getgrav/grav/commit/db8c1fcd63aaaf6d6b244bc6b4cfa5f7b96bbc7f
