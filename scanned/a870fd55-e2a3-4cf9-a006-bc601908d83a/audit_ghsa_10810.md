# [M] OpenClaw shell-env fallback trusted startup env and could execute attacker-influenced login-shell paths

## Summary
Severity: Medium
Advisory: GHSA-5h2c-8v84-qpvr
CWE: CWE-15, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-5h2c-8v84-qpvr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
OpenClaw shell-env fallback trusted startup environment values and could execute attacker-influenced login-shell startup paths before loading env keys.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `>= 2026.1.5` and `<= 2026.2.21-2`
- Fixed on `main`: `9363c320d8ffe29290906752fab92621da02c3f7`
- Planned patched release version (pre-set): `2026.2.22`

### Details
The vulnerable chain was in the shell-env fallback path:

1. `src/infra/shell-env.ts`
- `resolveShell(env)` trusted `env.SHELL` when set.
- `execLoginShellEnvZero(...)` executed `${SHELL} -l -c "env -0"` with inherited runtime env.

2. `src/config/io.ts`
- Config env values were applied before shell fallback execution.

3. `src/config/env-vars.ts` / env policy coverage
- `SHELL` handling was hardened, but startup-path selectors (`HOME`, `ZDOTDIR`) still needed explicit blocking in config env ingestion and sanitization for shell fallback execution.

With env/config influence, this could trigger unintended command execution in shell startup processing on the OpenClaw host process context.

### Fix
Mainline hardening now:
- blocks `SHELL`, `HOME`, and `ZDOTDIR` during config env ingestion used by runtime fallback,
- sanitizes shell fallback execution env, pinning `HOME` to the real user home and dropping `ZDOTDIR` + dangerous startup vars,
- adds regression tests for config env ingestion and shell fallback/path-probe sanitization.

### Fix Commit(s)
- `9363c320d8ffe29290906752fab92621da02c3f7`

### Impact
- Local code-execution risk in environments where attacker-controlled env/config input can reach shell-env fallback.
- Under OpenClaw trust assumptions (`SECURITY.md`), this is not a public-remote issue and depends on crossing local trusted-operator boundaries.

### Release Process Note
`patched_versions` is intentionally pre-set to the planned next release (`2026.2.22`) so once npm release is out, maintainers can publish advisory immediately.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5h2c-8v84-qpvr
- https://github.com/openclaw/openclaw/commit/9363c320d8ffe29290906752fab92621da02c3f7
- https://github.com/openclaw/openclaw
