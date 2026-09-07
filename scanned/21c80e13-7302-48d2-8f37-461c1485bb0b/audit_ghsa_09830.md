# [C] PraisonAI has critical RCE via `type: job` workflow YAML

## Summary
Severity: Critical
Advisory: GHSA-vc46-vw85-3wvm
CVE: CVE-2026-40288
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-vc46-vw85-3wvm
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.5.140
- PyPI: `PraisonAI` — affected >=0 <4.5.139

## Details
`praisonai workflow run <file.yaml>` loads untrusted YAML and if `type: job` executes steps through `JobWorkflowExecutor` in job_workflow.py.

This supports:
- `run:` → shell command execution via `subprocess.run()`
- `script:` → inline Python execution via `exec()`
- `python:` → arbitrary Python script execution

A malicious YAML file can execute arbitrary host commands.

### Affected Code
- workflow.py → `action_run()`
- job_workflow.py → `_exec_shell()`, `_exec_inline_python()`, `_exec_python_script()`

### PoC
Create `exploit.yaml`:

```yaml
type: job
name: exploit
steps:
  - name: write-file
    run: python -c "open('pwned.txt','w').write('owned')"
```

Run:

```bash
praisonai workflow run exploit.yaml
```

### Reproduction Steps
1. Save the YAML above as `exploit.yaml`.
2. Execute `praisonai workflow run exploit.yaml`.
3. Confirm `pwned.txt` appears in the working directory.

### Impact
Remote or local attacker-supplied workflow YAML can execute arbitrary host commands and code, enabling full system compromise in CI or shared deployment contexts.

**Reporter:** Lakshmikanthan K (letchupkt)

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-vc46-vw85-3wvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40288
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.139
