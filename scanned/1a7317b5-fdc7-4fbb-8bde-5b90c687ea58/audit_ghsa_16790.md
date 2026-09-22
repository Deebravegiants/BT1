# [M] amphp/artax Cookie leakage to wrong origins and non-restricted cookie acceptance

## Summary
Severity: Medium
Advisory: GHSA-gm98-g2wf-7c68
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-gm98-g2wf-7c68
Type: github-advisory

## Affected
- Packagist: `amphp/artax` — affected >=2 <2.0.6
- Packagist: `amphp/artax` — affected >=0 <1.0.6

## Details
In artax version before 1.0.6 and 2 before 2.0.6, cookies of `foo.bar.example.com` were leaked to `foo.bar`. Additionally, any site could set cookies for any other site. 
Artax fixed this issue by following newer browser implementations now. Cookies can only be set on domains higher or equal to the current domain, but not on any public suffixes.

## References
- https://github.com/amphp/artax/commit/25668b891d2bced567bd69611c7d18b6a93d5fc4
- https://github.com/amphp/artax/commit/accdadaf78f7a43305c3a97d6a964bbc550a555d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/amphp/artax/2017-05-09.yaml
- https://github.com/amphp/artax
- https://github.com/amphp/artax/releases/tag/v2.0.6
