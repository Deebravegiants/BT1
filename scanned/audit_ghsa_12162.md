# [M] OpenClaw's system.run shell-wrapper positional argv carriers could execute hidden commands under misleading approval text

## Summary
Severity: Medium
Advisory: GHSA-6rcp-vxwf-3mfp
CVE: CVE-2026-32052
CWE: CWE-436, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:A/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-6rcp-vxwf-3mfp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
### Summary
In `openclaw` up to and including **2026.2.23** (latest npm release as of **February 25, 2026**), `system.run` shell-wrapper inputs could present misleading approval/display text while still carrying hidden positional argv payloads that execute at runtime.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.23`
- Patched: `>= 2026.2.24` (planned next release)

### Root Cause
For shell-wrapper forms (for example `/bin/sh -c ...`), command-text binding could focus on inline shell payload text while runtime execution still used the full argv vector. Positional argv carriers after the inline payload could therefore be executed under incomplete display context.

### Security Impact
Approval/display context could omit executed argv carriers, enabling hidden command execution under misleading operator-visible text.

### Fix
- Detect shell-wrapper inline-command forms that carry trailing positional argv values.
- Bind approval/display command text to full formatted argv for those carrier forms.
- Reject payload-only `rawCommand` values when they do not match the execution-bound argv context for those forms.
- Forward canonical command display text to the macOS companion exec host and validate `rawCommand`/argv consistency there for carrier wrappers and env-modifier shell preludes.

### Verification
- `pnpm check`
- `pnpm exec vitest run --config vitest.gateway.config.ts`
- `pnpm test:fast`
- `pnpm vitest run src/infra/system-run-command.test.ts src/node-host/invoke-system-run.test.ts src/cli/nodes-cli.coverage.test.ts src/gateway/node-invoke-system-run-approval.test.ts`
- `cd apps/macos && swift test --filter ExecSystemRunCommandValidatorTests`

### Fix Commit(s)
- `0f0a680d3df81739ea5088a2f88e65f938b7936b`
- `55cf92578d266987e390c4bf688196af98eac748`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.24`) so after npm publish the advisory can be published without further field edits.

OpenClaw thanks @tdjackey for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6rcp-vxwf-3mfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-32052
- https://github.com/openclaw/openclaw/commit/0f0a680d3df81739ea5088a2f88e65f938b7936b
- https://github.com/openclaw/openclaw/commit/55cf92578d266987e390c4bf688196af98eac748
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-hidden-command-execution-via-shell-wrapper-positional-argv-carriers
