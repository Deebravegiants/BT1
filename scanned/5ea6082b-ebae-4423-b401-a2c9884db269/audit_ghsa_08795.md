# [H] OpenClaw vulnerable to arbitrary code execution via attacker-controlled setup-api.js loaded from cwd during env-key resolution

## Summary
Severity: High
Advisory: GHSA-r39h-4c2p-3jxp
CVE: CVE-2026-45004
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-r39h-4c2p-3jxp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.23

## Details
## Summary

OpenClaw's bundled plugin setup resolver could fall back to `process.cwd()` while resolving provider setup metadata. If a user ran an OpenClaw command from an attacker-controlled repository containing `extensions/<plugin>/setup-api.js`, OpenClaw could load and execute that JavaScript during ordinary provider/model status resolution.

## Impact

This is arbitrary JavaScript execution in the OpenClaw process under the current user account. A malicious repository could run code when the user executed commands such as provider/model inspection from that directory. The issue does not require gateway network exposure, but it does require user interaction: the user must run OpenClaw from a directory containing the attacker-controlled setup file.

## Affected Packages / Versions

- Package: `openclaw` on npm
- Affected: versions before `2026.4.23`
- Fixed: `2026.4.23`
- Latest stable verified fixed: `openclaw@2026.4.23`, tag `v2026.4.23`

## Fix

OpenClaw now resolves bundled setup fallbacks only from the canonical package/repository root and no longer includes `process.cwd()` as a trusted setup-api search root. A regression test verifies that a workspace-local `extensions/<plugin>/setup-api.js` is not loaded through provider setup resolution.

## Fix Commit(s)

- `993781e6e6eaf50f033cfc3e3bf4f47059740707` (`fix(plugins): ignore cwd setup-api fallback`)

## Severity

Severity remains `high` because successful exploitation allows arbitrary code execution under the user running OpenClaw. The CVSS vector is local/user-interaction scoped rather than network-only because the victim must run OpenClaw from an attacker-controlled directory.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r39h-4c2p-3jxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45004
- https://github.com/openclaw/openclaw/commit/993781e6e6eaf50f033cfc3e3bf4f47059740707
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-code-execution-via-setup-api-js-in-current-working-directory
