# [H] free5GC UDM incorrectly returns 500 for empty supi path parameter in PATCH sdm-subscriptions reques

## Summary
Severity: High
Advisory: GHSA-5rvc-5cwx-g5x8
CVE: CVE-2026-33192
CWE: CWE-209
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-5rvc-5cwx-g5x8
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udm` — affected >=0 <1.4.2

## Details
**Impact**  
This is an Improper Error Handling vulnerability with Information Exposure implications, combined with an HTTP Method Translation issue.  
- **Security Impact**: The UDM incorrectly converts a downstream 400 Bad Request (from UDR) into a 500 Internal Server Error when handling PATCH requests with an empty `supi` path parameter. Additionally, the UDM incorrectly translates the PATCH method to PUT when forwarding to UDR, indicating a deeper architectural issue. This leaks internal error handling behavior and makes it difficult for clients to distinguish between client-side errors and server-side failures.  
- **Functional Impact**: When a client sends a PATCH request with an empty `supi` (e.g., double slashes `//` in URL path), the UDM forwards a PUT request to UDR with the malformed path, which correctly returns 400. However, UDM propagates this as 500 SYSTEM_FAILURE instead of returning the appropriate 400 error to the client. This violates REST API best practices for PATCH operations and may indicate improper HTTP method handling.  
- **Affected Parties**: All deployments of free5GC v4.0.1 using the UDM Nudm_SDM service with PATCH operations on sdm-subscriptions endpoint.

**Patches**  
Yes, the issue has been patched.  
The fix is implemented in PR free5gc/udm#79.  
Users should upgrade to the next release of free5GC that includes this commit.

**Workarounds**  
There is no direct workaround at the application level. The recommendation is to apply the provided patch or implement API gateway-level validation to reject PATCH requests with empty path parameters before they reach UDM.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-5rvc-5cwx-g5x8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33192
- https://github.com/free5gc/free5gc/issues/784
- https://github.com/free5gc/udm/pull/79
- https://github.com/free5gc/udm
