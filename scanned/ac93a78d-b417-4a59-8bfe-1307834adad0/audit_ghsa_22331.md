# [M] Plone vulnerable to filesystem information leak

## Summary
Severity: Medium
Advisory: GHSA-m7f9-65wr-pwch
CVE: CVE-2016-7135
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-m7f9-65wr-pwch
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=5.0 <5.0.7
- PyPI: `Plone` — affected >=4.2 <4.3.12

## Details
Directory traversal vulnerability in Plone CMS 5.x through 5.0.6 and 4.2.x through 4.3.11 allows remote administrators to read arbitrary files via a `..` (dot dot) in the path parameter in a getFile action to `Plone/++theme++barceloneta/@@plone.resourceeditor.filemanager-actions`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7135
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2017-58.yaml
- https://plone.org/security/hotfix/20160830/filesystem-information-leak
- https://pypi.org/project/Products.PloneHotfix20160830
- https://web.archive.org/web/20200227230348/http://www.securityfocus.com/bid/92752
- https://web.archive.org/web/20201207134911/http://www.securityfocus.com/archive/1/539572/100/0/threaded
- http://packetstormsecurity.com/files/139110/Plone-CMS-4.3.11-5.0.6-XSS-Traversal-Open-Redirection.html
- http://seclists.org/fulldisclosure/2016/Oct/80
- http://www.openwall.com/lists/oss-security/2016/09/05/4
- http://www.openwall.com/lists/oss-security/2016/09/05/5
- http://www.securityfocus.com/archive/1/539572/100/0/threaded
- http://www.securityfocus.com/bid/92752
