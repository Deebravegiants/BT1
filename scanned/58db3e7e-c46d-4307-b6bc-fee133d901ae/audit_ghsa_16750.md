# [M] Denial of Service in extension "Code Highlight" (codehighlight)

## Summary
Severity: Medium
Advisory: GHSA-65xh-hh78-6454
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L/E:F/RL:O/RC:C (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-65xh-hh78-6454
Type: github-advisory

## Affected
- Packagist: `brotkrueml/codehighlight` — affected >=0 <2.7.0

## Details
The codehighlight extension bundles a vulnerable version of the 3rd party JavaScript component “prism” which is known to be vulnerable against Regular expression Denial of Service (ReDoS).

## References
- https://github.com/brotkrueml/codehighlight/commit/c43d46ef571a3b94a6240782423ce04bfada7fd8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/brotkrueml/codehighlight/2021-11-10-1.yaml
- https://github.com/brotkrueml/codehighlight
- https://typo3.org/security/advisory/typo3-ext-sa-2021-016
