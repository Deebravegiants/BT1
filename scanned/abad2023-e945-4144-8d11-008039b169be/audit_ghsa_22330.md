# [M] HTML Purifier allows remote attackers to obtain sensitive information

## Summary
Severity: Medium
Advisory: GHSA-jw86-5cjf-mv79
CVE: CVE-2011-3744
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jw86-5cjf-mv79
Type: github-advisory

## Affected
- Packagist: `ezyang/htmlpurifier` — affected >=0

## Details
HTML Purifier 4.2.0 allows remote attackers to obtain sensitive information via a direct request to a .php file, which reveals the installation path in an error message, as demonstrated by tests/PHPT/Reporter/SimpleTest.php and certain other files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3744
- https://github.com/ezyang/htmlpurifier
- http://code.google.com/p/inspathx/source/browse/trunk/paths_vuln/%21_README
- http://code.google.com/p/inspathx/source/browse/trunk/paths_vuln/htmlpurifier-4.2.0
- http://www.openwall.com/lists/oss-security/2011/06/27/6
