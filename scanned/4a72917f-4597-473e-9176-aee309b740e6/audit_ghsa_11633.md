# [M] OpenClaw's Node system.run approval hardening wrapper semantic drift can execute unintended local scripts

## Summary
Severity: Medium
Advisory: GHSA-h3rm-6x7g-882f
CVE: CVE-2026-29608
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-h3rm-6x7g-882f
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.3.1 <2026.3.2

## Details
### Summary
In `openclaw@2026.3.1`, node `system.run` approval-path hardening rewrote wrapper command argv in a way that changed execution semantics. A command shown/approved as a shell payload (for example `echo SAFE`) could execute a different local script when wrapper argv were rewritten.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `2026.3.1` (latest published npm version as of March 2, 2026)
- Fixed release: `2026.3.2` (released)

### Technical Details
Root cause was in node-host approval hardening for `system.run`:
- `src/node-host/invoke-system-run-plan.ts` rewrote `argv[0]` to the resolved executable.
- Wrapper resolution unwrapped dispatch wrappers, so input like `['env','sh','-c','echo SAFE']` resolved executable `sh`.
- The approved plan could become `['/bin/sh','sh','-c','echo SAFE']` while approval text remained `echo SAFE`.

That rewrite changed runtime behavior: `/bin/sh` interprets the extra `sh` positional argument as a script path, enabling execution of a local `./sh` file from approved `cwd` instead of the approved payload text.

### Impact
Approval-integrity break in `host=node` execution flow: operator-visible command text and executed behavior could diverge.

Exploit preconditions:
- attacker can influence wrapper argv and place a local file in approved working directory,
- operator grants approval for the displayed command.

### Fix Commit(s)
- `dded569626b0d8e7bdab10b5e7528b6caf73a0f1`

### Fixed Version
- Patched in `openclaw@2026.3.2`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h3rm-6x7g-882f
- https://nvd.nist.gov/vuln/detail/CVE-2026-29608
- https://github.com/openclaw/openclaw/commit/dded569626b0d8e7bdab10b5e7528b6caf73a0f1
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-approval-integrity-bypass-via-system-run-argv-rewriting
