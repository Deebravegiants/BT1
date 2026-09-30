# [M] pymonocypher: Potential heap buffer overflow on nb_blocks in argon2i_32 when provided buffer is too small

## Summary
Severity: Medium
Advisory: GHSA-8f95-v3jq-cj86
CVE: CVE-2026-53720
CWE: CWE-122, CWE-1284, CWE-787
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-8f95-v3jq-cj86
Type: github-advisory

## Affected
- PyPI: `pymonocypher` — affected >=0 <4.0.2.8

## Details
### Impact
The argon2i_32 implementation does not check the nb_blocks size.  If the caller does not provide a sufficiently large buffer based on the API contract, then argon2i_32 will write past the end of the buffer and possibly corrupt the heap.

### Patches
Fixed in 4.0.2.8, which now verifies that nb_blocks is large enough.  See [90ff5b1](https://github.com/jetperch/pymonocypher/commit/90ff5b13b13b5673c372e188f482d8c172e6ab86).

### Workarounds
Provide a correctly sized nb_blocks buffer.

pymonocypher thanks Haris (hextheshadow) for the vulnerability report, details, and recommended fix.

## References
- https://github.com/jetperch/pymonocypher/security/advisories/GHSA-8f95-v3jq-cj86
- https://github.com/jetperch/pymonocypher/commit/90ff5b13b13b5673c372e188f482d8c172e6ab86
- https://github.com/jetperch/pymonocypher
