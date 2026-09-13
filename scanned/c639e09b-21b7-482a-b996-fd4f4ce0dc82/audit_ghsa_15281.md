# [M] APM Server vulnerable to Insertion of Sensitive Information into Log File

## Summary
Severity: Medium
Advisory: GHSA-f6cj-4h3g-hwq4
CVE: CVE-2024-37286
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-03
Source: https://github.com/advisories/GHSA-f6cj-4h3g-hwq4
Type: github-advisory

## Affected
- Go: `github.com/elastic/apm-server` — affected >=0 <8.14.0

## Details
APM server logs contain document body from a partially failed bulk index request. For example, in case of unavailable_shards_exception for a specific document, since the ES response line contains the document body, and that APM server logs the ES response line on error, the document is effectively logged.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37286
- https://discuss.elastic.co/t/apm-server-8-14-0-security-update-esa-2024-19/364289
- https://github.com/elastic/apm-server
- https://pkg.go.dev/vuln/GO-2024-3037
