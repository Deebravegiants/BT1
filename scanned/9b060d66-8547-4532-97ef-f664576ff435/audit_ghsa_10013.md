# [H] PraisonAI Vulnerable to RCE via Automatic tools.py Import

## Summary
Severity: High
Advisory: GHSA-g985-wjh9-qxxc
CVE: CVE-2026-40287
CWE: CWE-426, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-g985-wjh9-qxxc
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.5.140
- PyPI: `PraisonAI` — affected >=0 <4.5.139

## Details
PraisonAI automatically imports `./tools.py` from the current working directory when launching certain components. This includes call.py, tool_resolver.py, and CLI tool-loading paths.

A malicious tools.py placed in the process working directory is executed immediately, allowing arbitrary Python code execution in the host environment.

### Affected Code
- call.py → `import_tools_from_file()`
- tool_resolver.py → `_load_local_tools()`
- tools.py → local tool import flow
- 

### PoC
Create tools.py in the directory where PraisonAI is launched:

```python
# tools.py
import os
os.system("echo pwned > /tmp/pwned.txt")
```

Run any PraisonAI component that loads local tools, for example:

```bash
praisonai workflow run safe.yaml
```

### Reproduction Steps
1. Create a malicious tools.py in the current working directory.
2. Start PraisonAI or invoke a CLI command that loads local tools.
3. Verify that `/tmp/pwned.txt` or the malicious command output exists.

### Impact
An attacker who can place or influence tools.py in the working directory can execute arbitrary code in the PraisonAI process, compromising the host and any connected data.

**Reporter:** Lakshmikanthan K (letchupkt)

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-g985-wjh9-qxxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-40287
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.139
