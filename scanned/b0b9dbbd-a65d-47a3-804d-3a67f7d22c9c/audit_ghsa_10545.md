# [H] zrok: Unauthenticated DoS via unbounded memory allocation in striped session cookie parsing

## Summary
Severity: High
Advisory: GHSA-cpf9-ph2j-ccr9
CVE: CVE-2026-40303
CWE: CWE-400, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-cpf9-ph2j-ccr9
Type: github-advisory

## Affected
- Go: `github.com/openziti/zrok` — affected >=0
- Go: `github.com/openziti/zrok/v2` — affected >=0 <2.0.1

## Details
**Summary**
endpoints.GetSessionCookie parses an attacker-supplied cookie chunk count and calls make([]string, count) with no upper bound before any token validation occurs. The function is reached on every request to an OAuth-protected proxy share, allowing an unauthenticated remote attacker to trigger gigabyte-scale heap allocations per request, leading to process-level OOM termination or repeated goroutine panics. Both publicProxy and dynamicProxy are affected.

- Attack Vector: Network — exploitable via a single HTTP request with a crafted Cookie header.
- Attack Complexity: Low — no preconditions or chaining required; the attacker only needs to know the cookie name (publicly derivable from any OAuth redirect).
- Privileges Required: None — reached before JWT validation or any authentication check.
- User Interaction: None.
- Scope: Unchanged — impact is confined to the affected proxy process.
- Confidentiality Impact: None.
- Integrity Impact: None.

Availability Impact: High — sustained or concurrent requests cause OOM process termination, taking down the proxy for all users of all shares it serves.

**Affected Components**
- endpoints/oauthCookies.go — GetSessionCookie (line 81)
- endpoints/publicProxy/authOAuth.go — handleOAuth (line 50) — call site, pre-auth
- endpoints/dynamicProxy/cookies.go — getSessionCookie (line 29) — call site

## References
- https://github.com/openziti/zrok/security/advisories/GHSA-cpf9-ph2j-ccr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40303
- https://github.com/openziti/zrok
- https://github.com/openziti/zrok/releases/tag/v2.0.1
