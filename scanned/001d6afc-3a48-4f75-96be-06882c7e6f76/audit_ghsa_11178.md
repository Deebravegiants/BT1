# [M] OpenFGA has an Authorization Bypass through cached keys

## Summary
Severity: Medium
Advisory: GHSA-h6c8-cww8-35hf
CVE: CVE-2026-33729
CWE: CWE-1289, CWE-20, CWE-345
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-h6c8-cww8-35hf
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <1.13.1

## Details
### Description
In OpenFGA, under specific conditions, models using conditions with caching enabled can result in two different check requests producing the same cache key. This can result in OpenFGA reusing an earlier cached result for a different request.

### Am I Affected?
Users are affected if the following preconditions are met:
1. The model has relations which rely on condition evaluation.
1. Caching is enabled.

### Fix
Upgrade to OpenFGA v1.13.1.

### Acknowledgement
OpenFGA would like to thank @Amemoyoi for the discovery and responsible disclosure.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-h6c8-cww8-35hf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33729
- https://github.com/openfga/openfga/commit/049b50ccd2cc7e163bd897f3d17a7b859ad146f8
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v1.13.1
