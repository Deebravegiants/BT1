# [M] OpenClaw Chutes manual OAuth state validation bypass can cause credential substitution

## Summary
Severity: Medium
Advisory: GHSA-7rcp-mxpq-72pj
CVE: CVE-2026-28477
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-7rcp-mxpq-72pj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

The manual Chutes OAuth login flow could accept attacker-controlled callback input in a way that bypassed OAuth CSRF state validation, potentially resulting in credential substitution.

## Impact

If an attacker can convince a user to paste attacker-provided OAuth callback data during the manual login prompt, OpenClaw may exchange an attacker-obtained authorization code and persist tokens for the wrong Chutes account.

The automatic local callback flow is not affected (it validates state in the local HTTP callback handler).

## Affected Packages / Versions

- `openclaw` (npm): `<= 2026.2.13` when using the manual Chutes OAuth login flow.

## Fix

The manual flow now requires the full redirect URL (must include `code` and `state`), validates the returned `state` against the expected value, and rejects code-only pastes.

## Fix Commit(s)

- a99ad11a4107ba8eac58f54a3c1a8a0cf5686f47

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7rcp-mxpq-72pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-28477
- https://github.com/openclaw/openclaw/commit/a99ad11a4107ba8eac58f54a3c1a8a0cf5686f47
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-oauth-state-validation-bypass-in-manual-chutes-login-flow
