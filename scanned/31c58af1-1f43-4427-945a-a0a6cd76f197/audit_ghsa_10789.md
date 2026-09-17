# [H] OpenClaw: Gemini OAuth exposed the PKCE verifier through the OAuth state parameter

## Summary
Severity: High
Advisory: GHSA-9jpj-g8vv-j5mf
CVE: CVE-2026-34511
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-9jpj-g8vv-j5mf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, the Gemini OAuth flow reused the PKCE verifier as the OAuth `state` value. Because the provider reflected `state` back in the redirect URL, the verifier could be exposed alongside the authorization code.

## Impact

Anyone who could capture the redirect URL could learn both the authorization code and the PKCE verifier, defeating PKCE's interception protection for that flow and enabling token redemption.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `a26f4d0f3ef0757db6c6c40277cc06a5de76c52f` — separate OAuth state from the PKCE verifier

OpenClaw thanks @BG0ECV for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9jpj-g8vv-j5mf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34511
- https://github.com/openclaw/openclaw/commit/a26f4d0f3ef0757db6c6c40277cc06a5de76c52f
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-pkce-verifier-exposure-via-oauth-state-parameter
