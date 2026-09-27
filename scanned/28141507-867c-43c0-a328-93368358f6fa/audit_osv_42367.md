# [H] MaxKey 4.1.12 DefaultRedirectResolver OAuth Authorization Code Theft

## Summary
Severity: High
Advisory: CVE-2026-67345
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67345
Type: osv

## Details
MaxKey through 4.1.12, fixed in commit ddbb72f, contains an insufficient redirect URI validation vulnerability in DefaultRedirectResolver.hostMatches() that allows remote attackers to hijack OAuth 2.0 authorization codes by supplying a crafted redirect_uri whose hostname suffix matches a registered URI without proper dot-boundary anchoring. Attackers who control a domain ending with the registered redirect URI hostname can social-engineer victims into clicking a crafted authorization URL, causing the authorization code to be issued to the attacker-controlled URI and exchanged for an access token granting access to the victim's identity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67345.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67345
- https://www.vulncheck.com/advisories/maxkey-defaultredirectresolver-oauth-authorization-code-theft
- https://github.com/dromara/MaxKey/issues/269
- https://github.com/dromara/MaxKey/commit/ddbb72fb24ab8e66aa422fb14b1177330bcffb45
- https://github.com/dromara/MaxKey
