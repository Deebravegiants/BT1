# [C] pymetasploit3 vulnerable to command injection in console.run_module_with_output()

## Summary
Severity: Critical
Advisory: GHSA-qpc3-8vqg-8g6w
CVE: CVE-2026-5463
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-qpc3-8vqg-8g6w
Type: github-advisory

## Affected
- PyPI: `pymetasploit3` — affected >=0

## Details
Command injection vulnerability in console.run_module_with_output() in pymetasploit3 through version 1.0.6 allows attackers to inject newline characters into module options such as RHOSTS. This breaks the intended command structure and causes the Metasploit console to execute additional unintended commands, potentially leading to arbitrary command execution and manipulation of Metasploit sessions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5463
- https://github.com/DanMcInerney/pymetasploit3
- https://pypi.org/project/pymetasploit3
