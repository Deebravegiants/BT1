# [H] pandasai vulnerable to prompt injection

## Summary
Severity: High
Advisory: GHSA-w832-v3c6-m6rg
CVE: CVE-2023-39660
CWE: CWE-94
Ecosystem: PyPI
Published: 2023-08-21
Source: https://github.com/advisories/GHSA-w832-v3c6-m6rg
Type: github-advisory

## Affected
- PyPI: `pandasai` — affected >=0 <0.8.1

## Details
An issue in Gaberiele Venturi pandasai v.0.8.0 and before allows a remote attacker to execute arbitrary code via a crafted request to the prompt function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39660
- https://github.com/gventuri/pandas-ai/issues/399
- https://github.com/gventuri/pandas-ai/pull/409
- https://github.com/gventuri/pandas-ai/commit/3aac79be8fc1d18b53d66a566adddbbdd2b38ad5
- https://github.com/gventuri/pandas-ai
