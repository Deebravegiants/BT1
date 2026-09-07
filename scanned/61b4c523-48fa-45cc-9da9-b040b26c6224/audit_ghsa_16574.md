# [H] LoLLMS Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-pwc9-q4hj-pg8g
CVE: CVE-2024-4078
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-16
Source: https://github.com/advisories/GHSA-pwc9-q4hj-pg8g
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0 <9.5.0

## Details
A vulnerability in the parisneo/lollms, specifically in the `/unInstall_binding` endpoint, allows for arbitrary code execution due to insufficient sanitization of user input. The issue arises from the lack of path sanitization when handling the `name` parameter in the `unInstall_binding` function, allowing an attacker to traverse directories and execute arbitrary code by loading a malicious `__init__.py` file. This vulnerability affects the latest version of the software. The exploitation of this vulnerability could lead to remote code execution on the system where parisneo/lollms is deployed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4078
- https://github.com/parisneo/lollms/commit/7ebe08da7e0026b155af4f7be1d6417bc64cf02f
- https://github.com/parisneo/lollms
- https://huntr.com/bounties/a55a8c04-df44-49b2-bcfa-2a2b728a299d
