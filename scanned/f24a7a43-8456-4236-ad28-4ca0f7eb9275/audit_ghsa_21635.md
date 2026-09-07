# [H] Improper Input Validation and Excessive Iteration in Go Facebook Thrift

## Summary
Severity: High
Advisory: GHSA-x4rg-4545-4w7w
CVE: CVE-2019-3564
CWE: CWE-20, CWE-755, CWE-834
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-x4rg-4545-4w7w
Type: github-advisory

## Affected
- Go: `github.com/facebook/fbthrift` — affected >=0 <0.31.1-0.20190225164308-c461c1bd1a3e

## Details
Go Facebook Thrift servers would not error upon receiving messages with containers of fields of unknown type. As a result, malicious clients could send short messages which would take a long time for the server to parse, potentially leading to denial of service. This issue affects Facebook Thrift prior to v2019.03.04.00.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3564
- https://github.com/facebook/fbthrift/commit/c461c1bd1a3e130b181aa9c854da3030cd4b5156
- https://github.com/facebook/fbthrift
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
- https://pkg.go.dev/vuln/GO-2021-0088
- https://www.facebook.com/security/advisories/cve-2019-3564
