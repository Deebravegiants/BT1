# [H] free5GC UDM vulnerable to null byte injection in URL path parameters causing 500 Internal Server Error

## Summary
Severity: High
Advisory: GHSA-p9hg-pq3q-v9gv
CVE: CVE-2026-33191
CWE: CWE-158, CWE-248
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-p9hg-pq3q-v9gv
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udm` — affected >=0 <1.4.2

## Details
**Impact**  
This is an Improper Input Validation vulnerability with Denial of Service and Injection implications.  
- **Security Impact**: A remote attacker can inject null bytes (URL-encoded as `%00`) into the `supi` path parameter of the UDM's Nudm_SubscriberDataManagement API. This causes URL parsing failure in Go's `net/url` package with the error "invalid control character in URL", resulting in a 500 Internal Server Error. This null byte injection vulnerability can be exploited for denial of service attacks.  
- **Functional Impact**: When the `supi` parameter contains null characters, the UDM attempts to construct a URL for UDR that includes these control characters. Go's URL parser rejects them, causing the request to fail with 500 instead of properly validating input and returning 400 Bad Request.  
- **Affected Parties**: All deployments of free5GC v4.0.1 using the UDM Nudm_SDM service with endpoints that include path parameters (e.g., `/nudm-sdm/v2/{supi}/am-data`).

**Patches**  
Yes, the issue has been patched.  
The fix is implemented in PR free5gc/udm#79.  
Users should upgrade to the next release of free5GC that includes this commit.

**Workarounds**  
There is no direct workaround at the application level. The recommendation is to apply the provided patch or implement API gateway-level validation to reject requests containing null bytes in path parameters before they reach UDM.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-p9hg-pq3q-v9gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33191
- https://github.com/free5gc/udm/pull/79
- https://github.com/free5gc/udm/commit/88de9fa74a1b3f3522e53b4cfa2d184712ffa4ee
- https://github.com/free5gc/udm
