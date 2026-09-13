# [H] NLTK vulnerable to Eval Injection via collocations CLI arguments

## Summary
Severity: High
Advisory: GHSA-848c-c2cx-j7qx
CVE: CVE-2025-71408
CWE: CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-25
Source: https://github.com/advisories/GHSA-848c-c2cx-j7qx
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.9.3

## Details
NLTK (Natural Language Toolkit) before version 3.9.3 contains an eval injection vulnerability in the nltk.collocations module that allows an attacker who controls command-line arguments to execute arbitrary Python code. When collocations.py is invoked directly, the __main__ block passes command-line arguments directly to eval() as suffixes of BigramAssocMeasures without allowlist validation or sanitization, enabling an attacker to supply a Python expression that escapes the intended attribute lookup and executes arbitrary code including OS commands via the os module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-71408
- https://github.com/nltk/nltk/pull/3465
- https://github.com/nltk/nltk/commit/66f14096d952ec8f04934f515e027534bd4eb0ac
- https://aydinnyunus.github.io/2026/06/07/command-injection-nltk-collocations-eval
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/releases/tag/3.9.3
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-3657.yaml
- https://www.vulncheck.com/advisories/nltk-eval-injection-via-collocations-py-command-line-arguments
