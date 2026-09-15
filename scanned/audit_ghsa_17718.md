# [M] OpenFGA Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-32q6-rr98-cjqv
CVE: CVE-2024-56323
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-01-13
Source: https://github.com/advisories/GHSA-32q6-rr98-cjqv
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=1.3.8 <1.8.3

## Details
### Overview
OpenFGA v1.3.8 to v1.8.2 (Helm chart openfga-0.1.38 to openfga-0.2.19, docker v1.3.8 to v.1.8.2) are vulnerable to authorization bypass when certain Check and ListObject calls are executed.

### Am I Affected?
You are affected by this authorization bypass vulnerability if you are using OpenFGA v1.3.8 to v1.8.2, specifically under the following conditions: 
1. Calling Check API or ListObjects with a model that uses [conditions](https://openfga.dev/docs/modeling/conditions), and 
2. OpenFGA is configured with caching enabled (`OPENFGA_CHECK_QUERY_CACHE_ENABLED`), and 
3. Check API call or ListObjects API calls contain [contextual tuples](https://openfga.dev/docs/concepts#what-are-contextual-tuples) that include conditions.

### Fix
Upgrade to v1.8.3. This upgrade is backwards compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-32q6-rr98-cjqv
- https://nvd.nist.gov/vuln/detail/CVE-2024-56323
- https://github.com/openfga/openfga
- https://pkg.go.dev/vuln/GO-2025-3384
