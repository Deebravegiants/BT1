# [M] Infinite loop in github.com/gomarkdown/markdown

## Summary
Severity: Medium
Advisory: GHSA-xhr3-wf7j-h255
CVE: CVE-2024-44337
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-xhr3-wf7j-h255
Type: github-advisory

## Affected
- Go: `github.com/gomarkdown/markdown` — affected >=0 <0.0.0-20240729212818-a2a9c4f76ef5

## Details
The package `github.com/gomarkdown/markdown` is a Go library for parsing Markdown text and rendering as HTML. Prior to pseudoversion `v0.0.0-20240729232818-a2a9c4f`, which corresponds with commit `a2a9c4f76ef5a5c32108e36f7c47f8d310322252`, there was a logical problem in the paragraph function of the parser/block.go file, which allowed a remote attacker to cause a denial of service (DoS) condition by providing a tailor-made input that caused an infinite loop, causing the program to hang and consume resources indefinitely. Submit `a2a9c4f76ef5a5c32108e36f7c47f8d310322252` contains fixes to this problem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-44337
- https://github.com/gomarkdown/markdown/commit/a2a9c4f76ef5a5c32108e36f7c47f8d310322252
- https://github.com/Brinmon/CVE-2024-44337
- https://github.com/gomarkdown/markdown
- https://pkg.go.dev/vuln/GO-2024-3205
