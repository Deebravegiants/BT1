# [H] OpenClaw: Sandbox media fallback tmp symlink alias bypass allows host file reads outside sandboxRoot

## Summary
Severity: High
Advisory: GHSA-xmv6-r34m-62p4
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-xmv6-r34m-62p4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
A sandbox path validation bypass in `openclaw` allows host file reads outside `sandboxRoot` via the media path fallback tmp flow when the fallback tmp root is a symlink alias.

### Affected Packages / Versions
- Package: `npm openclaw`
- Affected versions: `<= 2026.2.24`
- Latest published npm version at triage time (February 26, 2026): `2026.2.24`
- Patched version : `2026.2.25`

### Details
When `/tmp/openclaw` is unavailable or unsafe, `resolvePreferredOpenClawTmpDir()` in `src/infra/tmp-openclaw-dir.ts` fell back to `os.tmpdir()/openclaw-<uid>` without verifying that fallback path was a trusted non-symlink directory.

`resolveSandboxedMediaSource()` (`src/agents/sandbox-paths.ts`) allows absolute tmp media paths under the OpenClaw tmp root using lexical containment and alias checks. If the fallback tmp root is a symlink alias (for example to `/`), inputs like `$TMPDIR/openclaw-<uid>/etc/passwd` can pass validation and resolve to host files outside `sandboxRoot`.

### Impact
This can break sandbox media path confinement and permit unauthorized host file reads (confidentiality impact).

### Reproduction (high level)
1. Force resolver fallback (make `/tmp/openclaw` unavailable/invalid).
2. Make fallback root (`$TMPDIR/openclaw-<uid>`) a symlink alias to `/`.
3. Submit media path under fallback root (for example `$TMPDIR/openclaw-<uid>/etc/passwd`).
4. Observe accepted path and read outside `sandboxRoot`.

### Fix Commit(s)
- `496a76c03ba85e15ea715e5a583e498ae04d36e3`

### Release Process Note
Patched version is pre-set to release `2026.2.25`; once npm publish for `2026.2.25` is complete, this advisory can be published without further metadata edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xmv6-r34m-62p4
- https://github.com/openclaw/openclaw/commit/496a76c03ba85e15ea715e5a583e498ae04d36e3
- https://github.com/openclaw/openclaw
