# [M] OpenClaw: Skill env override host env injection via applySkillConfigEnvOverrides (defense-in-depth)

## Summary
Severity: Medium
Advisory: GHSA-82g8-464f-2mv7
CVE: CVE-2026-4039
CWE: CWE-1341, CWE-15, CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-82g8-464f-2mv7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary
`applySkillConfigEnvOverrides` previously copied `skills.entries.*.env` values into the host `process.env` without applying the host env safety policy.

### Impact
In affected versions, dangerous process-level variables such as `NODE_OPTIONS` could be injected when unset, which can influence runtime/child-process behavior.

### Required attacker capability
An attacker must be able to modify OpenClaw local state/config (for example `~/.openclaw/openclaw.json`) to set `skills.entries.<skill>.env` or related skill config values.

### Remediation
Fixed in `2026.2.21` by sanitizing skill env overrides and blocking dangerous host env keys (including `NODE_OPTIONS`) before applying overrides, with regression tests covering blocked dangerous keys.

## Fix Commit(s)
- `8c9f35cdb51692b650ddf05b259ccdd75cc9a83c`

Found using [MCPwner](https://github.com/Pigyon/MCPwner)

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-82g8-464f-2mv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-4039
- https://github.com/openclaw/openclaw/commit/8c9f35cdb51692b650ddf05b259ccdd75cc9a83c
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.21
