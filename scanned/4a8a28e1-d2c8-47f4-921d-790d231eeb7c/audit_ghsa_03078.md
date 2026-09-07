# [H] constructEvent does not verify header

## Summary
Severity: High
Advisory: GHSA-4g53-vp7q-gfjv
Ecosystem: npm
Published: 2021-05-28
Source: https://github.com/advisories/GHSA-4g53-vp7q-gfjv
Type: github-advisory

## Affected
- npm: `@worker-tools/stripe-webhook` — affected >=0 <1.1.4

## Details
### Impact
Anyone verifying a Stripe webhook request via this library's `constructEvent` function.

### Patches
Upgrade to 1.1.4. 

### Workarounds
Use `await verifyHeader(...)` directly instead of `constructEvent`.

### References
https://github.com/worker-tools/stripe-webhook/issues/1

## References
- https://github.com/worker-tools/stripe-webhook/security/advisories/GHSA-4g53-vp7q-gfjv
