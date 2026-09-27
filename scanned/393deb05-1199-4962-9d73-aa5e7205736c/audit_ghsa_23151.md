# [M] CakePHP 1.3.7 allows remote attackers to obtain sensitive information via a direct request to a .php file

## Summary
Severity: Medium
Advisory: GHSA-r7p6-fr3x-r877
CVE: CVE-2011-3712
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r7p6-fr3x-r877
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=1.3.7 <1.3.8

## Details
CakePHP 1.3.7 allows remote attackers to obtain sensitive information via a direct request to a `.php` file, which reveals the installation path in an error message, as demonstrated by `dispatcher.php` and certain other files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3712
- https://github.com/cakephp/cakephp
- http://code.google.com/p/inspathx/source/browse/trunk/paths_vuln/%21_README
- http://code.google.com/p/inspathx/source/browse/trunk/paths_vuln/cakephp-1.3.7
- http://www.openwall.com/lists/oss-security/2011/06/27/6
