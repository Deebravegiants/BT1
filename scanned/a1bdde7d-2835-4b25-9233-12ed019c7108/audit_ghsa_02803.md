# [H] github.com/tidwall/gjson Vulnerable to REDoS attack

## Summary
Severity: High
Advisory: GHSA-ppj4-34rq-v8j9
CVE: CVE-2021-42836
CWE: CWE-1333, CWE-400, CWE-697
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-25
Source: https://github.com/advisories/GHSA-ppj4-34rq-v8j9
Type: github-advisory

## Affected
- Go: `github.com/tidwall/gjson` — affected >=0 <1.9.3

## Details
GJSON is a Go package that provides a fast and simple way to get values from a json document. GJSON before 1.9.3 allows a ReDoS (regular expression denial of service) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42836
- https://github.com/tidwall/gjson/issues/236
- https://github.com/tidwall/gjson/issues/237
- https://github.com/tidwall/gjson/commit/590010fdac311cc8990ef5c97448d4fec8f29944
- https://github.com/tidwall/gjson/commit/77a57fda87dca6d0d7d4627d512a630f89a91c96
- https://github.com/tidwall/gjson
- https://github.com/tidwall/gjson/compare/v1.9.2...v1.9.3
- https://pkg.go.dev/vuln/GO-2021-0265
