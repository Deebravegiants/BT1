# [H] github.com/pires/go-proxyproto vulnerable to DoS via Connection descriptor exhaustion

## Summary
Severity: High
Advisory: GHSA-xcf7-q56x-78gh
CVE: CVE-2021-23409
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-xcf7-q56x-78gh
Type: github-advisory

## Affected
- Go: `github.com/pires/go-proxyproto` — affected >=0 <0.6.1

## Details
The package `github.com/pires/go-proxyproto` before 0.6.1 is vulnerable to Denial of Service (DoS) via creating connections without the proxy protocol header. While this issue was patched in 0.6.0, the fix introduced additional issues which were subsequently patched in 0.6.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23409
- https://github.com/pires/go-proxyproto/issues/65
- https://github.com/pires/go-proxyproto/issues/75
- https://github.com/pires/go-proxyproto/pull/74
- https://github.com/pires/go-proxyproto/pull/74/commits/cdc63867da24fc609b727231f682670d0d1cd346
- https://github.com/pires/go-proxyproto/pull/76
- https://github.com/pires/go-proxyproto/commit/2e44d7a76a851d66890ab341403253afae5caac2
- https://github.com/pires/go-proxyproto
- https://github.com/pires/go-proxyproto/releases/tag/v0.6.0
- https://github.com/pires/go-proxyproto/releases/tag/v0.6.1
- https://pkg.go.dev/vuln/GO-2022-0233
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMPIRESGOPROXYPROTO-1316439
