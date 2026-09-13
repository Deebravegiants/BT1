# [M] free5GC UDM incorrectly returns 500 for empty supi path parameter in DELETE sdm-subscriptions request

## Summary
Severity: Medium
Advisory: GHSA-958m-gxmc-mccm
CVE: CVE-2026-33065
CWE: CWE-209
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-958m-gxmc-mccm
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udm` — affected >=0 <1.4.2

## Details
**Impact**  
This is an Improper Error Handling  vulnerability with Information Exposure implications.  
- **Security Impact**: The UDM incorrectly converts a downstream 400 Bad Request (from UDR) into a 500 Internal Server Error when handling DELETE requests with an empty `supi` path parameter. This leaks internal error handling behavior and makes it difficult for clients to distinguish between client-side errors and server-side failures.  
- **Functional Impact**: When a client sends a DELETE request with an empty `supi` (e.g., double slashes `//` in URL path), the UDM forwards the malformed request to UDR, which correctly returns 400. However, UDM propagates this as 500 SYSTEM_FAILURE instead of returning the appropriate 400 error to the client. This violates REST API best practices for DELETE operations.  
- **Affected Parties**: All deployments of free5GC v4.0.1 using the UDM Nudm_SDM service with DELETE operations on sdm-subscriptions endpoint.

**Patches**  
Yes, the issue has been patched.  
The fix is implemented in PR free5gc/udm#79.  
Users should upgrade to the next release of free5GC that includes this commit.

**Workarounds**  
There is no direct workaround at the application level. The recommendation is to apply the provided patch or implement API gateway-level validation to reject DELETE requests with empty path parameters before they reach UDM.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-958m-gxmc-mccm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33065
- https://github.com/free5gc/free5gc/issues/783
- https://github.com/free5gc/udm/pull/79
- https://github.com/free5gc/udm/commit/88de9fa74a1b3f3522e53b4cfa2d184712ffa4ee
- https://github.com/free5gc/free5gc
