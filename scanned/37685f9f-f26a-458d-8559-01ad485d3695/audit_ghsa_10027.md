# [C] Agno is vulnerable to Eval Injection

## Summary
Severity: Critical
Advisory: GHSA-77rh-m34w-rv36
CVE: CVE-2026-35002
CWE: CWE-95
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-77rh-m34w-rv36
Type: github-advisory

## Affected
- PyPI: `agno` — affected >=0 <2.3.24

## Details
Agno versions prior to 2.3.24 contain an arbitrary code execution vulnerability in the model execution component that allows attackers to execute arbitrary Python code by manipulating the field_type parameter passed to eval(). Attackers can influence the field_type value in a FunctionCall to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35002
- https://github.com/agno-agi/agno/commit/cbf675521d4d2281925a051784a3b94172e56416
- https://github.com/agno-agi/agno
- https://github.com/agno-agi/agno/releases/tag/v2.3.24
- https://www.vulncheck.com/advisories/agno-field-type-eval-injection-arbitrary-code-execution
