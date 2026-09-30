# [M] CakePHP directory traversal vulnerability allows remote attackers to read arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-rw73-xmpv-j5x2
CVE: CVE-2006-5031
CWE: CWE-22
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-rw73-xmpv-j5x2
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=1.0.1.2708 <1.1.8.3544

## Details
Directory traversal vulnerability in `app/webroot/js/vendors.php` in Cake Software Foundation CakePHP before 1.1.8.3544 allows remote attackers to read arbitrary files via a `..` (dot dot) in the file parameter, followed by a filename ending with `%00` and a `.js` filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-5031
- https://exchange.xforce.ibmcloud.com/vulnerabilities/29115
- https://github.com/cakephp/cakephp
- http://cakeforge.org/frs/shownotes.php?release_id=134
- http://secunia.com/advisories/22040
- http://www.gulftech.org/?node=research&article_id=00114-09212006
- http://www.securityfocus.com/bid/20150
