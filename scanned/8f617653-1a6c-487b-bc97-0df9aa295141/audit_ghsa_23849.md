# [H] ProxyScotch is vulnerable to a server-side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-5hjh-c26m-xw8w
CVE: CVE-2022-25850
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-5hjh-c26m-xw8w
Type: github-advisory

## Affected
- Go: `github.com/hoppscotch/proxyscotch` — affected >=0 <1.0.0

## Details
ProxyScotch is a simple proxy server created for hoppscotch.io. The package github.com/hoppscotch/proxyscotch before 1.0.0 are vulnerable to Server-side Request Forgery (SSRF) when interceptor mode is set to proxy. It occurs when an HTTP request is made by a backend server to an untrusted URL submitted by a user. It leads to a leakage of sensitive information from the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25850
- https://github.com/hoppscotch/proxyscotch/commit/de67380f62f907f201d75854b76024ba4885fab7
- https://github.com/hoppscotch/proxyscotch
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMHOPPSCOTCHPROXYSCOTCH-2435228
