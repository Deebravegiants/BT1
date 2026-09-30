# [M] OpenClaw's `system.run` env override filtering allowed dangerous helper-command pivots

## Summary
Severity: Medium
Advisory: GHSA-j425-whc4-4jgc
CWE: CWE-15, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-j425-whc4-4jgc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.7

## Details
### Summary
`system.run` env override sanitization allowed dangerous override-only helper-command pivots to reach subprocesses. A caller who could invoke `system.run` with `env` overrides could bypass allowlist/approval intent by steering an allowlisted tool through helper-command or config-loading environment variables such as `GIT_SSH_COMMAND`, editor/pager hooks, and `GIT_CONFIG_*` / `NPM_CONFIG_*`.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published vulnerable version: `2026.3.2`
- Affected range: `<= 2026.3.2`
- Patched in: `2026.3.7`

### Details
Before the fix, `src/infra/host-env-security.ts` blocked only a narrow set of override-only environment variables. Dangerous request-scoped overrides such as `GIT_SSH_COMMAND` and prefix families such as `GIT_CONFIG_*` and `NPM_CONFIG_*` could still survive `sanitizeSystemRunEnvOverrides(...)` / `sanitizeHostExecEnv(...)` and reach the spawned process.

That mattered for `system.run` allowlist and approval flows because approval evaluation was tied to the reviewed binary/argv, while the launched process could still inherit attacker-controlled env overrides that changed helper-command execution or config resolution. For allowlisted tools such as `git`, this allowed behavior outside the reviewed command semantics.

The fix extends the shared TypeScript and macOS policy to block dangerous override-only exact keys and prefixes while preserving trusted inherited base-environment behavior.

### Impact
This is a real protection-bypass issue, but exploitation requires an already tool-enabled caller who can invoke `system.run` and supply `env` overrides. In affected deployments, that caller could bypass allowlist/approval intent and trigger helper-command execution or config-loading behavior that is not represented by the approved command line. Maintainer severity is set to medium because the bug still requires that existing execution capability; the vulnerability is the mismatch between reviewed command semantics and the actual spawned-process behavior.

### Fix Commit(s)
- `e27bbe4982439da6864160fd1b66445058f74801`

### Release Process Note
npm `2026.3.7` was published on March 8, 2026. This advisory is fixed in the released package.

Thanks @tdjackey and @SnailSploit for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j425-whc4-4jgc
- https://github.com/openclaw/openclaw/commit/e27bbe4982439da6864160fd1b66445058f74801
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.7
