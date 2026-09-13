# [H] NLTK AllowlistUnpickler dotted-name validation bypass allows remote code execution

## Summary
Severity: High
Advisory: GHSA-5gh2-94qg-qppq
CVE: CVE-2026-71513
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-22
Source: https://github.com/advisories/GHSA-5gh2-94qg-qppq
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=3.10.0 <3.10.3

## Details
NLTK before 3.10.3 contains a remote code execution vulnerability in AllowlistUnpickler that validates only the pickle module string and not the global name, allowing attackers to resolve dotted names by attribute traversal to callables outside the allowlisted namespace. Attackers can craft untrusted transition-parser models that execute arbitrary commands when TransitionParser.parse loads the model through allowlisted_pickle_load.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-71513
- https://github.com/nltk/nltk/commit/c3e37113742a1ebeeb4f2ca58941f320f98805ea
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/blob/v3.10.2/nltk/picklesec.py#L119-L124
- https://www.vulncheck.com/advisories/nltk-through-remote-code-execution-via-allowlistunpickler-dotted-name-bypass
