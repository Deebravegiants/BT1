# [M] OpenClaw has a BlueBubbles group allowlist mismatch via DM pairing-store fallback

## Summary
Severity: Medium
Advisory: GHSA-25pw-4h6w-qwvm
CVE: CVE-2026-32006
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-25pw-4h6w-qwvm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.26

## Details
### Summary
In `openclaw@2026.2.25`, BlueBubbles group authorization could incorrectly treat DM pairing-store identities as group allowlist identities when `dmPolicy=pairing` and `groupPolicy=allowlist`.

A sender that was only DM-paired (not explicitly present in `groupAllowFrom`) could pass group sender checks for message and reaction ingress.

Per OpenClaw's `SECURITY.md` trust model, this is a constrained authorization-consistency issue, not a multi-tenant boundary bypass or host-privilege escalation.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version at triage time: `2026.2.25`
- Affected versions: `<= 2026.2.25`
- Patched versions: `>= 2026.2.26` (planned next release)

### Technical Details
Root cause was DM/group allowlist composition where DM pairing-store identities could flow into group authorization decisions.

Fix approach:
- centralize DM/group authorization composition via shared resolvers
- remove local DM/group list recomposition at channel callsites
- add cross-channel regression coverage for message + reaction ingress
- add CI guard to block future pairing-store leakage into group auth composition

### Impact
- Affects deployments using BlueBubbles with `groupPolicy=allowlist` and `dmPolicy=pairing` when pairing-store entries are present.
- Could allow DM-authorized identities to be treated as group-authorized without explicit `groupAllowFrom` membership.
- Does **not** bypass gateway auth, sandbox boundaries, or create new host-level privilege beyond existing DM authorization.

### Fix Commit(s)
- `051fdcc428129446e7c084260f837b7284279ce9`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.26`) so once npm `2026.2.26` is published, this advisory can be published without further content edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-25pw-4h6w-qwvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32006
- https://github.com/openclaw/openclaw/commit/051fdcc428129446e7c084260f837b7284279ce9
- https://github.com/openclaw/openclaw/commit/1aadf26f9acc399affabd859937a09468a9c5cb4
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-dm-pairing-store-fallback-in-group-allowlist
