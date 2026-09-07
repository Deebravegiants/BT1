# [C] gorilla/handlers may allow requester to bypass expected behavior of the Same Origin Policy

## Summary
Severity: Critical
Advisory: GHSA-jcr6-mmjj-pchw
CVE: CVE-2017-20146
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-jcr6-mmjj-pchw
Type: github-advisory

## Affected
- Go: `github.com/gorilla/handlers` — affected >=0 <1.3.0

## Details
Usage of the CORS handler may apply improper CORS headers, allowing the requester to explicitly control the value of the Access-Control-Allow-Origin header, which bypasses the expected behavior of the Same Origin Policy.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20146
- https://github.com/gorilla/handlers/pull/116
- https://github.com/gorilla/handlers/commit/90663712d74cb411cbef281bc1e08c19d1a76145
- https://github.com/gorilla/handlers
- https://pkg.go.dev/vuln/GO-2020-0020
