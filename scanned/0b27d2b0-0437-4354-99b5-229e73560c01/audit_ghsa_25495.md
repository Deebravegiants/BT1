# [C] Object state limitation has no effect

## Summary
Severity: Critical
Advisory: GHSA-5x4f-7xgq-r42x
CWE: CWE-281
Ecosystem: Packagist
Published: 2022-04-29
Source: https://github.com/advisories/GHSA-5x4f-7xgq-r42x
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-kernel` — affected >=7.5.0 <7.5.28

## Details
Object state limitation is a policy you can use in your roles to limit access to content based on specific object state values. Due to a flawed earlier update, these limitations were ineffective in releases made since February 16th 2022. They would grant access to the given content regardless of the object state. Depending on how your frontent is designed, knowing the URL to the content may or may not be required to access it. If you are using object state limitations in your roles, this issue is critical. Please apply the fix as soon as possible.

## References
- https://github.com/ezsystems/ezpublish-kernel/security/advisories/GHSA-5x4f-7xgq-r42x
- https://github.com/ezsystems/ezpublish-kernel/commit/133c33cbcaa330953d6283865153f3dfdc7a2e45
- https://developers.ibexa.co/security-advisories/ibexa-sa-2022-004-ineffective-object-state-limitation-and-unauthenticated-fastly-purge
- https://github.com/ezsystems/ezpublish-kernel
