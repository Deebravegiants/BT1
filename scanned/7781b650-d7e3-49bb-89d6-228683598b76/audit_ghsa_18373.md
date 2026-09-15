# [H] TkEasyGUI Affected by Uncontrolled Search Path Element Issue

## Summary
Severity: High
Advisory: GHSA-ph2w-cx28-vhrq
CVE: CVE-2025-55671
CWE: CWE-427
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-05
Source: https://github.com/advisories/GHSA-ph2w-cx28-vhrq
Type: github-advisory

## Affected
- PyPI: `TkEasyGUI` — affected >=0 <1.0.22

## Details
Uncontrolled search path element issue exists in TkEasyGUI versions prior to v1.0.22. If this vulnerability is exploited, arbitrary code may be executed with the privilege of running the program.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55671
- https://github.com/kujirahand/tkeasygui-python
- https://github.com/kujirahand/tkeasygui-python/releases/tag/v1.0.22
- https://jvn.jp/en/jp/JVN48739895
