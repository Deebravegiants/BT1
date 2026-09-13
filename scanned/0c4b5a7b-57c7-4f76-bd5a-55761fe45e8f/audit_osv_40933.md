# [H] Capgo - Unauthenticated API Key Generation via Client-Side Parameter Manipulation

## Summary
Severity: High
Advisory: CVE-2026-56237
Aliases: GHSA-22w2-mx2h-4fr7
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56237
Type: osv

## Details
Capgo before 12.128.2 contains a broken authentication vulnerability in its API key generation mechanism. API keys are exposed in frontend requests, and the backend fails to validate that keys are securely generated and bound to the authenticated user. An attacker can tamper with the API key parameter in the generation request and supply arbitrary values, generating custom API keys without proper authorization, which can lead to unauthorized access to protected endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56237.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-22w2-mx2h-4fr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-56237
- https://www.vulncheck.com/advisories/capgo-unauthenticated-api-key-generation-via-client-side-parameter-manipulation
