# [M] Information Disclosure in TYPO3 extension sf_event_mgt

## Summary
Severity: Medium
Advisory: GHSA-g8rg-7rpr-cwr2
CVE: CVE-2020-25026
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-g8rg-7rpr-cwr2
Type: github-advisory

## Affected
- Packagist: `derhansen/sf_event_mgt` — affected >=0 <4.3.1
- Packagist: `derhansen/sf_event_mgt` — affected >=5.0.0 <5.1.1

## Details
A missing access check in the backend module allows an authenticated backend user to export participant data for events which the user does not have access to, resulting in Information Disclosure. 

Another missing access check in the backend module allows an authenticated backend user to send emails to event participants for events which the user does not have access to, resulting in Broken Access Control.

External reference: [https://typo3.org/security/advisory/typo3-ext-sa-2020-017](https://typo3.org/security/advisory/typo3-ext-sa-2020-017)

## References
- https://github.com/derhansen/sf_event_mgt/security/advisories/GHSA-g8rg-7rpr-cwr2
- https://nvd.nist.gov/vuln/detail/CVE-2020-25026
- https://github.com/derhansen/sf_event_mgt/commit/17edcbf608b252cc1123e1279f0735f6aa28fef4
- https://packagist.org/packages/derhansen/sf_event_mgt
- https://typo3.org/help/security-advisories
- https://typo3.org/security/advisory/typo3-ext-sa-2020-017
