# [M] Snipe-IT's API Location Creation Bypasses FMCS Parent-Child Company Boundary Validation

## Summary
Severity: Medium
Advisory: GHSA-8w8c-8mx9-52cw
CVE: CVE-2026-55472
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-8w8c-8mx9-52cw
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
When Full Multiple Companies Support and scope_locations_fmcs are both enabled, the API endpoint for creating locations can still create a child location under a parent location from a different company. The code detects the invalid parent/child company mismatch, but it appears not to return immediately, so the request continues and the record is still saved. The equivalent Web flow correctly rejects the same relationship.

This breaks the expected company-boundary enforcement for location hierarchies under FMCS. It allows cross-company parent/child relationships to be inserted into the location tree, which can affect hierarchy integrity, downstream business logic, and the consistency of company isolation between the Web and API interfaces.

### Patches
Patched in https://github.com/grokability/snipe-it/commit/9a8cbd6e00613a726b639a97a1da71b3c54f9489

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-8w8c-8mx9-52cw
- https://nvd.nist.gov/vuln/detail/CVE-2026-55472
- https://github.com/grokability/snipe-it/commit/9a8cbd6e00613a726b639a97a1da71b3c54f9489
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
