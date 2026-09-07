# [M] Open redirect in web2py

## Summary
Severity: Medium
Advisory: GHSA-w4r7-vm83-q2c7
CVE: CVE-2023-22432
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-06
Source: https://github.com/advisories/GHSA-w4r7-vm83-q2c7
Type: github-advisory

## Affected
- PyPI: `web2py` — affected >=0 <2.23.1

## Details
Open redirect vulnerability exists in web2py versions prior to 2.23.1. When using the tool, a web2py user may be redirected to an arbitrary website by accessing a specially crafted URL. As a result, the user may become a victim of a phishing attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22432
- https://jvn.jp/en/jp/JVN78253670
- http://web2py.com
- http://web2py.com/init/default/download
