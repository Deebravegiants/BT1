# [H] Slim vulnerable to PHP object injection

## Summary
Severity: High
Advisory: GHSA-74mf-vjpg-9xh7
CVE: CVE-2015-2171
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-74mf-vjpg-9xh7
Type: github-advisory

## Affected
- Packagist: `slim/slim` — affected >=0 <2.6.0

## Details
Middleware/SessionCookie.php in Slim before 2.6.0 allows remote attackers to conduct PHP object injection attacks and execute arbitrary PHP code via crafted session data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2171
- https://github.com/slimphp/Slim/issues/1034
- https://github.com/slimphp/Slim/commit/9fa651474eb4d3bb0ce40dd5a55c51bb861c2658
- https://github.com/FriendsOfPHP/security-advisories/blob/master/slim/slim/CVE-2015-2171.yaml
- https://github.com/slimphp/Slim
- https://web.archive.org/web/20200229032229/http://www.securityfocus.com/bid/70087
- http://seclists.org/fulldisclosure/2015/Mar/16
- http://www.slimframework.com/2015/03/01/version-260.html
