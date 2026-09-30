# [?] difficulty: Fix caculate next target panic (#1066)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-08-07
Source: https://github.com/starcoinorg/starcoin/commit/c3451ed41ef0365ba8a3e67af792773aecf237f2
Type: security-commit

## Details
difficulty: Fix caculate next target panic (#1066)

## Patch
### consensus/src/difficulty.rs
```diff
@@ -56,6 +56,9 @@ pub fn get_next_work_required(chain: &dyn ChainReader, epoch: &EpochInfo) -> Res
     let mut avg_time: u64 = 0;
     let mut avg_target = U256::zero();
     let mut latest_block_index = 0;
+    if blocks.len() <= 1 {
+        return Ok(difficult_to_target(current_header.difficulty));
+    }
     let block_n = blocks.len() - 1;
     while latest_block_index < block_n {
         let solve_time =
```
