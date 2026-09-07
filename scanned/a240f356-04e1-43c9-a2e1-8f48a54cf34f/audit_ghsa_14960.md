# [H] ydata cross-site scripting

## Summary
Severity: High
Advisory: GHSA-2r57-2mrh-ggjv
CVE: CVE-2024-37063
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-2r57-2mrh-ggjv
Type: github-advisory

## Affected
- PyPI: `ydata-profiling` — affected >=3.7.0

## Details
A cross-site scripting (XSS) vulnerability in versions 3.7.0 or newer of Ydata's ydata-profiling open-source library allows for payloads to be run when a maliocusly crafted report is viewed in the browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37063
- https://github.com/ydataai/ydata-profiling
- https://hiddenlayer.com/sai-security-advisory/ydata-june2024
