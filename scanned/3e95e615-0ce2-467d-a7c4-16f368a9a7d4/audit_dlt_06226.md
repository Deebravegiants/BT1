# [M] Solidity compiler version 0.8.13 contains vulnerabilities applicable to EtherFi

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-07
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/26
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0x8a56dce519b226f5a3c93538eeb51ec4f8dc135ea004a4f43247343252fb14ca
**Severity:** medium

**Description:**
## Description
The project uses solidity version 0.8.13 which contains bugs not yet fixed compared to a newer compiler version. The following bugs are mitigated in 0.8.14 & 0.8.15 release:
- [Bug when Copying Dirty Bytes Arrays to Storage](https://soliditylang.org/blog/2022/06/15/dirty-bytes-array-to-storage-bug/)
- [Size Check Bug in Nested Calldata Array ABI-Reencoding](https://soliditylang.org/blog/2022/05/17/calldata-reencode-size-check-bug/)
- [Bug Concerning Data Location during Inheritance](https://soliditylang.org/blog/2022/05/17/data-location-inheritance-bug/)

However the most important one is the optimizer bug that can have severe consequences via removing assembly blocks:
- [Optimizer Bug Regarding Memory Side Effects of Inline Assembly](https://soliditylang.org/blog/2022/06/15/inline-assembly-memory-side-effects-bug/)

 which only occur under specific conditions: optimizer must be enabled and use legacy compilation instead of --via-ir which are true for the current configuration of the project:

`foundry.toml`
```toml
1: [profile.default]
7: optimizer_runs = 2000
```

The following contracts compiled with `0.8.13` contain assembly blocks that might be vulnerable. Any newly introduced assembly blocks here are at risk of being removed by the compiler.
- [`src/EtherFiNode.sol`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/EtherFiNode.sol#L485-L487)
- [`src/RegulationManagerV2.sol`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/RegulationsManagerV2.sol#L57-L64)
- [`src/StakingManager.sol`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/StakingManager.sol#L349-L351)

It's worth to mention the project also has dependencies that use assembly blocks which might be vulnerable as well. Read the official disclosure by Certora: [Overly Optimistic Optimizer](https://medium.com/certora/overly-optimistic-optimizer-certora-bug-disclosure-2101e3f7994d).


## Recommendation
Consider using a more up to date solidity compiler version instead of `0.8.13`. In the future be mindful about compiler bugs, it's a good practice to read [Solidity release announcements](https://soliditylang.org/blog/) which highlight the previous bugs in older compiler versions.
