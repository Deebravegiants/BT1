# [M] Denial of service via malicious preflight requests in github.com/rs/cors

## Summary
Severity: Medium
Advisory: GHSA-mh55-gqvf-xfwm
CVE: CVE-2025-47908
CWE: CWE-770
Ecosystem: Go
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-mh55-gqvf-xfwm
Type: github-advisory

## Affected
- Go: `github.com/rs/cors` — affected >=1.9.0 <1.11.0

## Details
Middleware causes a prohibitive amount of heap allocations when processing malicious preflight requests that include a Access-Control-Request-Headers (ACRH) header whose value contains many commas. This behavior can be abused by attackers to produce undue load on the middleware/server as an attempt to cause a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47908
- https://github.com/rs/cors/issues/170
- https://github.com/rs/cors/pull/171
- https://github.com/rs/cors/commit/4c32059b2756926619f6bf70281b91be7b5dddb2
- https://github.com/rs/cors
- https://pkg.go.dev/vuln/GO-2024-2883
