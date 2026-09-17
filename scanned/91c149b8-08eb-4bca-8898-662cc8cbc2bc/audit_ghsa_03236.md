# [M] Redirect URL matching ignores character casing

## Summary
Severity: Medium
Advisory: GHSA-grfp-q2mm-hfp6
CVE: CVE-2020-15234
CWE: CWE-178, CWE-20, CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-grfp-q2mm-hfp6
Type: github-advisory

## Affected
- Go: `github.com/ory/fosite` — affected >=0 <0.34.1

## Details
### Impact

Before version v0.34.1, the OAuth 2.0 Client's registered redirect URLs and the redirect URL provided at the OAuth2 Authorization Endpoint where compared using `strings.ToLower` while they should have been compared with a simple string match:

1. Registering a client with allowed redirect URL `https://example.com/callback`
2. Performing OAuth2 flow and requesting redirect URL `https://example.com/CALLBACK`
3. Instead of an error (invalid redirect URL), the browser is redirected to `https://example.com/CALLBACK` with a potentially successful OAuth2 response, depending on the state of the overall OAuth2 flow (the user might still deny the request for example).

## References
- https://github.com/ory/fosite/security/advisories/GHSA-grfp-q2mm-hfp6
- https://nvd.nist.gov/vuln/detail/CVE-2020-15234
- https://github.com/ory/fosite/commit/cdee51ebe721bfc8acca0fd0b86b030ca70867bf
- https://github.com/ory/fosite
