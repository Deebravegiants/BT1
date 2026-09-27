# [H] LoLLMS Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-jccx-m9v4-9hwh
CVE: CVE-2024-6982
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-jccx-m9v4-9hwh
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0 <11.0.0

## Details
A remote code execution vulnerability exists in the Calculate function of parisneo/lollms version 9.8. The vulnerability arises from the use of Python's `eval()` function to evaluate mathematical expressions within a Python sandbox that disables `__builtins__` and only allows functions from the `math` module. This sandbox can be bypassed by loading the `os` module using the `_frozen_importlib.BuiltinImporter` class, allowing an attacker to execute arbitrary commands on the server. The issue is fixed in version 9.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6982
- https://github.com/parisneo/lollms/commit/30e7eaba2ccfb751a81e7cb29fdef2ae8ffa6832
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/4f8e73ac-aaaf-4d5c-a6dd-58215b5a7fea
