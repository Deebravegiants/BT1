# [M] ForkCMS Directory Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4x28-j85r-668q
CVE: CVE-2012-1207
CWE: CWE-22
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4x28-j85r-668q
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <3.2.5

## Details
Directory traversal vulnerability in `frontend/core/engine/javascript.php` in Fork CMS 3.2.4 and possibly other versions before 3.2.5 allows remote attackers to read arbitrary files via a `..` (dot dot) in the module parameter to `frontend/js.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1207
- https://github.com/forkcms/forkcms/commit/a9986b86c53de0582248b39605660fbba0c21a29
- https://exchange.xforce.ibmcloud.com/vulnerabilities/73169
- https://github.com/forkcms/forkcms
- https://web.archive.org/web/20120401204340/http://www.securityfocus.com/bid/51972
- http://packetstormsecurity.org/files/109709/Fork-CMS-3.2.4-Cross-Site-Scripting-Local-File-Inclusion.html
- http://www.fork-cms.com/blog/detail/fork-cms-3-2-5-released
