# [C] Code execution in pandasai

## Summary
Severity: Critical
Advisory: GHSA-5g73-69p4-7gvx
CVE: CVE-2024-23752
CWE: CWE-862, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-22
Source: https://github.com/advisories/GHSA-5g73-69p4-7gvx
Type: github-advisory

## Affected
- PyPI: `pandasai` — affected >=0

## Details
GenerateSDFPipeline in synthetic_dataframe in PandasAI (aka pandas-ai) through 1.5.17 allows attackers to trigger the generation of arbitrary Python code that is executed by SDFCodeExecutor. An attacker can create a dataframe that provides an English language specification of this Python code. NOTE: the vendor previously attempted to restrict code execution in response to a separate issue, CVE-2023-39660.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23752
- https://github.com/gventuri/pandas-ai/issues/868
- https://github.com/gventuri/pandas-ai
