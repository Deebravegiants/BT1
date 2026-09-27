# [H] Banks: Unsafe importlib.import_module of attacker-controlled Tool.import_path in CompletionExtension allows RCE

## Summary
Severity: High
Advisory: CVE-2026-61536
Aliases: GHSA-64vx-6h2c-rjh7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-61536
Type: osv

## Details
Banks generates meaningful LLM prompts using a simple template language. In versions prior to 2.4.3, banks parses Tool JSON objects from the rendered body of {% completion %} blocks and later resolves their import_path field through importlib.import_module(...) + getattr(...) to obtain the callable that handles a tool call. There is no allowlist or sanitization on import_path, so any importable Python attribute (e.g. os.system, subprocess.getoutput) can be selected. When the LLM emits a tool_calls entry whose function.name matches the attacker-supplied tool name, the resolved callable is invoked with kwargs decoded from tool_call.function.arguments, yielding arbitrary code execution in the banks-hosting process. This is distinct from GHSA-gphh-9q3h-jgpp / CVE-2026-44209. That advisory was fixed in 2.4.2 by switching src/banks/env.py from Environment to SandboxedEnvironment. The fix does not touch src/banks/extensions/completion.py, and the unsafe import + getattr chain still executes on 2.4.2. The malicious Tool JSON is plain text in the rendered template body — it requires no Jinja attribute access, so the sandbox is irrelevant. This issue has been fixed in version 2.4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61536.json
- https://github.com/masci/banks/security/advisories/GHSA-64vx-6h2c-rjh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-61536
