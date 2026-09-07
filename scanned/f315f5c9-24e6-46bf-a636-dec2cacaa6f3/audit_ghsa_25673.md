# [M] Zope XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vh6g-786f-hxxp
CVE: CVE-2011-4924
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-vh6g-786f-hxxp
Type: github-advisory

## Affected
- PyPI: `zope` — affected >=3.1.1 <3.7.3
- PyPI: `zope2` — affected >=0 <2.12.22
- PyPI: `zope2` — affected >=2.13.0a1 <2.13.12

## Details
Cross-site scripting (XSS) vulnerability in Zope 2.8.x before 2.8.12, 2.9.x before 2.9.12, 2.10.x before 2.10.11, 2.11.x before 2.11.6, and 2.12.x before 2.12.3, 3.1.1 through 3.4.1. allows remote attackers to inject arbitrary web script or HTML via vectors related to the way error messages perform sanitization. NOTE: this issue exists because of an incomplete fix for CVE-2010-1104

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4924
- https://github.com/zopefoundation/Zope/commit/37e4ea774acc668f6b430a45a6ab1e359710f590
- https://github.com/zopefoundation/Zope/commit/a0655194cb39ad88ce3323a3e489927c5f979c44
- https://access.redhat.com/security/cve/cve-2011-4924
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-4924
- https://github.com/zopefoundation/Zope
- https://security-tracker.debian.org/tracker/CVE-2011-4924
- http://www.openwall.com/lists/oss-security/2012/01/19/16
- http://www.openwall.com/lists/oss-security/2012/01/19/17
- http://www.openwall.com/lists/oss-security/2012/01/19/18
- http://www.openwall.com/lists/oss-security/2012/01/19/19
