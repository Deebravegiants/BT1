# [H] Refuel Autolab Eval Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-g2m8-f3x2-qprw
CVE: CVE-2024-27320
CWE: CWE-1236, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-12
Source: https://github.com/advisories/GHSA-g2m8-f3x2-qprw
Type: github-advisory

## Affected
- PyPI: `refuel-autolabel` — affected >=0.0.8

## Details
An arbitrary code execution vulnerability exists in versions 0.0.8 and newer of the Refuel Autolabel library because of the way its classification tasks handle provided CSV files. If a victim user creates a classification task using a maliciously crafted CSV file containing Python code, the code will be passed to an eval function which executes it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27320
- https://github.com/refuel-ai/autolabel
- https://github.com/refuel-ai/autolabel/blob/v0.0.16/src/autolabel/dataset/validation.py#L57-L79
- https://hiddenlayer.com/sai-security-advisory/2024-09-autolabel
