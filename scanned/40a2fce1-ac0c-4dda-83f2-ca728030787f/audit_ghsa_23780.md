# [M] Plone Open Redirect Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-69vh-662j-v988
CVE: CVE-2016-7137
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-69vh-662j-v988
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=5.0
- PyPI: `Plone` — affected >=4.0
- PyPI: `Plone` — affected >=3.3

## Details
Multiple open redirect vulnerabilities in Plone CMS 5.x through 5.0.6, 4.x through 4.3.11, and 3.3.x through 3.3.6 allow remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via a URL in the referer parameter to (1) `%2b%2bgroupdashboard%2b%2bplone.dashboard1%2bgroup/%2b/portlets.Actions` or (2) `folder/%2b%2bcontextportlets%2b%2bplone.footerportlets/%2b /portlets.Actions` or the (3) `came_from` parameter to `/login_form`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7137
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2017-60.yaml
- https://plone.org/security/hotfix/20160830/open-redirection-in-plone
- https://web.archive.org/web/20210625091607/http://www.securityfocus.com/bid/92752
- https://web.archive.org/web/20210625092107/http://www.securityfocus.com/archive/1/539572/100/0/threaded
- http://packetstormsecurity.com/files/139110/Plone-CMS-4.3.11-5.0.6-XSS-Traversal-Open-Redirection.html
- http://seclists.org/fulldisclosure/2016/Oct/80
- http://www.openwall.com/lists/oss-security/2016/09/05/4
- http://www.openwall.com/lists/oss-security/2016/09/05/5
- http://www.securityfocus.com/archive/1/539572/100/0/threaded
- http://www.securityfocus.com/bid/92752
