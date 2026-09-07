# [H] GitPython: git-config OPTION-name injection via =/#/whitespace bypasses name validator, enabling forged core.sshCommand/hooksPath (RCE)

## Summary
Severity: High
Advisory: GHSA-jm78-9fvv-mhgr
CWE: CWE-74, CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-jm78-9fvv-mhgr
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.58

## Details
## Summary
GitPython's config-name validator only neutralizes CR/LF/NUL for the `"option"` label; it does not reject `=`, `#`, `;`, `[`, `]`, or whitespace in an **option name**. `write_section` writes the option name verbatim into the config file, so an option name such as `sshCommand = touch <cmd> #` is written as `\tsshCommand = touch <cmd> # = <value>`, which git parses as `core.sshCommand = touch <cmd>` (the trailing `#` comments out the intended value). This forges arbitrary config directives (`core.sshCommand`, `core.hooksPath`, `alias.*`) → RCE on the next git operation. This is a distinct field (option name, not section name) and distinct character class (`=`/`#`/space, not newline/bracket) from GHSA-3rp5-jjmw-4wv2 (section-name bracket injection) and GHSA-mv93-w799-cj2w / GHSA-v87r-6q3f-2j67 (newline injection).

## Root Cause
`_assure_config_name_safe(name, label)` (`git/config.py:897`) applies the bracket/quote state machine ONLY when `label == "section"`; for the `"option"` label it falls through with just the `UNSAFE_CONFIG_CHARS_RE = [\r\n\x00]` regex. `write_section` then writes the option name verbatim into `"\t%s = %s\n"` (config.py:702).

## Impact
Arbitrary git-config directive injection → remote code execution via `core.sshCommand` (fires on any ssh git operation, no staged file needed) or `core.hooksPath` (with a staged hook). Requires the embedding application to forward a caller-influenced OPTION NAME into the config writer (name-control model, the same name-control model accepted by the related published advisories GHSA-3rp5-jjmw-4wv2 and GHSA-mv93-w799-cj2w). Default configuration.

## Proof of Concept
```python
with repo.config_writer() as cw:
    cw.set_value("core", "sshCommand = touch /tmp/RCE #", "x")
# git config --get core.sshCommand  ->  touch /tmp/RCE
```

## Attack Chain
1. Entry: app calls config writer with attacker-controlled OPTION name: `set_value("core", "sshCommand = touch /tmp/RCE #", "x")`.
2. Check: `_assure_config_name_safe(option, "option")` @ config.py. Guard: regex matches only `[\r\n\x00]`; bracket/quote state machine is gated on `label=="section"`. Bypass proof: `=`,`#`,space pass → no `ValueError`.
3. Sink: `write_section` writes `"\tsshCommand = touch /tmp/RCE # = x\n"` (config.py:702).
4. Impact: git parses `core.sshCommand=touch /tmp/RCE` → arbitrary code execution on next git op.

## Bypass Evidence
Independently reproduced (gate harness): `set_value('core','sshCommand = touch <RCE> #','x')` → no `ValueError`; file line `sshCommand = touch <RCE> # = x`; `git config --get core.sshCommand` → `touch <RCE>` (rc=0). Also verified `core.hooksPath` via both `GitConfigParser` and `repo.config_writer()`. Fix-commit read: bracket/quote checks are inside `if label == "section"`; the `"option"` label is not covered.

## Affected Versions
`GitPython <= 3.1.57` (validator present verbatim on the latest release tag).

## Suggested Fix
Apply the section-name safety checks (reject `=`, `#`, `;`, `[`, `]`, whitespace) to the `"option"` label as well, or validate the fully-rendered config line after substitution.

---
Reported by **zx (Jace)** — GitHub: @manus-use

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-jm78-9fvv-mhgr
- https://github.com/gitpython-developers/GitPython/pull/2204
- https://github.com/gitpython-developers/GitPython/commit/a495ccd3b547ccd60b2187215823b72a9c0188bf
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.58
