# [M] Open redirect in web2py

## Summary
Severity: Medium
Advisory: GHSA-cgrj-xjm7-9q27
CVE: CVE-2022-33146
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-28
Source: https://github.com/advisories/GHSA-cgrj-xjm7-9q27
Type: github-advisory

## Affected
- PyPI: `web2py` — affected >=0 <2.22.5

## Details
Open redirect vulnerability in web2py versions prior to 2.22.5 allows a remote attacker to redirect a user to an arbitrary web site and conduct a phishing attack by having a user to access a specially crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33146
- https://github.com/web2py/web2py/commit/a181b855a43cb8b479d276b082cfcde385768451
- https://github.com/web2py/web2py/commit/d9805606f88f00c0be56438247605cefde73e14e#diff-c1d01f37ee54d813815718760b9c4d7b274e2be7ad18f65552cd564336ab593bR110
- https://github.com/web2py/web2py
- https://jvn.jp/en/jp/JVN02158640/index.html
- http://web2py.com
