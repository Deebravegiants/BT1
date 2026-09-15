# [H] claude-code-cache-fix vulnerable to local code execution via Python triple-quote injection in tools/quota-statusline.sh

## Summary
Severity: High
Advisory: GHSA-g3xq-3gmv-qq8g
CVE: CVE-2026-45136
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-g3xq-3gmv-qq8g
Type: github-advisory

## Affected
- npm: `claude-code-cache-fix` — affected >=3.5.0 <3.5.2

## Details
## Summary

`tools/quota-statusline.sh` (introduced in v3.5.0) interpolates Claude Code's hook stdin payload directly into a Python triple-quoted string literal. A `'''` byte sequence in any user-controlled field of the payload closes the literal early and lets following bytes execute as Python in the user's Claude Code process.

## Affected versions

- v3.5.0
- v3.5.1

## Patched versions

- v3.5.2

## Affected configurations

Users who wired `tools/quota-statusline.sh` into Claude Code's `statusLine` configuration. The v3.5.0 README explicitly recommends this setup, so most users on v3.5.0/v3.5.1 with the recommended setup are affected.

## Attack chain

Claude Code's statusline hook payload reflects user-controlled paths (`cwd`, `workspace.current_dir`, `workspace.project_dir`, `transcript_path`). Apostrophes are legal in POSIX filesystem paths.

1. A hostile directory name containing `'''+payload+'''` lands on disk via any normal vector — `git clone`, archive extraction, npm package, downloaded zip, etc.
2. The victim has the recommended `tools/quota-statusline.sh` wired into their CC `statusLine` config.
3. The victim `cd`s anywhere a hostile path is reachable.
4. CC fires the statusline hook on every redraw. The Python literal closes early. The injected bytes execute as Python in the user's process.

## Severity

Local code execution at user privilege. Persistent re-fire on every statusline redraw. No user interaction beyond `cd`-ing into the hostile path. The user's shell, CC session, files, SSH keys, and any locally-accessible credentials are reachable from the executed code.

## Vulnerable pattern

```sh
input=$(cat)
result=$(python3 -c "
    stdin_data = json.loads('''$input''') if '''$input''' else {}
")
```

## Fix

Capture stdin in bash, export to env, and pipe the Python source through a single-quoted heredoc (`<<'PYEOF'`). Single-quoting disables ALL bash interpolation inside the body. Python reads the JSON via `os.environ.get('CC_INPUT')`, where the bytes are inert at every layer.

```sh
CC_INPUT=$(cat)
export CC_INPUT

python3 <<'PYEOF' 2>/dev/null
import os, json
try:
    cc_input = json.loads(os.environ.get('CC_INPUT') or '{}')
except Exception:
    cc_input = {}
# ...
PYEOF
```

## Workarounds

Until upgrading to v3.5.2:

- Disable the statusline by removing the `statusLine` entry from `~/.claude/settings.json`, or
- Replace `tools/quota-statusline.sh` with a script that does NOT pass stdin through `python3 -c "..."` (a heredoc + env var rewrite is safe)

## Credit

Reported by Jakob Linke (@schuay) via GitHub issue [#108](https://github.com/cnighswonger/claude-code-cache-fix/issues/108).

## Timeline

- 2026-05-07 — reported (#108)
- 2026-05-07 — confirmed, fix implemented (#110)
- 2026-05-07 — v3.5.2 published

## References
- https://github.com/cnighswonger/claude-code-cache-fix/security/advisories/GHSA-g3xq-3gmv-qq8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-45136
- https://github.com/cnighswonger/claude-code-cache-fix/issues/108
- https://github.com/cnighswonger/claude-code-cache-fix/pull/110
- https://github.com/cnighswonger/claude-code-cache-fix/commit/613e4df30547f3e6baf32d161eddc828f171da17
- https://github.com/cnighswonger/claude-code-cache-fix
