# [M] derhansen/sf_event_mgt vulnerable to Broken Access Control in Backend Module 

## Summary
Severity: Medium
Advisory: GHSA-4576-pgh2-g34j
CVE: CVE-2024-24751
CWE: CWE-284, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-4576-pgh2-g34j
Type: github-advisory

## Affected
- Packagist: `derhansen/sf_event_mgt` — affected >=7.0.0 <7.4.0

## Details
The existing access control check for events in the backend module got broken during the update of the extension to TYPO3 12.4, because the `RedirectResponse` from the `$this->redirect()` function was never handled.

## References
- https://github.com/derhansen/sf_event_mgt/security/advisories/GHSA-4576-pgh2-g34j
- https://nvd.nist.gov/vuln/detail/CVE-2024-24751
- https://github.com/derhansen/sf_event_mgt/commit/a08c2cd48695c07e462d15eeb70434ddc0206e4c
- https://github.com/derhansen/sf_event_mgt
