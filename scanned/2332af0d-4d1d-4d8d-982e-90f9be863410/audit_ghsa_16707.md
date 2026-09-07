# [H] fuel/core ImageMagick driver does not escape all shell arguments.

## Summary
Severity: High
Advisory: GHSA-26hp-cgjj-m2j3
CWE: CWE-78
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-26hp-cgjj-m2j3
Type: github-advisory

## Affected
- Packagist: `fuel/core` — affected >=0 <1.8.0.4

## Details
This vulnerability may cause OS commands to be executed when you pass unvalidated image filenames containing specially crafted strings to the ImageMagick driver.

## References
- https://github.com/fuel/core/commit/95c134e9e087f3c4523fe6cd86ed4e9e1e7af91c
- https://fuelphp.com/security-advisories
- https://github.com/FriendsOfPHP/security-advisories/blob/master/fuel/core/2016-06-29-1.yaml
- https://github.com/fuel/core
