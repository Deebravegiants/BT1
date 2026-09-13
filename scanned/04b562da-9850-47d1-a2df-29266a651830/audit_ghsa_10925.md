# [H] XPath: Boolean expression infinite loop leads to denial of service via CPU exhaustion

## Summary
Severity: High
Advisory: GHSA-65xw-vw82-r86x
CVE: CVE-2026-32287
CWE: CWE-400, CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-65xw-vw82-r86x
Type: github-advisory

## Affected
- Go: `github.com/antchfx/xpath` — affected >=0 <1.3.6

## Details
Boolean expressions that evaluate to true can cause an infinite loop in logicalQuery.Select, leading to 100% CPU usage. This can be triggered by top-level selectors such as "1=1" or "true()".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32287
- https://github.com/antchfx/xpath/issues/121
- https://github.com/golang/vulndb/issues/4526
- https://github.com/antchfx/xpath/commit/afd4762cc342af56345a3fb4002a59281fcab494
- https://github.com/antchfx/xpath
- https://pkg.go.dev/vuln/GO-2026-4526
- https://securityinfinity.com/research/infinite-loop-dos-in-antchfx-xpath-logicalquery-select
