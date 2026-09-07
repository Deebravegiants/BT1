# [H] OpenZeppelin Contracts vulnerable to ECDSA signature malleability

## Summary
Severity: High
Advisory: GHSA-4h98-2769-gh6h
CVE: CVE-2022-35961
CWE: CWE-354
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-4h98-2769-gh6h
Type: github-advisory

## Affected
- npm: `@openzeppelin/contracts` — affected >=4.1.0 <4.7.3
- npm: `@openzeppelin/contracts-upgradeable` — affected >=4.1.0 <4.7.3

## Details
### Impact

The functions `ECDSA.recover` and `ECDSA.tryRecover` are vulnerable to a kind of signature malleability due to accepting EIP-2098 compact signatures in addition to the traditional 65 byte signature format. This is only an issue for the functions that take a single `bytes` argument, and not the functions that take `r, v, s` or `r, vs` as separate arguments.

The potentially affected contracts are those that implement signature reuse or replay protection by marking the signature itself as used rather than the signed message or a nonce included in it. A user may take a signature that has already been submitted, submit it again in a different form, and bypass this protection.

### Patches

The issue has been patched in 4.7.3.


### For more information

If you have any questions or comments about this advisory, or need assistance deploying a fix, email us at [security@openzeppelin.com](mailto:security@openzeppelin.com).

## References
- https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-4h98-2769-gh6h
- https://nvd.nist.gov/vuln/detail/CVE-2022-35961
- https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3610
- https://github.com/OpenZeppelin/openzeppelin-contracts/commit/d693d89d99325f395182e4f547dbf5ff8e5c3c87
- https://github.com/OpenZeppelin/openzeppelin-contracts
- https://github.com/OpenZeppelin/openzeppelin-contracts/releases/tag/v4.7.3
