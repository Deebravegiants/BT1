# [H] Golang Facebook Thrift servers vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-w3r9-r9w7-8h48
CVE: CVE-2019-11939
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w3r9-r9w7-8h48
Type: github-advisory

## Affected
- Go: `github.com/facebook/fbthrift` — affected >=0 <0.31.1-0.20200311080807-483ed864d69f

## Details
Golang Facebook Thrift servers would not error upon receiving messages declaring containers of sizes larger than the payload. As a result, malicious clients could send short messages which would result in a large memory allocation, potentially leading to denial of service. This issue affects Facebook Thrift prior to v2020.03.16.00.

### Specific Go Packages Affected
github.com/facebook/fbthrift/thrift/lib/go/thrift

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11939
- https://github.com/facebook/fbthrift/commit/483ed864d69f307e9e3b9dadec048216100c0757
- https://github.com/facebook/fbthrift
- https://pkg.go.dev/vuln/GO-2021-0082
- https://www.facebook.com/security/advisories/cve-2019-11939
