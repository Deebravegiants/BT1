# [M] Web2py Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gp69-xcm6-ffqj
CVE: CVE-2016-4808
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gp69-xcm6-ffqj
Type: github-advisory

## Affected
- PyPI: `web2py` — affected >=0 <2.14.6

## Details
Web2py versions 2.14.5 and below was affected by CSRF (Cross Site Request Forgery) vulnerability, which allows an attacker to trick a logged-in administrator into performing unwanted actions i.e An attacker can trick a victim into disable the installed application just by visiting a URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4808
- https://github.com/web2py/web2py
- https://www.exploit-db.com/exploits/39821
- http://packetstormsecurity.com/files/137070/Web2py-2.14.5-CSRF-XSS-Local-File-Inclusion.html
