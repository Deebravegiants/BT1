# [M] zrok: Reflected XSS in GitHub OAuth callback via unsanitized refreshInterval error rendering

## Summary
Severity: Medium
Advisory: GHSA-4fxq-2x3x-6xqx
CVE: CVE-2026-40302
CWE: CWE-116, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-4fxq-2x3x-6xqx
Type: github-advisory

## Affected
- Go: `github.com/openziti/zrok` — affected >=0
- Go: `github.com/openziti/zrok/v2` — affected >=0 <2.0.1

## Details
**Summary**
The proxyUi template engine uses Go's text/template (which performs no HTML escaping) instead of html/template. The GitHub OAuth callback handlers in both publicProxy and dynamicProxy embed the attacker-controlled refreshInterval query parameter verbatim into an error message when time.ParseDuration fails, and render that error unescaped into HTML. An attacker can deliver a crafted login URL to a victim; after the victim completes the GitHub OAuth flow, the callback page executes arbitrary JavaScript in the OAuth server's origin.

- Attack Vector: Network — the attack is delivered as a crafted URL over the internet.
- Attack Complexity: Low — no race conditions or special environment prerequisites.
- Privileges Required: None — the attacker needs no account on the zrok instance.
- User Interaction: Required — the victim must click the crafted link and complete the GitHub OAuth flow.
- Scope: Changed — the injected script executes in the OAuth server's origin, not the victim's share origin.
- Confidentiality Impact: Low — the script runs in the OAuth server origin after a failed flow; no session cookie is set at this point, limiting what can be exfiltrated to what is visible in the DOM and what can be requested from the OAuth server.
- Integrity Impact: Low — the script can initiate new OAuth flows or submit forms on behalf of the victim in the OAuth server origin.
- Availability Impact: None.

**Affected Components**

- endpoints/proxyUi/template.go — init() / WriteTemplate (lines 8, 18, 99) — text/template used for HTML rendering
- endpoints/proxyUi/template.html — line 119 — {{ .Error }} in HTML without escaping
- endpoints/publicProxy/providerGithub.go — login callback closure (lines 93, 128, 130)
- endpoints/dynamicProxy/providerGithub.go — loginHandler() (lines 110, 146, 148)

## References
- https://github.com/openziti/zrok/security/advisories/GHSA-4fxq-2x3x-6xqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40302
- https://github.com/openziti/zrok
- https://github.com/openziti/zrok/releases/tag/v2.0.1
