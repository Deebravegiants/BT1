# [M] OpenClaw's non-default safeBins sort configuration can bypass intended allowlist approval constraints

## Summary
Severity: Medium
Advisory: GHSA-vmqr-rc7x-3446
CVE: CVE-2026-22169
CWE: CWE-15, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-vmqr-rc7x-3446
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
When `sort` is explicitly added to `tools.exec.safeBins` (non-default), the `--compress-program` option can invoke an external helper and bypass the intended safe-bin approval constraints in allowlist mode.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Vulnerable versions: `<=2026.2.21-2`
- Latest published npm version checked during triage: `2026.2.21-2` (as of February 22, 2026)
- Patched in planned next release: `2026.2.22`

## Fix Commit(s)

- `57fbbaebca4d34d17549accf6092ae26eb7b605c`

## Release Process Note

`patched_versions` is pre-set to the planned next release (`>=2026.2.22`). Once that npm release is published, the advisory can be published directly.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vmqr-rc7x-3446
- https://github.com/openclaw/openclaw/commit/57fbbaebca4d34d17549accf6092ae26eb7b605c
- https://github.com/openclaw/openclaw
