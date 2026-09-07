# [C] Cache poisoning in drupal/core

## Summary
Severity: Critical
Advisory: GHSA-rjqg-3h9m-fx5x
CVE: CVE-2023-5256
CWE: CWE-200
Ecosystem: Packagist
Published: 2023-09-28
Source: https://github.com/advisories/GHSA-rjqg-3h9m-fx5x
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.7.0 <9.5.11
- Packagist: `drupal/core` — affected >=10.0.0 <10.0.11
- Packagist: `drupal/core` — affected >=10.1.0 <10.1.4

## Details
In certain scenarios, Drupal's JSON:API module will output error backtraces. With some configurations, this may cause sensitive information to be cached and made available to anonymous users, leading to privilege escalation.

This vulnerability only affects sites with the JSON:API module enabled, and can be mitigated by uninstalling JSON:API.

The core REST and contributed GraphQL modules are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5256
- https://github.com/drupal/core/commit/1cd2741c2b43f6ad1bdfc121b8d9ec3b87e70742
- https://github.com/drupal/core/commit/5495dc530e3acd056478245bfe1828210c6da7dc
- https://github.com/drupal/core/commit/d4fe67562ee3ea0d9ecb9672d2945d94c5633d24
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2023-006
