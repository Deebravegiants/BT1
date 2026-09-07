# [M] Gouniverse GoLang CMS vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-pv7h-hg6m-82j8
CVE: CVE-2024-8572
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-08
Source: https://github.com/advisories/GHSA-pv7h-hg6m-82j8
Type: github-advisory

## Affected
- Go: `github.com/gouniverse/cms` — affected >=0 <1.4.1

## Details
A vulnerability was found in Gouniverse GoLang CMS 1.4.0. It has been declared as problematic. This vulnerability affects the function PageRenderHtmlByAlias of the file FrontendHandler.go. The manipulation of the argument alias leads to cross site scripting. The attack can be initiated remotely. Upgrading to version 1.4.1 is able to address this issue. The patch is identified as 3e661cdfb4beeb9fe2ad507cdb8104c0b17d072c. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8572
- https://github.com/gouniverse/cms/issues/5
- https://github.com/gouniverse/cms/issues/5#issuecomment-2330848731
- https://github.com/gouniverse/cms/commit/3e661cdfb4beeb9fe2ad507cdb8104c0b17d072c
- https://github.com/gouniverse/cms
- https://github.com/gouniverse/cms/releases/tag/v1.4.1
- https://pkg.go.dev/vuln/GO-2024-3125
- https://vuldb.com/?ctiid.276802
- https://vuldb.com/?id.276802
- https://vuldb.com/?submit.401896
