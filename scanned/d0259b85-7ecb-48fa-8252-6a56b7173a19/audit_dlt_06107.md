# [H] Any whitelisted account can break the protocol by blocking setAssetAllowed()

## Summary
Severity: High
Chain: Smart contract
Component: VMEX
Published: 2023-06-20
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/28
Type: hats-finding

## Details
**Github username:** @8ahoz
**Submission hash (on-chain):** 0x8711e507759f48a25f42dc1d10858eddeb4d5018c95796f88c4ca1fa197f6293
**Severity:** high severity

**Description:**
## Description:
Whitelisted addresses that are allowed to create permissionless tranches can create tranches and call `claimTrancheId()` in `LendingPoolConfigurator.sol` which increases `totalTranches` number. The same number later used to iterate through all tranches on the protocol in `validateAssetAllowed()` which is used in `setAssetAllowed()` in `AssetsMapping.sol`

`setAssetAllowed()` is an important function used to enable assets on whole protocol by `onlyGlobalAdmin`.
If the `totalTranches` number is sufficiently high, the loop on `AssetsMapping:L68` will revert with OOG.

https://github.com/VMEX-finance/vmex/blob/b0dc00c5dd6bdcac05827128d14dcdc730f19e1c/packages/contracts/contracts/protocol/lendingpool/AssetMappings.sol#L68

## Attack scenario:
A whitelisted account that is allowed to create tranches will make a high number of calls to the `claimTrancheId()` and increase the `totalTranches` number to a sufficiently high number.
After that all calls to the `setAssetAllowed()` from the global admin will be blocked because of OOG errors.
