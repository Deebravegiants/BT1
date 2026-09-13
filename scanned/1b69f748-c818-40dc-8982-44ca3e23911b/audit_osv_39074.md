# [M] CodexBar < 0.32.0 Session Cookie Exposure via HTTP Redirect

## Summary
Severity: Medium
Advisory: CVE-2026-43625
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-43625
Type: osv

## Details
CodexBar prior to 0.32.0 contains a session cookie leakage vulnerability that allows network attackers to intercept imported browser session cookies by exploiting improper redirect handling for Amp and Ollama provider sessions. Attackers can position themselves on the network path to receive cleartext HTTP requests carrying imported session cookies when a provider-controlled redirect target issues a redirect to a cleartext HTTP endpoint within the same provider domain.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43625.json
- https://github.com/steipete/CodexBar/releases/tag/v0.32.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-43625
- https://www.vulncheck.com/advisories/codexbar-session-cookie-exposure-via-http-redirect
- https://github.com/steipete/CodexBar/pull/1226
- https://github.com/steipete/CodexBar/commit/cdd7e347c1cf616615f18aa2ac52ba2ec9cab332
- https://github.com/steipete/CodexBar
