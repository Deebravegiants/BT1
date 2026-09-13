# [M] OpenClaw's system.run allowlist approval parsing missed PowerShell encoded-command wrappers

## Summary
Severity: Medium
Advisory: GHSA-3h2q-j2v4-6w5r
CWE: CWE-184, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-3h2q-j2v4-6w5r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.7

## Details
OpenClaw's `system.run` shell-wrapper detection did not recognize PowerShell `-EncodedCommand` forms as inline-command wrappers.

In `allowlist` mode, a caller with access to `system.run` could invoke `pwsh` or `powershell` using `-EncodedCommand`, `-enc`, or `-e`, and the request would fall back to plain argv analysis instead of the normal shell-wrapper approval path. This could allow a PowerShell inline payload to execute without the approval step that equivalent `-Command` invocations would require.

Latest published npm version: `2026.3.2`

Fixed on `main` on March 7, 2026 in `1d1757b16f48f1a93cd16ab0ad7e2c3c63ce727d` by recognizing PowerShell encoded-command aliases during shell-wrapper parsing, so allowlist mode continues to require approval for those payloads. Normal approved PowerShell wrapper flows continue to work.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.2`
- Patched version: `>= 2026.3.7`

## Fix Commit(s)

- `1d1757b16f48f1a93cd16ab0ad7e2c3c63ce727d`

## Release Process Note

npm `2026.3.7` was published on March 8, 2026. This advisory is fixed in the released package.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3h2q-j2v4-6w5r
- https://github.com/openclaw/openclaw/commit/1d1757b16f48f1a93cd16ab0ad7e2c3c63ce727d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.7
