# [M] Drupal Full Path Disclosure

## Summary
Severity: Medium
Advisory: GHSA-mg8j-w93w-xjgc
CVE: CVE-2024-45440
CWE: CWE-209, CWE-497
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-mg8j-w93w-xjgc
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=10.3.0 <10.3.6
- Packagist: `drupal/drupal` — affected >=11.0.0 <11.0.5
- Packagist: `drupal/core-recommended` — affected >=10.3.0 <10.3.6
- Packagist: `drupal/core-recommended` — affected >=11.0.0 <11.0.5
- Packagist: `drupal/core` — affected >=10.3.0 <10.3.6
- Packagist: `drupal/core` — affected >=11.0.0 <11.0.5
- Packagist: `drupal/drupal` — affected >=8.0.0 <10.2.9
- Packagist: `drupal/core-recommended` — affected >=8.0.0 <10.2.9
- Packagist: `drupal/core` — affected >=8.0.0 <10.2.9

## Details
`core/authorize.php` in Drupal 11.x-dev allows Full Path Disclosure (even when error logging is None) if the value of `hash_salt` is `file_get_contents` of a file that does not exist.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45440
- https://github.com/github/advisory-database/pull/4827
- https://github.com/drupal/drupal
- https://senscybersecurity.nl/CVE-2024-45440-Explained
- https://www.drupal.org/project/drupal/issues/3457781
- https://www.drupal.org/project/drupal/releases/10.2.9
- https://www.drupal.org/project/drupal/releases/10.3.6
- https://www.drupal.org/project/drupal/releases/11.0.5
- https://www.exploit-db.com/exploits/52266
