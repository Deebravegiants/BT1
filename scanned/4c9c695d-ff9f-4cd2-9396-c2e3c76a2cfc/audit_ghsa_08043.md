# [M] web2py has an Open Redirect Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rf8c-3f5p-xv45
CVE: CVE-2026-25198
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-rf8c-3f5p-xv45
Type: github-advisory

## Affected
- PyPI: `web2py` — affected >=0 <3.1.1

## Details
web2py versions 2.27.1-stable+timestamp.2023.11.16.08.03.57 and prior contain an Open Redirect vulnerability. If this vulnerability is exploited, the user may be redirected to an arbitrary website when accessing a specially crafted URL. As a result, the user may become a victim of a phishing attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25198
- https://github.com/web2py/web2py/commit/b4e1ddbd6d40fb30863f6263a67bcdf411a0c6df
- https://github.com/web2py/web2py
- https://github.com/web2py/web2py/releases
- https://jvn.jp/en/jp/JVN46925341
- https://web2py.com
