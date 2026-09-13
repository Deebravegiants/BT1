# [M] OpenFGA has cache-key delimiter injection in shared-iterator and v2 iterator that caches enables intra-store authorization-decision poisoning

## Summary
Severity: Medium
Advisory: GHSA-8396-jffm-qx4w
CVE: CVE-2026-48096
CWE: CWE-345, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-8396-jffm-qx4w
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <1.16.0

## Details
### Description
In OpenFGA, when iterator caching is enabled, two distinct check requests can produce the same cache key, leading to OpenFGA reusing an earlier cached result for a subsequent request.

### Preconditions
This applies if the following preconditions are present:

- FGA runs with SharedIteratorCache enabled,
- FGA runs with ListObjectsIteratorCache enabled.

### Fix
Upgrade to version 1.16.0 or greater.

### Acknowledgements
OpenFGA would like to thank @j4xT for the discovery and the detailed report.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-8396-jffm-qx4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-48096
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v1.16.0
