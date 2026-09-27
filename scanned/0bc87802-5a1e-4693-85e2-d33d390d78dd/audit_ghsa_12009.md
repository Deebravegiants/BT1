# [M] OpenClaw unpaired device identity can bypass operator pairing and self-assign operator scopes with shared auth

## Summary
Severity: Medium
Advisory: GHSA-553v-f69r-656j
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-553v-f69r-656j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.22 <2026.2.25

## Details
### Summary
A client using shared gateway auth could attach an unpaired device identity and request elevated operator scopes (including `operator.admin`) before pairing approval, enabling privilege escalation.

### Impact
Attackers with valid shared gateway auth could self-assign higher operator scopes by presenting a self-signed, unpaired device identity.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `>= 2026.2.22 <= 2026.2.24`
- Latest published npm at triage time: `2026.2.24`
- Planned patched release: `2026.2.25`

### Remediation
Require pairing for operator device-identity sessions authenticated with shared token/password auth (except existing control-ui trusted-proxy/control-ui bypass policy paths).

### Fix Commit(s)
- `8d1481cb4a9d31bd617e52dc8c392c35689d9dea`

### Release Process Note
`patched_versions` is pre-set to the release (`>= 2026.2.25`). Advisory published with npm release `2026.2.25`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-553v-f69r-656j
- https://github.com/openclaw/openclaw/commit/8d1481cb4a9d31bd617e52dc8c392c35689d9dea
- https://github.com/openclaw/openclaw
