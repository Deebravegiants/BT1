# [M] CVE-2025-1386- Query smuggling in ch-go library

## Summary
Severity: Medium
Advisory: GHSA-m454-3xv7-qj85
CVE: CVE-2025-1386
CWE: CWE-444
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-12
Source: https://github.com/advisories/GHSA-m454-3xv7-qj85
Type: github-advisory

## Affected
- Go: `github.com/ClickHouse/ch-go` — affected >=0 <0.65.0

## Details
### Impact

When using the ch-go library, under a specific condition when the query includes a large, uncompressed malicious external data, it is possible for an attacker in control of such data to smuggle another query packet into the connection stream.

### Patches

If you are using ch-go library, we recommend you to update to at least version 0.65.0.

### Credit

This issue was found by lixts and reported through our bugcrowd program.

## References
- https://github.com/ClickHouse/ch-go/security/advisories/GHSA-m454-3xv7-qj85
- https://nvd.nist.gov/vuln/detail/CVE-2025-1386
- https://github.com/ClickHouse/ch-go/commit/0e835663df32b09b828528c07a5507686e6d975e
- https://github.com/ClickHouse/ch-go
- https://pkg.go.dev/vuln/GO-2025-3603
