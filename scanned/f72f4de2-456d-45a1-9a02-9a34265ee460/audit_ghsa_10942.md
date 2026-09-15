# [H] OpenClaw's non-default autoAllowSkills setting could bypass on-miss exec prompt

## Summary
Severity: High
Advisory: GHSA-7ff8-xjh3-mgh6
CWE: CWE-266, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-7ff8-xjh3-mgh6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
### Summary
In `openclaw` versions up to and including `2026.2.22-2`, a non-default exec-approval configuration could allow a skill-name collision to bypass an `ask=on-miss` prompt.

When `autoAllowSkills=true`, a path-scoped executable such as `./skill-bin` could resolve to basename `skill-bin`, satisfy the `skills` allowlist segment, and run without prompting for approval.

### Affected Packages / Versions
- Package: `npm openclaw`
- Affected versions: `<= 2026.2.22-2`
- Patched versions: `>= 2026.2.23` (released)

### Configuration Scope (Not Default)
This behavior requires non-default settings and does not affect default installs.

Required conditions:
- `autoAllowSkills=true` (default is `false`)
- `system.run` with `security=allowlist`
- `ask=on-miss`

### Technical Details
The allowlist evaluator accepted `skills` satisfaction by bin-name match, so `./skill-bin` could match `skillBins.has("skill-bin")` after resolution.

The fix hardens skill auto-allow matching by requiring:
- a pathless invocation token (no `/` or `\\`), and
- a trusted resolved executable path for that skill bin on the machine where skills run.

This preserves normal `skill-bin ...` behavior while preventing `./<skill-bin>` and absolute-path basename collisions from auto-satisfying `skills`.

### Impact
In affected non-default configurations, approval prompts could be skipped for commands that should have required operator confirmation.

### Fix Commit(s)
- `ffd63b7a2c4c6d5aeb4710ef951d5794ad7ad77b` (`fix(security): trust resolved skill-bin paths in allowlist auto-allow`)

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7ff8-xjh3-mgh6
- https://github.com/openclaw/openclaw/commit/ffd63b7a2c4c6d5aeb4710ef951d5794ad7ad77b
- https://github.com/openclaw/openclaw
