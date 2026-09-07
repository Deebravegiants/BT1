# [M] goldmark vulnerable to Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-c97m-vxhj-p7j6
CVE: CVE-2026-5160
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-c97m-vxhj-p7j6
Type: github-advisory

## Affected
- Go: `github.com/yuin/goldmark/renderer/html` — affected >=0 <1.7.17

## Details
Versions of the package github.com/yuin/goldmark/renderer/html before 1.7.17 are vulnerable to Cross-site Scripting (XSS) due to improper ordering of URL validation and normalization. The renderer validates link destinations using a prefix-based check (IsDangerousURL) before resolving HTML entities. This allows an attacker to bypass protocol filtering by encoding dangerous schemes using HTML5 named character references. For example, a payload such as javascript&colon;alert(1) is not recognized as dangerous during validation, leading to arbitrary script execution in the context of applications that render the URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5160
- https://github.com/yuin/goldmark/commit/cb46bbc4eca29d55aa9721e04ad207c23ccc44f9
- https://github.com/yuin/goldmark
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMYUINGOLDMARKRENDERERHTML-15838406
