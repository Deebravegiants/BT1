# [H] x402 SDK vulnerable in outdated versions in resource servers for builders

## Summary
Severity: High
Advisory: GHSA-3j63-5h8p-gf7c
Ecosystem: npm
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-3j63-5h8p-gf7c
Type: github-advisory

## Affected
- npm: `x402` — affected >=0 <0.5.2
- npm: `x402-next` — affected >=0 <0.5.2
- npm: `x402-express` — affected >=0 <0.5.2
- npm: `x402-hono` — affected >=0 <0.5.2

## Details
### Impact
There is a security vulnerability in outdated versions of the x402 SDK. This does not directly affect users' keys, smart contracts, or funds.

This primarily impacts builders working on resource servers.

### Patches
Please update to the following package versions:
* x402 >= 0.5.2
* x402-next >= 0.5.2
* x402-express >= 0.5.2
* x402-hono >= 0.5.2

## References
- https://github.com/coinbase/x402/security/advisories/GHSA-3j63-5h8p-gf7c
- https://github.com/coinbase/x402
