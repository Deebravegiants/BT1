# [H] LiquidJS: Uncontrolled Resource Consumption in `join` filter allows template authors to bypass `memoryLimit` and crash the process

## Summary
Severity: High
Advisory: CVE-2026-69222
Aliases: GHSA-4r6h-5v86-94p3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-69222
Type: osv

## Details
LiquidJS is a Shopify / GitHub Pages compatible template engine in pure JavaScript. Prior to 10.27.2, the join filter in src/filters/array.ts computes complexity from array.length and separator length instead of the total string length produced by array.join(sep). The concat filter can cheaply double arrays of references, after which join materializes the referenced content while charging only for element count, allowing a template to exceed a configured memoryLimit by a large factor. The sibling array_to_sentence_string filter in src/filters/string.ts has the same accounting defect, and a crafted template can allocate toward V8's string or process memory limit and crash the process. This issue is fixed in version 10.27.2.

## References
- https://github.com/harttle/liquidjs/releases/tag/v10.27.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69222.json
- https://github.com/harttle/liquidjs/security/advisories/GHSA-4r6h-5v86-94p3
- https://nvd.nist.gov/vuln/detail/CVE-2026-69222
- https://github.com/harttle/liquidjs/commit/7ab49f999ac045ec1e87f3a7a9fd68dd9e8602b3
- https://github.com/harttle/liquidjs/pull/925
