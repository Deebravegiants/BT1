# [M] LiquidJS: An infinite loop vulnerability in `strip_html` filter

## Summary
Severity: Medium
Advisory: CVE-2026-61556
Aliases: GHSA-m7fp-h3p4-hr49
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-61556
Type: osv

## Details
LiquidJS is a Shopify / GitHub Pages compatible template engine in pure JavaScript. From 10.26.0 until 10.27.1, the strip_html filter in src/filters/html.ts can enter an infinite loop when an input string contains <, includes at least one preceding character, and has no later >. In strip_html, the search for the next opener advances lt while the loop index remains unchanged when the closer search returns -1, and the equality-only stall guard does not exit because the loop index is less than lt. Reprocessing the same state indefinitely blocks template rendering and can cause denial of service with an input as short as a<. This issue is fixed in version 10.27.1.

## References
- https://github.com/harttle/liquidjs/releases/tag/v10.27.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61556.json
- https://github.com/harttle/liquidjs/security/advisories/GHSA-m7fp-h3p4-hr49
- https://nvd.nist.gov/vuln/detail/CVE-2026-61556
- https://github.com/harttle/liquidjs/commit/5c3522f33928aae66f0fe85c36e1d9015c768fe2
- https://github.com/harttle/liquidjs/pull/917
