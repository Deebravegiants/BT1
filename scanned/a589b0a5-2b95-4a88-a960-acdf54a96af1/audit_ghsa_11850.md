# [M] OpenClaw's tools.exec.safeBins trusted PATH directories allowed binary shadowing in allowlist mode

## Summary
Severity: Medium
Advisory: GHSA-qhrr-grqp-6x2g
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-qhrr-grqp-6x2g
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
In `openclaw` allowlist mode, `tools.exec.safeBins` trusted PATH-derived directories for safe-bin resolution. A same-name binary placed in a trusted PATH directory could satisfy safe-bin checks and execute.

### Impact
This is an allowlist bypass in exec policy that can lead to command execution in the OpenClaw runtime context when allowlist mode relies on safe bins and an attacker can influence trusted binary locations.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.2.21-2`
- Patched versions: `>= 2026.2.22` (planned next release)
- Latest published npm version at triage time (2026-02-22): `2026.2.21-2`

### Root Cause
- Safe-bin trust accepted PATH-derived directories instead of explicit trusted directories.
- Safe-bin execution used shell command tokens that could resolve to shadowed binaries.

### Remediation
- Stop trusting PATH-derived directories for safe-bin trust.
- Add explicit `tools.exec.safeBinTrustedDirs` for opt-in extra trusted paths.
- Pin safe-bin shell execution to resolved absolute executable paths.

### Fix Commit(s)
- `64b273a71cf0b2f2419c974832cede1fc2158729`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.22`). After npm release, this advisory is ready for publish without additional field edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qhrr-grqp-6x2g
- https://github.com/openclaw/openclaw/commit/64b273a71cf0b2f2419c974832cede1fc2158729
- https://github.com/openclaw/openclaw
