# [M] graphql-php is affected by a Denial of Service via quadratic complexity in OverlappingFieldsCanBeMerged validation

## Summary
Severity: Medium
Advisory: GHSA-68jq-c3rv-pcrr
CVE: CVE-2026-40476
CWE: CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-68jq-c3rv-pcrr
Type: github-advisory

## Affected
- Packagist: `webonyx/graphql-php` — affected >=0 <15.31.5

## Details
The `OverlappingFieldsCanBeMerged` validation rule exhibits quadratic time complexity when processing queries with many repeated fields sharing the same response name. An attacker can send a crafted query like `{ hello hello hello ... }` with thousands of repeated fields, causing excessive CPU usage during validation before execution begins.

This is not mitigated by existing QueryDepth or QueryComplexity rules.

**Observed impact (tested on v15.31.4):**
- 1000 fields: ~0.6s
- 2000 fields: ~2.4s
- 3000 fields: ~5.3s
- 5000 fields: request timeout (>20s)

**Root cause:** `collectConflictsWithin()` performs O(n²) pairwise comparisons of all fields with the same response name. For identical repeated fields, every comparison returns "no conflict" but the quadratic iteration count causes resource exhaustion.

**Fix:** Deduplicate structurally identical fields before pairwise comparison, reducing the complexity from O(n²) to O(u²) where u is the number of unique field signatures (typically 1 for this attack pattern).

**Credit:** Ashwak N (ashwakn04@gmail.com)

## References
- https://github.com/webonyx/graphql-php/security/advisories/GHSA-68jq-c3rv-pcrr
- https://nvd.nist.gov/vuln/detail/CVE-2026-40476
- https://github.com/webonyx/graphql-php
- https://github.com/webonyx/graphql-php/releases/tag/v15.31.5
