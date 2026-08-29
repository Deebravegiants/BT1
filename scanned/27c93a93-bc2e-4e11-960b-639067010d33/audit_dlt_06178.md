# [M] Wrong manage of time in HoprChannels contract

## Summary
Severity: Medium
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-12
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/31
Type: hats-finding

## Details
**Github username:** @Rotcivegaf
**Submission hash (on-chain):** 0xe8c24d473904841d17d964b57f434f042f46ce2975a8c33197438f2c6975004f
**Severity:** medium

**Description:**
## Description

In the contract **HoprChannels** the `TWENTY_FOUR_HOURS` is calculate in milliseconds an the timestamp of the EVM is in seconds

https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/8822abcfa5348b8e1f45c1d9fa5a5135090e0622/packages/ethereum/contracts/src/Channels.sol#L16

In the abstract contract **HoprLedger** the `snapshotInterval` is defined with `TWENTY_FOUR_HOURS`(24 * 60 * 60 * 1000) instead of 24 hours it is 24000 hours, the `latestSnapshotRoot` will update with wrong delta

https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/8822abcfa5348b8e1f45c1d9fa5a5135090e0622/packages/ethereum/contracts/src/Ledger.sol#L90

## Recommendation 

Calculate the `TWENTY_FOUR_HOURS` in seconds:

```diff
@@ -13,7 +13,7 @@ import { HoprLedger } from "./Ledger.sol";
 import { HoprMultiSig } from "./MultiSig.sol";
 import { HoprNodeSafeRegistry } from "./node-stake/NodeSafeRegistry.sol";
 
-uint256 constant TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000; // in milliseconds
+uint256 constant TWENTY_FOUR_HOURS = 24 * 60 * 60; // in milliseconds
 
 uint256 constant INDEX_SNAPSHOT_INTERVAL = TWENTY_FOUR_HOURS;
```
