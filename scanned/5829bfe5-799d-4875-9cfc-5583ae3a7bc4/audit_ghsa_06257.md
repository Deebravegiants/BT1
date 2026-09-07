# [H] Glances: Incomplete fix of CVE-2026-32608: action-template sanitizer is bypassed by nested stat values (process 'cmdline') → OS command injection

## Summary
Severity: High
Advisory: GHSA-73wf-9vmv-5pv9
CVE: CVE-2026-62982
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-73wf-9vmv-5pv9
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=4.5.2 <4.5.6

## Details
## Summary
CVE-2026-32608 ("Command Injection via Process Names in Action Command Templates") was fixed (commit `5680a5d`) by adding `_sanitize_mustache_dict`, which replaces the shell operators `&&`, `|`, `>>`, `>` with spaces in the values rendered into action command templates.

The sanitizer only processes **top-level string** values (`if isinstance(v, str)`). Attacker-controlled **nested** values — most notably a process's **`cmdline`, which Glances exposes as a `list`** and which is fully attacker-controlled via argv — are passed through **unsanitized**. Because the Mustache renderer (`chevron`) does **not** HTML-escape the pipe character `|`, a `|` embedded in such a nested value survives into the rendered command and is then interpreted by `secure_popen` (which still interprets `&&`/`|`/`>` by default, `allow_operators=True`), re-introducing the exact command injection the CVE was meant to close.

## Details
The fix (`glances/actions.py`):
```python
_SHELL_OPERATORS = ('&&', '|', '>>', '>')                     # line 25

def _sanitize_mustache_dict(mustache_dict):                   # line 28
    ...
    for k, v in mustache_dict.items():
        if isinstance(v, str):                                # line 40  <-- ONLY top-level strings
            for op in _SHELL_OPERATORS:
                v = v.replace(op, ' ')
            safe[k] = v
        else:
            safe[k] = v                                       # nested list/dict passed VERBATIM
    return safe
```
Render + sink (`glances/actions.py:104-111`):
```python
safe_dict = _sanitize_mustache_dict(mustache_dict)
cmd_full  = chevron.render(cmd, safe_dict)                    # chevron does NOT escape '|'
...
ret = secure_popen(cmd_full)                                 # secure_popen(cmd, allow_operators=True)
```
`secure_popen` (`glances/secure.py:17`, default `allow_operators=True`) splits the command by `&&`, then `__secure_popen` interprets `|` (pipe to a new process) and `>` (write output to a file). A surviving `|` therefore launches an attacker-named second process.

**The attacker-controlled nested value — `cmdline`.** The action `mustache_dict` is the per-item plugin stat (`glances/plugins/plugin/model.py:931` `mustache_dict = item`, then `:943` `self.actions.run(..., mustache_dict=mustache_dict)`). For the processlist plugin, each `item` contains `cmdline`, a **list** of the process arguments, set by the attacker simply by launching a process with chosen argv. The sanitizer's `isinstance(v, str)` test skips the list, so its elements reach `chevron.render` unmodified.

**Why the operator survives render.** `chevron`/Mustache HTML-escapes `& < > " '` for `{{var}}` (so `>` and `&&` are neutralized) but **does not escape `|`**. A pipe in the (unsanitized) nested value therefore reaches `secure_popen` intact and is interpreted.

**Parent-fix attribution (verified against the real diff of commit `5680a5d` / CVE-2026-32608):** that fix added exactly `_SHELL_OPERATORS`, `_sanitize_mustache_dict`, and the `_sanitize_mustache_dict(mustache_dict)` call — and the sanitizer's docstring explicitly claims to neutralize "user-controllable data (process names, container names, mount points, etc.)". It does so only for top-level strings; the list/dict case (`else: safe[k] = v`) was left unsanitized. This is therefore a genuine incomplete-fix gap, not a re-report of the patched (top-level string) vector.

## Proof of Concept
Lab-only, harmless (touches a marker file; non-destructive). Runs the real `glances` chain (`_sanitize_mustache_dict` → `chevron.render` → `secure_popen`) — see `poc/glances_nested_mustache_poc.py`.

Attacker process argv (the only attacker input): `cmdline = ['x', '|touch /tmp/glances_poc_marker', '#']`.
Admin action template (renders the offending process's cmdline): `echo ALERT {{#cmdline}}{{.}} {{/cmdline}}`.

Observed (confirmed on develop HEAD `92156d0`/4.5.6 and verified code-identical on v4.5.5):
```
cmdline after sanitizer : ['x', '|touch /tmp/glances_poc_marker', '#']   <- pipe survives
cmd_full -> secure_popen : 'echo ALERT x |touch /tmp/glances_poc_marker # '
[VULNERABLE] marker created -> /tmp/glances_poc_marker  (command injection executed)
```
Replacing `touch /tmp/...` with any command yields arbitrary execution in the Glances process context.

## Preconditions (stated honestly)
- A configured alert **action** whose command template **renders a nested stat field** (e.g. the process `cmdline` via a `{{#cmdline}}…{{/cmdline}}` section). Templates that render only **flat string** fields (`{{name}}`, `{{value}}`, `{{username}}`, `{{mnt_point}}`) are **not** affected — those values *are* sanitized.
- Glances running with privilege to enumerate the attacker's process (typically **root** in server/agent monitoring deployments) → privilege boundary crossed (`S:C`).

## Impact
A local unprivileged user gains OS command execution in the Glances security context (commonly root) — the same impact and threat model as the parent CVE-2026-32608, re-enabled for any action template that renders a nested stat field. The injection is reliable once the (admin-set) template references such a field.

## Suggested fix
- Sanitize **recursively** — apply the operator stripping to strings inside lists and dicts, not only top-level `str` values.
- And/or build the templated action as an argument list and run it via `secure_popen(..., allow_operators=False)` / `shell=False` without operator interpretation.
- And/or also strip the pipe `|` (and treat all `_SHELL_OPERATORS`) on every rendered string regardless of nesting; do not rely on Mustache HTML-escaping (it does not escape `|`).

## Credit
Ta Duc Thien

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-73wf-9vmv-5pv9
- https://github.com/nicolargo/glances/commit/ea4cf2f54f0d961e24aa0b24fff9584bab39db93
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.6
