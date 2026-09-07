# [H] OpenClaw has system.run shell-wrapper env injection via SHELLOPTS/PS4 can bypass allowlist intent (RCE)

## Summary
Severity: High
Advisory: GHSA-2fgq-7j6h-9rm4
CVE: CVE-2026-32003
CWE: CWE-15, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-2fgq-7j6h-9rm4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
`system.run` allowed `SHELLOPTS` + `PS4` environment injection to trigger command substitution during `bash -lc` xtrace expansion before the allowlisted command body executed.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.21-2` (includes latest published npm version at triage time)
- Patched (planned next release): `2026.2.22`

### Impact
In `allowlist` mode, an attacker who can invoke `system.run` with request-scoped `env` could execute additional shell commands outside the intended allowlisted command body.

### Root Cause
Host exec env sanitization blocked startup-file vectors (`BASH_ENV`, `ENV`, etc.) but did not block `SHELLOPTS`/`PS4`. For shell wrappers (`bash|sh|zsh ... -c/-lc`), request env overrides were passed through and `bash` evaluated `PS4` under `xtrace`, enabling command substitution.

### Fix
- Block `SHELLOPTS` and `PS4` in host exec env sanitizers (Node + macOS).
- For shell wrappers (`bash|sh|zsh ... -c/-lc`), reduce request-scoped env overrides to an explicit allowlist (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
- Add regression tests for TS and macOS paths.

### Fix Commit(s)
- `e80c803fa887f9699ad87a9e906ab5c1ff85bd9a`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.22`). Once npm release `2026.2.22` is published, advisory publication is a final state action only.

### Severity Rationale
This advisory is rated **medium** because exploitation requires a caller that can already invoke `system.run` with request-scoped `env`.

Under OpenClaw's documented trust model (`SECURITY.md`), authenticated Gateway callers are treated as trusted operators, and adversarial multi-operator / prompt-injection scenarios are out of scope.

The bug remains a real allowlist-intent bypass, but it does not cross a separate trust boundary in the documented deployment assumptions.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2fgq-7j6h-9rm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-32003
- https://github.com/openclaw/openclaw/commit/e80c803fa887f9699ad87a9e906ab5c1ff85bd9a
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-remote-code-execution-via-shellopts-ps4-environment-injection-in-system-run
