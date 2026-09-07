# [C] Drupal Core Insufficient Contextual Links validation leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-jjx7-8462-w4m4
CWE: CWE-20
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-jjx7-8462-w4m4
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.5.8
- Packagist: `drupal/drupal` — affected >=8.6.0 <8.6.2

## Details
The Contextual Links module doesn't sufficiently validate the requested contextual links.
This vulnerability is mitigated by the fact that an attacker must have a role with the permission "access contextual links".

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/2018-10-17-5.yaml
- https://github.com/drupal/drupal
- https://www.drupal.org/sa-core-2018-006
