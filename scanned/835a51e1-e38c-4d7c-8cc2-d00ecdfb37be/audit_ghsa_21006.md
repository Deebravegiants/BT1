# [M] Gophish before 0.12.0 vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-hvw3-p9px-gpc9
CVE: CVE-2022-25295
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-12
Source: https://github.com/advisories/GHSA-hvw3-p9px-gpc9
Type: github-advisory

## Affected
- Go: `github.com/gophish/gophish` — affected >=0 <0.12.0

## Details
This affects the package github.com/gophish/gophish before 0.12.0. The Open Redirect vulnerability exists in the next query parameter. The application uses url.Parse(r.FormValue("next")) to extract path and eventually redirect user to a relative URL, but if next parameter starts with multiple backslashes like \\\\\\example.com, browser will redirect user to http://example.com.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25295
- https://github.com/gophish/gophish/pull/2262
- https://github.com/gophish/gophish/commit/2a452bda89ffdb85f929fa78290bce1f456881dc
- https://github.com/gophish/gophish
- https://github.com/gophish/gophish/releases/tag/v0.12.0
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGOPHISHGOPHISH-2404177
