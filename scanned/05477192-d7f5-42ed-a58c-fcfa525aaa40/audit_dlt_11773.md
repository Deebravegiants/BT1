# [?] Merge pull request #2161 from AleoHQ/fix/reward-truncation-and-overflow

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-11-10
Source: https://github.com/AleoNet/snarkVM-test/commit/320ac64f15acb85ea8c2fb986faac669af5cb643
Type: security-commit

## Details
Merge pull request #2161 from AleoHQ/fix/reward-truncation-and-overflow

[TOB] Remove possible truncation in `block_reward`

## Patch
### ledger/block/src/helpers/target.rs
```diff
@@ -27,7 +27,7 @@ pub const fn block_reward(total_supply: u64, block_time: u16, coinbase_reward: u
     // Compute the expected block height at year 1.
     let block_height_at_year_1 = block_height_at_year(block_time, 1);
     // Compute the annual reward: (0.05 * S).
-    let annual_reward = (total_supply / 1000) * 50;
+    let annual_reward = total_supply / 20;
     // Compute the block reward: (0.05 * S) / H_Y1.
     let block_reward = annual_reward / block_height_at_year_1 as u64;
     // Return the sum of the block reward, coinbase reward, and transaction fees.
```
