# [C] PandasAI vulnerable to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-8fp9-43pw-56vw
CVE: CVE-2023-39661
CWE: CWE-74, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-15
Source: https://github.com/advisories/GHSA-8fp9-43pw-56vw
Type: github-advisory

## Affected
- PyPI: `pandasai` — affected >=0

## Details
An issue in pandas-ai v.0.8.1 and before allows a remote attacker to execute arbitrary code via the `_is_jailbreak` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39661
- https://github.com/gventuri/pandas-ai/issues/410
- https://github.com/gventuri/pandas-ai
