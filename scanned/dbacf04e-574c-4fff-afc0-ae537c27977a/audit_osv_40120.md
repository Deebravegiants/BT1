# [M] CodexBar < 0.33.0 Credential Leakage via HTTP Redirect

## Summary
Severity: Medium
Advisory: CVE-2026-49949
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-49949
Type: osv

## Details
CodexBar before 0.33.0 contains a credential forwarding vulnerability that allows network-adjacent attackers to intercept sensitive credentials by issuing cross-origin or HTTP-downgrade redirects to the shared ProviderHTTPClient transport. Attackers can redirect credentialed provider requests carrying browser cookies, bearer tokens, or API keys to an unintended host, port, or plaintext HTTP destination to capture those credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49949.json
- https://github.com/steipete/CodexBar/releases/tag/v0.33.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-49949
- https://www.vulncheck.com/advisories/codexbar-credential-leakage-via-http-redirect
- https://github.com/steipete/CodexBar/pull/1237
- https://github.com/steipete/CodexBar/commit/08c171b6b487654a0eb188494fa24bd1c4272a2e
- https://github.com/steipete/CodexBar
