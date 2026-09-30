# [?] fix: saturate reward emission overflow instead of panicking in update_reward_infos

## Summary
Severity: Unknown
Chain: Solana
Component: raydium-io/raydium-clmm
Published: 2026-06-16
Source: https://github.com/raydium-io/raydium-clmm/commit/b4a362ef3bd298455fe13b7692257184d053764d
Type: security-commit

## Details
fix: saturate reward emission overflow instead of panicking in update_reward_infos

## Patch
### programs/amm/src/instructions/initialize_reward.rs
```diff
@@ -157,6 +157,8 @@ pub fn initialize_reward(
         ctx.accounts.funder_token_account.amount,
         reward_amount_with_transfer_fee
     );
+    // Single top-up must be < u64::MAX / 3
+    require_gt!(u64::MAX / 3, reward_amount);
 
     let mut pool_state = ctx.accounts.pool_state.load_mut()?;
     pool_state.initialize_reward(
```

### programs/amm/src/instructions/set_reward_params.rs
```diff
@@ -98,7 +98,8 @@ pub fn set_reward_params<'a, 'b, 'c: 'info, 'info>(
         )?
     };
 
-    // check reward total emissioned overflow, if overflow, return error
+    // Single top-up must be < u64::MAX / 3
+    require_gt!(u64::MAX / 3, reward_amount);
     reward_info
         .reward_total_emitted
         .checked_add(reward_amount)
@@ -197,7 +198,7 @@ fn normal_update(
         let emission_diff_x64 =
             emissions_per_second_x64.saturating_sub(reward_info.emissions_per_second_x64);
         reward_amount = U256::from(left_reward_time)
-            .mul_div_floor(
+            .mul_div_ceil(
                 U256::from(emission_diff_x64),
                 U256::from(fixed_point_64::Q64),
             )
@@ -207,7 +208,7 @@ fn normal_update(
 
         if extend_period > 0 {
             let reward_amount_diff = U256::from(extend_period)
-                .mul_div_floor(
+                .mul_div_ceil(
                     U256::from(reward_info.emissions_per_second_x64),
                     U256::from(fixed_point_64::Q64),
                 )
@@ -265,7 +266,7 @@ fn admin_update(
         let emission_diff_x64 =
             emissions_per_second_x64.saturating_sub(reward_info.emissions_per_second_x64);
         reward_amount = U256::from(left_reward_time)
-            .mul_div_floor(
+            .mul_div_ceil(
                 U256::from(emission_diff_x64),
                 U256::from(fixed_point_64::Q64),
             )
@@ -274,7 +275,7 @@ fn admin_update(
         reward_info.emissions_per_second_x64 = emissions_per_second_x64;
 
         let reward_amount_diff = U256::from(extend_period)
-            .mul_div_floor(
+            .mul_div_ceil(
                 U256::from(reward_info.emissions_per_second_x64),
                 U256::from(fixed_point_64::Q64),
             )
```

### programs/amm/src/states/pool.rs
```diff
@@ -358,21 +358,18 @@ impl PoolState {
                         U128::from(reward_info.emissions_per_second_x64),
                         U128::from(fixed_point_64::Q64),
                     )
-                    .unwrap_or(U128::zero())
-                    .as_u64();
+                    .unwrap_or(U128::zero());
 
                 let mut reward_growth_delta = U256::from(time_delta)
                     .mul_div_floor(
                         U256::from(reward_info.emissions_per_second_x64),
                         U256::from(self.liquidity),
                     )
                     .unwrap_or(U256::zero());
-
-                if let Some(new_total) = reward_info.reward_total_emitted.checked_add(reward_delta)
-                {
-                    reward_info.reward_total_emitted = new_total;
+                let remain = u64::MAX.saturating_sub(reward_info.reward_total_emitted);
+                if reward_delta <= U128::from(remain) {
+                    reward_info.reward_total_emitted += reward_delta.as_u64();
                 } else {
-                    let remain = u64::MAX.saturating_sub(reward_info.reward_total_emitted);
                     reward_info.reward_total_emitted = u64::MAX;
 
                     reward_growth_delta = U256::from(remain)
@@ -1053,7 +1050,11 @@ pub mod pool_test {
                 let pre_loaded = pool_state
                     .next_initialized_tick_array_start_index(&None, 0, zero_for_one)
                     .expect("pre-loaded variant must not error at the default-bitmap boundary");
-                assert_eq!(pre_loaded, None, "pre-loaded variant, zero_for_one={}", zero_for_one);
+                assert_eq!(
+                    pre_loaded, None,
+                    "pre-loaded variant, zero_for_one={}",
+                    zero_for_one
+                );
 
                 let lazy = pool_state
                     .next_tick_array_index_with_extension_info(None, 0, zero_for_one)
```
