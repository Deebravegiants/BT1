# [H] PHP OpenID Library Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-5qp6-78pr-gv8c
CVE: CVE-2013-4701
CWE: CWE-400
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5qp6-78pr-gv8c
Type: github-advisory

## Affected
- Packagist: `openid/php-openid` — affected >=0 <2.3.0
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.6

## Details
Auth/Yadis/XML.php in PHP OpenID Library 2.2.2 and earlier allows remote attackers to read arbitrary files, send HTTP requests to intranet servers, or cause a denial of service (CPU and memory consumption) via XRDS data containing an external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4701
- https://github.com/openid/php-openid/commit/625c16bb28bb120d262b3f19f89c2c06cb9b0da9
- https://github.com/FriendsOfPHP/security-advisories/blob/master/openid/php-openid/CVE-2013-4701.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2013-4701.yaml
- https://github.com/openid/php-openid
- https://typo3.org/security/advisory/typo3-core-sa-2014-002
- http://jvn.jp/en/jp/JVN24713981/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2013-000080
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00028.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00083.html
