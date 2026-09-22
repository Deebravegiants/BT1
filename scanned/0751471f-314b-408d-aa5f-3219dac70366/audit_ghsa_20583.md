# [H] Classic Buffer Overflow in pyo

## Summary
Severity: High
Advisory: GHSA-5f5c-687x-g5qm
CVE: CVE-2021-41499
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-07
Source: https://github.com/advisories/GHSA-5f5c-687x-g5qm
Type: github-advisory

## Affected
- PyPI: `pyo` — affected >=0 <1.0.3

## Details
Buffer Overflow Vulnerability exists in ajaxsoundstudio.com in Pyo < 1.03 in the Server_debug function, which allows remote attackers to conduct DoS attacks by deliberately passing on an overlong audio file name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41499
- https://github.com/belangeo/pyo/issues/222
- https://github.com/belangeo/pyo
