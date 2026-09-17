# [M] OpenClaw's sandbox skill mirroring path traversal vulnerability could write outside the sandbox workspace

## Summary
Severity: Medium
Advisory: GHSA-xw4p-pw82-hqr7
CVE: CVE-2026-28457
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-xw4p-pw82-hqr7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Overview

In affected versions, OpenClaw’s sandbox skill mirroring used the skill’s frontmatter `name` as part of the destination path when copying skills into the sandbox workspace. A crafted skill name containing traversal segments (for example `../`) or an absolute path could cause the copy to write outside `<sandbox_workspace>/skills/`.

## Impact

- Files may be written outside the sandbox workspace root (within the permissions of the user running OpenClaw).

## Attack Requirements

- Attacker can provide a skill package (controls `SKILL.md` frontmatter).
- Victim runs with sandbox enabled and skill mirroring into the sandbox workspace.

## Affected Packages / Versions

- `openclaw` (npm): `< 2026.2.14`

## Fixed In

- `openclaw` (npm): `>= 2026.2.14`

## Fix Commit(s)

- 3eb6a31b6fcf8268456988bfa8e3637d373438c2

OpenClaw thanks @1seal for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xw4p-pw82-hqr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-28457
- https://github.com/openclaw/openclaw/commit/3eb6a31b6fcf8268456988bfa8e3637d373438c2
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-path-traversal-in-sandbox-skill-mirroring-via-name-parameter
