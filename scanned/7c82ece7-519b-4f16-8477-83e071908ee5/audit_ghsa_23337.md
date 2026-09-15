# [M] CiviCRM SQL injection vulnerability via Quick Search API

## Summary
Severity: Medium
Advisory: GHSA-4465-r2hg-v4rj
CVE: CVE-2013-4662
CWE: CWE-89
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4465-r2hg-v4rj
Type: github-advisory

## Affected
- Packagist: `civicrm/civicrm-core` — affected >=4.2.0 <4.2.9
- Packagist: `civicrm/civicrm-core` — affected >=4.3.0 <4.3.3

## Details
The Quick Search API in CiviCRM 4.2.0 through 4.2.9 and 4.3.0 through 4.3.3 allows remote authenticated users to bypass the validation layer and conduct SQL injection attacks via a direct request to the "second layer" of the API, related to contact.getquick.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4662
- https://civicrm.org/advisory/civi-sa-2013-004-limited-sql-injection-quick-search-api
- https://github.com/civicrm/civicrm-core
- https://issues.civicrm.org/jira/browse/CRM-12765
