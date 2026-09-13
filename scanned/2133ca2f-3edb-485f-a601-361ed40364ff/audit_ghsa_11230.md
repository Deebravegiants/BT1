# [H] OpenClaw affected by BASH_ENV / ENV startup-file injection into spawned shell commands

## Summary
Severity: High
Advisory: GHSA-w9cg-v44m-4qv8
CWE: CWE-15, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-w9cg-v44m-4qv8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary
`BASH_ENV` / `ENV` startup-file injection could lead to unintended pre-command shell execution when attacker-controlled environment values were admitted and then inherited by host command execution paths.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.19-2`
- Fixed on `main`: `2cdbadee1f8fcaa93302d7debbfc529e19868ea4`
- Planned patched release version: `2026.2.21`

### Details
The fix hardens environment handling across all relevant execution paths:
- Blocks dangerous startup/runtime env keys and prefixes in shared host env sanitization.
- Sanitizes inherited ambient environment even when no per-request overrides are provided.
- Blocks dangerous config-driven env injection before values enter process environment.
- Uses the same sanitizer in macOS host execution paths.
- Aligns skill env override sanitization with the shared dangerous-env policy.

### Impact
Medium. Exploitation requires local/privileged influence over configuration or environment inputs; there is no standalone remote unauthenticated trigger from this issue alone.

### Fix Commit(s)
- `2cdbadee1f8fcaa93302d7debbfc529e19868ea4`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.21`). Once npm `openclaw@2026.2.21` is published, the advisory can be published without further field edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w9cg-v44m-4qv8
- https://github.com/openclaw/openclaw/commit/2cdbadee1f8fcaa93302d7debbfc529e19868ea4
- https://github.com/openclaw/openclaw
