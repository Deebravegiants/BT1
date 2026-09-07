# [M] eZ Platform Prevent accepting app.php in URL in Platform.sh

## Summary
Severity: Medium
Advisory: GHSA-qhjc-hg94-245v
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-qhjc-hg94-245v
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform` — affected >=2.5.0 <2.5.4
- Packagist: `ezsystems/ezplatform` — affected >=1.13.0 <1.13.5.1
- Packagist: `ezsystems/ezplatform` — affected >=1.7.0 <1.7.9.1

## Details
The recommended rewrite rules in eZ Platform prevent users from including the front-controller script (normally "app.php") in URLs. This prevents certain vulnerabilities related to caching. However, this is not possible when using eZ Platform Cloud (i.e. running eZ Platform on the Platform.sh cloud service), nor can it be done within the .platform.app.yaml configuration file. Therefore we need to reject such requests in the application itself. This advisory adds the prevention within the front controller script itself.
 
If you use eZ Platform Cloud / Platform.sh we recommend that you install this security update as soon as possible. It is distributed via Composer as ezsystems/ezplatform 1.7.9.1, and 1.13.5.1, and 2.5.4. This is the commit: https://github.com/ezsystems/ezplatform/commit/34ce86722b36a172e587068fe64a84faa7320cc2

## References
- https://github.com/ezsystems/ezplatform/commit/34ce86722b36a172e587068fe64a84faa7320cc2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezplatform/2019-09-03-2.yaml
- https://github.com/ezsystems/ezplatform
- https://share.ez.no/community-project/security-advisories/ezsa-2019-007-prevent-accepting-app.php-in-url-in-platform.sh
