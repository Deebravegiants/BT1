# [H] XXE in PHPSpreadsheet due to incomplete fix for previous encoding issue

## Summary
Severity: High
Advisory: GHSA-vvwv-h69m-wg6f
CVE: CVE-2019-12331
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-20
Source: https://github.com/advisories/GHSA-vvwv-h69m-wg6f
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.8.0
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
PHPOffice PhpSpreadsheet before 1.8.0 has an XXE issue. The XmlScanner decodes the sheet1.xml from an .xlsx to utf-8 if something else than UTF-8 is declared in the header. This was a security measurement to prevent CVE-2018-19277 but the fix is not sufficient. By double-encoding the the xml payload to utf-7 it is possible to bypass the check for the string ?<!ENTITY? and thus allowing for an xml external entity processing (XXE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12331
- https://github.com/PHPOffice/PhpSpreadsheet/pull/1041
- https://github.com/PHPOffice/PhpSpreadsheet/commit/0e6238c69e863b58aeece61e48ea032696c6dccd
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpoffice/phpspreadsheet/CVE-2019-12331.yaml
- https://github.com/PHPOffice/PhpSpreadsheet
- https://github.com/PHPOffice/PhpSpreadsheet/blob/master/CHANGELOG.md#180---2019-07-01
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/1.8.0
- https://herolab.usd.de/security-advisories/usd-2019-0046
