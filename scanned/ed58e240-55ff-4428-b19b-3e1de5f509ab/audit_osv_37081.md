# [M] Phishing Club has Authenticated Blind SQL Injection in GetOrphaned Recipient Listing

## Summary
Severity: Medium
Advisory: CVE-2026-28226
Aliases: GHSA-4r69-4qff-ccj3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-28226
Type: osv

## Details
Phishing Club is a phishing simulation and man-in-the-middle framework. Prior to version 1.30.2, an authenticated SQL injection vulnerability exists in the GetOrphaned recipient listing endpoint in versions prior to v1.30.2. The endpoint constructs a raw SQL query and concatenates the user-controlled sortBy value directly into the ORDER BY clause without allowlist validation. Because unknown values are silently passed through `RemapOrderBy()`, an authenticated attacker can inject SQL expressions into the `ORDER BY` clause. This issue was patched in v1.30.2 by validating the order-by column against an allowlist and clearing unknown mappings.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28226.json
- https://github.com/phishingclub/phishingclub/security/advisories/GHSA-4r69-4qff-ccj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-28226
- https://github.com/phishingclub/phishingclub/commit/c7e666da9a71cd519f317cbf67ade10068a33070
