# [M] Insecure Unserialize Vulnerability in FLOW3

## Summary
Severity: Medium
Advisory: GHSA-m2hp-5x78-74mg
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-m2hp-5x78-74mg
Type: github-advisory

## Affected
- Packagist: `typo3/flow` — affected >=1.0.0 <1.0.4

## Details
Due to a missing signature (HMAC) for a request argument, an attacker could unserialize arbitrary objects within FLOW3.

To our knowledge it is neither possible to inject code through this vulnerability, nor are there exploitable objects within the FLOW3 Base Distribution. However, there might be exploitable objects within user applications.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/flow/2012-03-28.yaml
- https://github.com/neos/flow
- https://www.neos.io/blog/flow-sa-2012-001.html
