# [M] Plone XSS

## Summary
Severity: Medium
Advisory: GHSA-22jm-p2vv-j2hc
CVE: CVE-2016-7136
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-22jm-p2vv-j2hc
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=5.0.0
- PyPI: `Plone` — affected >=4.0.0

## Details
z3c.form in Plone CMS 5.x through 5.0.6 and 4.x through 4.3.11 allows remote attackers to conduct cross-site scripting (XSS) attacks via a crafted GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7136
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2017-59.yaml
- https://plone.org/security/hotfix/20160830/non-persistent-xss-in-plone-forms
- https://web.archive.org/web/20210625091607/http://www.securityfocus.com/bid/92752
- https://web.archive.org/web/20210625092107/http://www.securityfocus.com/archive/1/539572/100/0/threaded
- http://packetstormsecurity.com/files/139110/Plone-CMS-4.3.11-5.0.6-XSS-Traversal-Open-Redirection.html
- http://seclists.org/fulldisclosure/2016/Oct/80
- http://www.openwall.com/lists/oss-security/2016/09/05/4
- http://www.openwall.com/lists/oss-security/2016/09/05/5
