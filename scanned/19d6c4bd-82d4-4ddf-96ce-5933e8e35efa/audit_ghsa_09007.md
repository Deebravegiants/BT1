# [C] llm CLI tool contains a code injection vulnerability via `--functions` command-line argument

## Summary
Severity: Critical
Advisory: GHSA-g76p-4vg5-f4qh
CVE: CVE-2026-31236
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-g76p-4vg5-f4qh
Type: github-advisory

## Affected
- PyPI: `llm` — affected >=0

## Details
The llm CLI tool thru 0.27.1 contains a critical code injection vulnerability via its --functions command-line argument. This argument is intended to allow users to provide custom Python function definitions. However, the tool directly executes the provided code using the unsafe exec() function without any sanitization, sandboxing, or security restrictions. An attacker can exploit this by crafting a malicious llm command with arbitrary Python code in the --functions argument and using social engineering to trick a victim into running it. This leads to arbitrary code execution on the victim's system, potentially granting the attacker full control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31236
- https://github.com/simonw/llm
- https://www.notion.so/CVE-2026-31236-35d1e139318881a4a0f1fffcf671f7e3
