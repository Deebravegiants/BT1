# [M] DoS in go-jose Parsing

## Summary
Severity: Medium
Advisory: GHSA-c6gw-w398-hv78
CVE: CVE-2025-27144
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-c6gw-w398-hv78
Type: github-advisory

## Affected
- Go: `github.com/go-jose/go-jose/v4` — affected >=0 <4.0.5
- Go: `github.com/go-jose/go-jose/v3` — affected >=0 <3.0.4
- Go: `github.com/go-jose/go-jose` — affected >=0 <3.0.4

## Details
### Impact
When parsing compact JWS or JWE input, go-jose could use excessive memory. The code used strings.Split(token, ".") to split JWT tokens, which is vulnerable to excessive memory consumption when processing maliciously crafted tokens with a large number of '.' characters.  An attacker could exploit this by sending numerous malformed tokens, leading to memory exhaustion and a Denial of Service.

### Patches
Version 4.0.5 fixes this issue

### Workarounds
Applications could pre-validate payloads passed to go-jose do not contain an excessive number of '.' characters.

### References
This is the same sort of issue as in the golang.org/x/oauth2/jws package as CVE-2025-22868 and Go issue https://go.dev/issue/71490.

## References
- https://github.com/go-jose/go-jose/security/advisories/GHSA-c6gw-w398-hv78
- https://nvd.nist.gov/vuln/detail/CVE-2025-27144
- https://github.com/golang/go/issues/71490
- https://github.com/go-jose/go-jose/commit/99b346cec4e86d102284642c5dcbe9bb0cacfc22
- https://github.com/go-jose/go-jose
- https://github.com/go-jose/go-jose/releases/tag/v4.0.5
- https://go.dev/issue/71490
