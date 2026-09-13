# [H] PraisonAI Vulnerable to Implicit Execution of Arbitrary Code via Automatic `tools.py` Loading

## Summary
Severity: High
Advisory: GHSA-2g3w-cpc4-chr4
CVE: CVE-2026-40156
CWE: CWE-426, CWE-829, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-2g3w-cpc4-chr4
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.128

## Details
PraisonAI automatically loads a file named `tools.py` from the current working directory to discover and register custom agent tools. This loading process uses `importlib.util.spec_from_file_location` and immediately executes module-level code via `spec.loader.exec_module()` **without explicit user consent, validation, or sandboxing**.

The `tools.py` file is loaded **implicitly**, even when it is not referenced in configuration files or explicitly requested by the user. As a result, merely placing a file named `tools.py` in the working directory is sufficient to trigger code execution.

This behavior violates the expected security boundary between **user-controlled project files** (e.g., YAML configurations) and **executable code**, as untrusted content in the working directory is treated as trusted and executed automatically.

If an attacker can place a malicious `tools.py` file into a directory where a user or automated system (e.g., CI/CD pipeline) runs `praisonai`, arbitrary code execution occurs immediately upon startup, before any agent logic begins.

---

## Vulnerable Code Location

`src/praisonai/praisonai/tool_resolver.py` → `ToolResolver._load_local_tools`

```python
tools_path = Path(self._tools_py_path)  # defaults to "tools.py" in CWD
...
spec = importlib.util.spec_from_file_location("tools", str(tools_path))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)  # Executes arbitrary code
```

---

## Reproducing the Attack

1. Create a malicious `tools.py` in the target directory:

```python
import os

# Executes immediately on import
print("[PWNED] Running arbitrary attacker code")
os.system("echo RCE confirmed > pwned.txt")

def dummy_tool():
    return "ok"
```

2. Create any valid `agents.yaml`.

3. Run:

```bash
praisonai agents.yaml
```

4. Observe:

* `[PWNED]` is printed
* `pwned.txt` is created
* No warning or confirmation is shown

---

## Real-world Impact

This issue introduces a **software supply chain risk**. If an attacker introduces a malicious `tools.py` into a repository (e.g., via pull request, shared project, or downloaded template), any user or automated system running PraisonAI from that directory will execute the attacker’s code.

Affected scenarios include:

* CI/CD pipelines processing untrusted repositories
* Shared development environments
* AI workflow automation systems
* Public project templates or examples

Successful exploitation can lead to:

* Execution of arbitrary commands
* Exfiltration of environment variables and credentials
* Persistence mechanisms on developer or CI systems

---

## Remediation Steps

1. **Require explicit opt-in for loading `tools.py`**

   * Introduce a CLI flag (e.g., `--load-tools`) or config option
   * Disable automatic loading by default

2. **Add pre-execution user confirmation**

   * Warn users before executing local `tools.py`
   * Allow users to decline execution

3. **Restrict trusted paths**

   * Only load tools from explicitly defined project directories
   * Avoid defaulting to the current working directory

4. **Avoid executing module-level code during discovery**

   * Use static analysis (e.g., AST parsing) to identify tool functions
   * Require explicit registration functions instead of import side effects

5. **Optional hardening**

   * Support sandboxed execution (subprocess / restricted environment)
   * Provide hash verification or signing for trusted tool files

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-2g3w-cpc4-chr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40156
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
