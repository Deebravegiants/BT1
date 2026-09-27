# [H] Superduper: Remote code execution via unsafe eval in superduper query parsing

## Summary
Severity: High
Advisory: GHSA-2799-6g5r-mmc7
CVE: CVE-2026-31225
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-2799-6g5r-mmc7
Type: github-advisory

## Affected
- PyPI: `superduper-framework` — affected >=0

## Details
The superduper project thru v0.10.0 contains a critical remote code execution vulnerability in its query parsing component. The _parse_op_part() function in query.py uses the unsafe eval() function to dynamically evaluate user-supplied query operands without proper sanitization or restriction. Although the function attempts to limit the execution context by providing a restricted global namespace, it does not block access to dangerous built-in functions. A remote attacker can exploit this by submitting a specially crafted query string containing Python code that imports modules (e.g., os) and executes arbitrary system commands, leading to complete compromise of the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31225
- https://github.com/superduper-io/superduper
- https://www.notion.so/CVE-2026-31225-35d1e1393188814f99b5eec7b6517190
