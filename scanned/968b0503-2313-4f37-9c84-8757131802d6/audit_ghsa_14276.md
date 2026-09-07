# [C] Access bypass in Drupal core

## Summary
Severity: Critical
Advisory: GHSA-8849-cv9f-vccm
CVE: CVE-2023-31250
Ecosystem: Packagist
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-8849-cv9f-vccm
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=10.0.0 <10.0.8
- Packagist: `drupal/core` — affected >=9.5.0 <9.5.8
- Packagist: `drupal/core` — affected >=9.0.0 <9.4.14
- Packagist: `drupal/core` — affected >=7.0.0 <7.96

## Details
The file download facility doesn't sufficiently sanitize file paths in certain situations. This may result in users gaining access to private files that they should not have access to. Some sites may require configuration changes following this security release. Review the release notes for your Drupal version if you have issues accessing private files after updating.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31250
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2023-005
