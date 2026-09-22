# [M] OpenClaw: MS Teams fileConsent/invoke missing conversation binding allowed cross-conversation pending-upload consumption

## Summary
Severity: Medium
Advisory: GHSA-j26j-7qc4-3mrf
CWE: CWE-639, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-j26j-7qc4-3mrf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
In `openclaw` MS Teams file-consent flow, pending uploads were authorized by `uploadId` alone. `fileConsent/invoke` did not verify the invoke conversation against the conversation that created the pending upload.

### Impact
An attacker who obtained a valid `uploadId` within TTL could trigger cross-conversation upload completion (accept path) or cancel a victim pending upload (decline path).

### Technical Details
- Pending uploads stored `conversationId`, but invoke handling consumed by `uploadId` only.
- The invoke path did not enforce conversation binding before `uploadToConsentUrl(...)` and pending-upload removal.
- Fix binds accept/decline handling to normalized conversation id match before consuming pending upload state.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version (as of February 26, 2026): `2026.2.24`
- Vulnerable range: `<= 2026.2.24`
- Patched in release: `2026.2.25`

### Remediation
Upgrade to `openclaw` `2026.2.25` (or later) once published.

### Fix Commit(s)
- `347f7b9550064f5f5b33c6e07f64e85b9657b6f1`

### Release Process Note
`patched_versions` is pre-set to the release (`2026.2.25`). Advisory published with npm release `2026.2.25`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j26j-7qc4-3mrf
- https://github.com/openclaw/openclaw/commit/347f7b9550064f5f5b33c6e07f64e85b9657b6f1
- https://github.com/openclaw/openclaw
