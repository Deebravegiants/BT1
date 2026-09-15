# [C] docconv OS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-6m4h-hfpp-x8cx
CVE: CVE-2022-4643
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-6m4h-hfpp-x8cx
Type: github-advisory

## Affected
- Go: `github.com/sajari/docconv` — affected >=0 <1.2.1
- Go: `code.sajari.com/docconv` — affected >=1.1.0 <1.3.5

## Details
A vulnerability was found in docconv prior to version 1.2.1. It has been declared as critical. This vulnerability affects the function ConvertPDFImages of the file pdf_ocr.go. The manipulation of the argument path leads to os command injection. The attack can be initiated remotely. Upgrading to version 1.2.1 can address this issue. The name of the patch is b19021ade3d0b71c89d35cb00eb9e589a121faa5. It is recommended to upgrade the affected component. VDB-216502 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4643
- https://github.com/sajari/docconv/pull/110
- https://github.com/sajari/docconv/commit/b19021ade3d0b71c89d35cb00eb9e589a121faa5
- https://github.com/sajari/docconv
- https://github.com/sajari/docconv/releases/tag/v1.2.1
- https://github.com/sajari/docconv/releases/tag/v1.3.5
- https://pkg.go.dev/vuln/GO-2022-1184
- https://vuldb.com/?id.216502
