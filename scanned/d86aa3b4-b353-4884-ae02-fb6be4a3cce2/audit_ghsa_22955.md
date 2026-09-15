# [M] PHPExcel vulnerable to XXE attacks through libxml

## Summary
Severity: Medium
Advisory: GHSA-28rm-rj57-qjpv
CVE: CVE-2014-2054
CWE: CWE-611
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-28rm-rj57-qjpv
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpexcel` — affected >=0 <1.8.0

## Details
PHPExcel before 1.8.0, as used in ownCloud Server before 5.0.15 and 6.0.x before 6.0.2, does not disable external entity loading in libxml, which allows remote attackers to read arbitrary files, cause a denial of service, or possibly have other impact via an XML External Entity (XXE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2054
- https://github.com/PHPOffice/PHPExcel/commit/e04bf7ed091b0a72d028eacf26d770b485d4e897
- https://github.com/PHPOffice/PHPExcel
- https://github.com/PHPOffice/PHPExcel/blob/2b601574975acfb9d4378a788ed5f2b747958095/changelog.txt#L120
- https://github.com/PHPOffice/PHPExcel/blob/develop/changelog.txt
- http://owncloud.org/about/security/advisories/oC-SA-2014-006
