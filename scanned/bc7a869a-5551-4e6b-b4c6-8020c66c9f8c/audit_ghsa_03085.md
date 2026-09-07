# [M] Cross-site Scripting in Documize

## Summary
Severity: Medium
Advisory: GHSA-wmwp-pggc-h4mj
CVE: CVE-2019-19619
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-wmwp-pggc-h4mj
Type: github-advisory

## Affected
- Go: `github.com/documize/community` — affected >=0 <3.5.1

## Details
domain/section/markdown/markdown.go in Documize before 3.5.1 mishandles untrusted Markdown content. This was addressed by adding the bluemonday HTML sanitizer to defend against XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19619
- https://github.com/documize/community/commit/a4384210d4d0d6b18e6fdb7e155de96d4a1cf9f3
- https://github.com/documize/community
- https://github.com/documize/community/compare/v3.5.0...v3.5.1
- https://github.com/documize/community/releases/tag/v3.5.1
- https://pkg.go.dev/vuln/GO-2021-0086
