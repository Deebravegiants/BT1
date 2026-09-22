# [H] Alchemy Non-SMA and Webauthn Account Security Advisory

## Summary
Severity: High
Advisory: GHSA-56r6-ccm5-8hg3
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-56r6-ccm5-8hg3
Type: github-advisory

## Affected
- npm: `@account-kit/smart-contracts` — affected >=4.42.0 <4.52.0

## Details
### Impact
A potential security issue has been mitigated on old account deployment functions from the factory. Smart wallets in use on all existing supported networks are not impacted.
### Patches
Please direct creation of new wallets to either `createSemiModularAccount` on `AccountFactory.sol` or `createWebAuthnAccount` on `WebAuthnFactory.sol`.

## References
- https://github.com/alchemyplatform/modular-account/security/advisories/GHSA-56r6-ccm5-8hg3
- https://github.com/alchemyplatform/aa-sdk/commit/b343437a9e4a833c25fed7bc8785a815cbbae0ee
- https://github.com/alchemyplatform/modular-account/commit/2352c9b692935ba97d98619cb31ba1653eee241f
- https://github.com/alchemyplatform/modular-account
