# [M] docconv vulnerable to Memory Allocation with Excessive Size Value

## Summary
Severity: Medium
Advisory: GHSA-qvx2-59g8-8hph
CVE: CVE-2022-4741
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-25
Source: https://github.com/advisories/GHSA-qvx2-59g8-8hph
Type: github-advisory

## Affected
- Go: `github.com/sajari/docconv` — affected >=0 <1.2.1
- Go: `code.sajari.com/docconv` — affected >=0 <1.2.1

## Details
A vulnerability was found in docconv up to 1.2.0 and classified as problematic. This issue affects the function `ConvertDocx/ConvertODT/ConvertPages/ConvertXML/XMLToText`. The manipulation leads to uncontrolled memory allocation. The attack may be initiated remotely. Upgrading to version 1.2.1 can address this issue. The name of the patch is 42bcff666855ab978e67a9041d0cdea552f20301. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216779.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4741
- https://github.com/sajari/docconv/pull/111
- https://github.com/sajari/docconv/commit/42bcff666855ab978e67a9041d0cdea552f20301
- https://github.com/sajari/docconv
- https://github.com/sajari/docconv/releases/tag/v1.2.1
- https://pkg.go.dev/vuln/GO-2022-1188
- https://vuldb.com/?ctiid.216779
- https://vuldb.com/?id.216779
