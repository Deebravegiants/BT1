# [M] OpenClaw: macOS beta onboarding exposed PKCE verifier via OAuth state

## Summary
Severity: Medium
Advisory: GHSA-6g25-pc82-vfwp
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-6g25-pc82-vfwp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary

The affected surface is the OpenClaw macOS app onboarding flow, and the macOS app is currently in **beta**.
In that beta onboarding flow, Anthropic OAuth used the PKCE `code_verifier` value as OAuth `state`, exposing that secret in front-channel URL state.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.24` (latest published npm at triage time)
- Affected surface: macOS app beta onboarding path (`apps/macos`)
- Not affected: core CLI/gateway onboarding paths
- Patched version : `2026.2.25`

### Impact

Scope is limited to the macOS beta onboarding OAuth path. Exploitation required obtaining both OAuth authorization artifacts and exposed `state` values during that flow.

### Remediation

OpenClaw removed Anthropic OAuth sign-in from macOS onboarding and now supports setup-token-only Anthropic subscription auth in this path.

### Fix Commit(s)

- `8f3310000a8b0c11eced054c2cdb6fb27803511a`

### Release Process Note

`patched_versions` is pre-set to the release (`2026.2.25`).
Advisory published with npm release `2026.2.25`.2.25` is published, this advisory is published.

OpenClaw thanks @zdi-disclosures for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6g25-pc82-vfwp
- https://github.com/openclaw/openclaw/commit/8f3310000a8b0c11eced054c2cdb6fb27803511a
- https://github.com/openclaw/openclaw
