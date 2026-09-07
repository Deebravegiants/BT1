# [M] DSPy does not properly restrict file reads

## Summary
Severity: Medium
Advisory: GHSA-vvw2-h478-xwr3
CVE: CVE-2025-12695
CWE: CWE-653
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-04
Source: https://github.com/advisories/GHSA-vvw2-h478-xwr3
Type: github-advisory

## Affected
- PyPI: `dspy` — affected >=0

## Details
The overly permissive sandbox configuration in DSPy allows attackers to steal sensitive files in cases when users build an AI agent which consumes user input and uses the “PythonInterpreter” class.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12695
- https://github.com/stanfordnlp/dspy
- https://research.jfrog.com/vulnerabilities/dspy-sandbox-escape-arbitrary-file-read-jfsa-2025-001495652
