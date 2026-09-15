# [H] Vaultwarden: CSRF in SSO Authorization Flow

## Summary
Severity: High
Advisory: CVE-2026-47158
Aliases: GHSA-pfp2-jhgq-6hg5
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-47158
Type: osv

## Details
Vaultwarden is a Bitwarden-compatible server written in Rust. Prior to 1.36.0, Vaultwarden's SSO authorization flow did not bind the OAuth state parameter accepted by /connect/authorize to the initiating browser session, allowed attacker-controlled PKCE parameters, and left SsoAuth records intact after failed token exchange, allowing an unauthenticated attacker to induce IdP authentication and redeem tokens for a fully authenticated session. This issue is fixed in version 1.36.0.

## References
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.36.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47158.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-pfp2-jhgq-6hg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-47158
- https://github.com/dani-garcia/vaultwarden/commit/d297e274a35dccd0f5d935e9d5934e0f7e9c0a87
- https://github.com/dani-garcia/vaultwarden/pull/7163
