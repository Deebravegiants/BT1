# [M] Fulcio is vulnerable to Server-Side Request Forgery (SSRF) via MetaIssuer Regex Bypass

## Summary
Severity: Medium
Advisory: GHSA-59jp-pj84-45mr
CVE: CVE-2026-22772
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-59jp-pj84-45mr
Type: github-advisory

## Affected
- Go: `github.com/sigstore/fulcio` — affected >=0 <1.8.5

## Details
# Security Disclosure: SSRF via MetaIssuer Regex Bypass

## Summary

Fulcio's `metaRegex()` function uses unanchored regex, allowing attackers to bypass MetaIssuer URL validation and trigger SSRF to arbitrary internal services.

Since the SSRF only can trigger GET requests, the request cannot mutate state. The response from the GET request is not returned to the caller so data exfiltration is not possible. A malicious actor could attempt to probe an internal network through [Blind SSRF](https://portswigger.net/web-security/ssrf/blind).

## Impact

- SSRF to cloud metadata (169.254.169.254)
- SSRF to internal Kubernetes APIs
- SSRF to any service accessible from Fulcio's network
- Affects ALL deployments using MetaIssuers

## Patches

Upgrade to v1.8.5.

## Workarounds

None. If anchors are included in the meta issuer configuration URL, they will be escaped before the regular expression is compiled, not making this a sufficient mitigation. Deployments must upgrade to the latest Fulcio release v1.8.5.

## Affected Code

**File**: `pkg/config/config.go`  
**Function**: `metaRegex()` (lines 143-156)

```go
func metaRegex(issuer string) (*regexp.Regexp, error) {
    quoted := regexp.QuoteMeta(issuer)
    replaced := strings.ReplaceAll(quoted, regexp.QuoteMeta("*"), "[-_a-zA-Z0-9]+")
    return regexp.Compile(replaced)  // Missing ^ and $ anchors
}
```

## The Bug

The regex has no `^` (start) or `$` (end) anchors. Go's `regexp.MatchString()` does substring matching, so:

```
Pattern:  https://oidc.eks.*.amazonaws.com/id/*
Regex:    https://oidc\.eks\.[-_a-zA-Z0-9]+\.amazonaws\.com/id/[-_a-zA-Z0-9]+

Input:    https://attacker.com/x/https://oidc.eks.foo.amazonaws.com/id/bar
Result:   MATCHES (substring found)
```

## Exploit

1. Attacker sends JWT with `iss` claim: `https://attacker.com/path/https://oidc.eks.x.amazonaws.com/id/y`
2. Fulcio's `GetIssuer()` matches this against MetaIssuer patterns
3. Unanchored regex matches the embedded pattern as substring
4. Fulcio calls `oidc.NewProvider()` with attacker's URL
5. HTTP request goes to `attacker.com`, not `amazonaws.com`
6. Attacker returns OIDC discovery with `jwks_uri` pointing to internal service
7. Fulcio fetches from internal service → SSRF

## References
- https://github.com/sigstore/fulcio/security/advisories/GHSA-59jp-pj84-45mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-22772
- https://github.com/sigstore/fulcio/commit/eaae2f2be56df9dea5f9b439ec81bedae4c0978d
- https://github.com/sigstore/fulcio
