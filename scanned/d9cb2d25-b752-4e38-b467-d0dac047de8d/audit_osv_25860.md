# [M] era-compiler-vyper First Immutable Variable Initialization vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-46232
Aliases: GHSA-h8jv-969m-94r4
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-46232
Type: osv

## Details
era-compiler-vyper is the EraVM Vyper compiler for zkSync Era, a layer 2 rollup that uses zero-knowledge proofs to scale Ethereum. Prior to era-compiler-vype version 1.3.10, a bug prevented the initialization of the first immutable variable for Vyper contracts meeting certain criteria. The problem arises when there is a String or Array with more 256-bit words allocated than initialized. It results in the second word’s index unset, that is effectively set to 0, so the first immutable value with the actual 0 index is overwritten in the ImmutableSimulator. Version 1.3.10 fixes this issue by setting all indexes in advance. The problem will go away, but it will get more expensive if the user allocates a lot of uninitialized space, e.g. `String[4096]`. Upgrading and redeploying affected contracts is the only way of working around the issue.

## References
- https://github.com/matter-labs/era-system-contracts/blob/main/contracts/ImmutableSimulator.sol#L37
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46232.json
- https://github.com/matter-labs/era-compiler-vyper/security/advisories/GHSA-h8jv-969m-94r4
- https://nvd.nist.gov/vuln/detail/CVE-2023-46232
- https://github.com/matter-labs/era-compiler-vyper/commit/8be305a1b9c68d0fd47dad3434224ed85944ca25
