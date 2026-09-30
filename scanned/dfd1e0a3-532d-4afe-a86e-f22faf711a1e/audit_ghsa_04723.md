# [C] googleapis/mcp-toolbox: authentication bypass vulnerability in the generic opaque token validation path (validateOpaqueToken)

## Summary
Severity: Critical
Advisory: GHSA-wcpr-6g7x-p44r
CVE: CVE-2026-11718
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-wcpr-6g7x-p44r
Type: github-advisory

## Affected
- Go: `github.com/googleapis/mcp-toolbox` — affected >=0 <1.4.0

## Details
An authentication bypass vulnerability exists in the generic opaque token validation path (validateOpaqueToken) of googleapis/mcp-toolbox.

When the toolbox validates an opaque token via an OAuth 2.0 introspection endpoint (RFC 7662), it decodes the response into an introspectResp struct. However, the subsequent claim-checking logic (validateClaims) evaluates the issuer condition as if a.issuer != "" && iss != "". If the external OAuth provider's introspection response omits the optional iss (issuer) field completely, the variable iss defaults to an empty string. This causes the conditional block to evaluate to false and be skipped silently. Consequently, the application accepts tokens issued by unauthorized or unintended third-party identity providers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11718
- https://github.com/googleapis/mcp-toolbox/pull/3360
- https://github.com/googleapis/mcp-toolbox
