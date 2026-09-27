# [C] OpenFlagr contains an authentication bypass vulnerability in the HTTP middleware

## Summary
Severity: Critical
Advisory: GHSA-rwp9-5g7q-73q3
CVE: CVE-2026-0650
CWE: CWE-306, CWE-425
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-rwp9-5g7q-73q3
Type: github-advisory

## Affected
- Go: `github.com/openflagr/flagr` — affected >=0 <0.0.0-20251009103504-fe83dc87aa40

## Details
OpenFlagr versions prior to and including 1.1.18 contain an authentication bypass vulnerability in the HTTP middleware. Due to improper handling of path normalization in the whitelist logic, crafted requests can bypass authentication and access protected API endpoints without valid credentials. Unauthorized access may allow modification of feature flags and export of sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0650
- https://github.com/openflagr/flagr/commit/fe83dc87aa404a57554aa5839ac450f55c203570
- https://dreyand.rs/code%20review/golang/2026/01/03/0day-speedrun-openflagr-less-1118-authentication-bypass
- https://github.com/openflagr/flagr
- https://github.com/openflagr/flagr/releases/tag/1.1.19
- https://www.vulncheck.com/advisories/openflagr-authentication-bypass-via-prefix-whitelist-path-normalization
