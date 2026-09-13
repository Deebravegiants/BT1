# [M] OpenAM Reflected XSS in the OAuth2/OIDC `wap` consent page

## Summary
Severity: Medium
Advisory: GHSA-vqxv-6xrh-49cp
CVE: CVE-2026-62280
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-vqxv-6xrh-49cp
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-oauth2` — affected >=13.0.0 <16.1.2

## Details
### Description
The OAuth2/OIDC consent page rendered for `display=wap` authorize requests reflected several request-derived values into the HTML response without escaping. An attacker who induces a user with an active OpenAM session to follow a crafted authorize link can execute arbitrary JavaScript in the OpenAM origin.

This is the same vulnerability class as CVE-2026-44203; that fix did not cover this code path.

### Impact
Arbitrary JavaScript execution in the OpenAM origin in the victim's authenticated context — enabling session/cookie theft, CSRF-token exfiltration, and actions on behalf of the victim, up to administrative takeover if the victim is an administrator. Reachable on any deployment with at least one registered OAuth2 client; no attacker-controlled client and no special configuration required.

### Mitigation
- Upgrade to 16.1.2 (or later).
- Until then, restrict/limit access to the OAuth2 authorize endpoint and treat unsolicited `display=wap` authorize links as untrusted.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-vqxv-6xrh-49cp
- https://github.com/OpenIdentityPlatform/OpenAM/commit/98cee2dfe701c2e16e5bcee34e6fd9d913925118
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.1.2
