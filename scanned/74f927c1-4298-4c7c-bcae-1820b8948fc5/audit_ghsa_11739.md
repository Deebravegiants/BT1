# [M] OpenClaw has a Discord `allowFrom` slug-collision authorization bypass

## Summary
Severity: Medium
Advisory: GHSA-4cqv-h74h-93j4
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-4cqv-h74h-93j4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
OpenClaw supports Discord allowlists using either user IDs or names/tags. Name/tag matching depends on slug normalization, so different user tags can collide to the same slug and unintentionally satisfy a name-based allowlist entry.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.21-2`
- Patched versions: >= 2026.2.22

## What Changed
- `openclaw security audit` now warns on Discord name/tag allowlist entries (DM allowlists, guild/channel `users`, and pairing-store entries).
- Runtime authorization now prefers resolved user IDs when a configured name/tag can be resolved, without rewriting config files on disk.
- Name-based entries remain supported for compatibility.

## Recommendations
- Prefer stable Discord user IDs for security-sensitive allowlists.
- Run `openclaw security audit` and address warnings where practical.

## Fix Commit(s)
- f97c45c5b5e0698b6667bb5f6badc0cac7dabd12
- 747bb581b3f2264495e1fec5a0727d9f2ca1b6f1

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4cqv-h74h-93j4
- https://github.com/openclaw/openclaw/commit/747bb581b3f2264495e1fec5a0727d9f2ca1b6f1
- https://github.com/openclaw/openclaw/commit/f97c45c5b5e0698b6667bb5f6badc0cac7dabd12
- https://github.com/openclaw/openclaw
