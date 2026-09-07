# [H] Plone vulnerable to cross-site request forgery

## Summary
Severity: High
Advisory: GHSA-p3qm-44cf-f8qx
CVE: CVE-2015-7293
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p3qm-44cf-f8qx
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <5.0a1

## Details
Multiple cross-site request forgery (CSRF) vulnerabilities in Zope Management Interface 4.3.7 and earlier, and Plone before 5.x.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7293
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2017-51.yaml
- https://plone.org/security/hotfix/20151006
- https://pypi.python.org/pypi/plone4.csrffixes
- https://www.exploit-db.com/exploits/38411
- http://hyp3rlinx.altervista.org/advisories/AS-ZOPE-CSRF.txt
- http://packetstormsecurity.com/files/133889/Zope-Management-Interface-4.3.7-Cross-Site-Request-Forgery.html
