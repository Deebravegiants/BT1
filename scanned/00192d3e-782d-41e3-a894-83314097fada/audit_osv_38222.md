# [H] Saleor has a resource exhaustion vulnerability in GraphQL queries

## Summary
Severity: High
Advisory: CVE-2026-35401
Aliases: GHSA-gqqv-xwx3-jj4h
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-35401
Type: osv

## Details
Saleor is an e-commerce platform. From 2.0.0 to before 3.23.0a3, 3.22.47, 3.21.54, and 3.20.118, a malicious actor can include many GraphQL mutations or queries in a single API call using aliases or chaining multiple mutations, resulting in resource exhaustion. This vulnerability is fixed in 3.23.0a3, 3.22.47, 3.21.54, and 3.20.118.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35401.json
- https://github.com/saleor/saleor/security/advisories/GHSA-gqqv-xwx3-jj4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-35401
