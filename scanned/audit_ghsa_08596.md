# [M] GPT-Pilot contains a command injection vulnerability in the Executor.run() method

## Summary
Severity: Medium
Advisory: GHSA-m85w-whwh-qvfx
CVE: CVE-2026-31246
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-m85w-whwh-qvfx
Type: github-advisory

## Affected
- PyPI: `gpt-pilot` — affected >=0

## Details
GPT-Pilot thru commit 0819827ce20346ef5f25b3fe29293cb448840565 (2025-09-03) contains a command injection vulnerability (CWE-78) in the Executor.run() method. During project execution, when the system prompts the user to confirm or modify a command to be run, it accepts free-text input without proper validation. The user-supplied input is directly passed to asyncio.create_subprocess_shell() for execution. This allows an attacker to replace the intended command with arbitrary shell commands, leading to remote code execution with the privileges of the GPT-Pilot process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31246
- https://github.com/Pythagora-io/gpt-pilot
- https://www.notion.so/CVE-2026-31246-35d1e1393188812ea3c6c88ad28d3d57
