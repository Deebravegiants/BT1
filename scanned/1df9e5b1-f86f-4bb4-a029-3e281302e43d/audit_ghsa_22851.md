# [M] Web2py Reflected XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pvcp-73cg-6f77
CVE: CVE-2016-4807
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pvcp-73cg-6f77
Type: github-advisory

## Affected
- PyPI: `web2py` — affected >=0

## Details
Web2py versions 2.14.5 and below was affected by Reflected XSS vulnerability, which allows an attacker to perform an XSS attack on logged in user (admin).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4807
- https://github.com/web2py/web2py
- https://www.exploit-db.com/exploits/39821
- http://packetstormsecurity.com/files/137070/Web2py-2.14.5-CSRF-XSS-Local-File-Inclusion.html
