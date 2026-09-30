# [?] Merge pull request #183 from raydium-io/fix/overflow-panic-guards

## Summary
Severity: Unknown
Chain: Solana
Component: raydium-io/raydium-clmm
Published: 2026-06-24
Source: https://github.com/raydium-io/raydium-clmm/commit/f68fd4286821905b5d1f8a8762f0c51a7f33c578
Type: security-commit

## Details
Merge pull request #183 from raydium-io/fix/overflow-panic-guards

Fix/overflow panic guards

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

### programs/amm/src/states/tick_array.rs
```diff
@@ -404,31 +404,35 @@ impl TickState {
     pub fn has_liquidity(&self) -> bool {
         self.liquidity_gross > 0
     }
-    /// Get the output amount of a limit order
-    /// amount_in: the amount of the input token
-    /// zero_for_one: the direction of the input token
-    /// output amount is rounded down
-    pub fn get_limit_order_output(amount_in: u64, tick: i32, zero_for_one: bool) -> Result<u64> {
+
+    fn limit_order_output_u128(amount_in: u64, tick: i32, zero_for_one: bool) -> Result<U128> {
         let output_amount = if zero_for_one {
             let token_0_price_x64 = tick_math::get_price_at_tick(tick, false)?;
             // Convert token0 amount to token1 amount using token0 price
             // token1_amount = token0_amount * token_0_price_x64 / 2^64
-            U128::from(amount_in)
-                .mul_div_floor(token_0_price_x64, U128::from(fixed_point_64::Q64))
-                .ok_or(ErrorCode::CalculateOverflow)?
-                .as_u64()
+            U128::from(amount_in).mul_div_floor(token_0_price_x64, U128::from(fixed_point_64::Q64))
         } else {
             let token_0_price_x64 = tick_math::get_price_at_tick(tick, true)?;
             // Convert token1 amount to token0 amount using token1 price (1/token_0_price_x64)
             // token0_amount = token1_amount * 2^64 / token_0_price_x64
-            U128::from(amount_in)
-                .mul_div_floor(U128::from(fixed_point_64::Q64), token_0_price_x64)
-                .ok_or(ErrorCode::CalculateOverflow)?
-                .as_u64()
-        };
+            U128::from(amount_in).mul_div_floor(U128::from(fixed_point_64::Q64), token_0_price_x64)
+        }
+        .ok_or(ErrorCode::CalculateOverflow)?;
         Ok(output_amount)
     }
 
+    /// Get the output amount of a limit order
+    /// amount_in: the amount of the input token
+    /// zero_for_one: the direction of the input token
+    /// output amount is rounded down
+    pub fn get_limit_order_output(amount_in: u64, tick: i32, zero_for_one: bool) -> Result<u64> {
+        let output_amount = Self::limit_order_output_u128(amount_in, tick, zero_for_one)?;
+        if output_amount > U128::from(u64::MAX) {
+            return err!(ErrorCode::CalculateOverflow);
+        }
+        Ok(output_amount.as_u64())
+    }
+
     /// Given the output amount from a limit order, calculate the required input token amount
     /// the direction of the limit order is always opposite to the direction of the swap
     /// amount_out: the amount of the output token(limit order token)
@@ -441,16 +445,20 @@ impl TickState {
             U128::from(amount_out)
                 .mul_div_ceil(token_0_price_x64, U128::from(fixed_point_64::Q64))
                 .ok_or(ErrorCode::CalculateOverflow)?
-                .as_u64()
         } else {
             let token_0_price_x64 = tick_math::get_price_at_tick(tick, false)?;
             // token0_consumed = token1_executed * 2^64 / token_0_price_x64
             U128::from(amount_out)
                 .mul_div_ceil(U128::from(fixed_point_64::Q64), token_0_price_x64)
                 .ok_or(ErrorCode::CalculateOverflow)?
-                .as_u64()
         };
-        Ok(amount_in)
+        // Checked downcast: an overflowing input means the trade would require
+        // more than u64::MAX input tokens — physically impossible since token
+        // balances are u64 — so return an error rather than panicking.
+        if amount_in > U128::from(u64::MAX) {
+            return err!(ErrorCode::CalculateOverflow);
+        }
+        Ok(amount_in.as_u64())
     }
 
     pub fn limit_order_unfilled_amount(&self) -> Result<u64> {
@@ -486,14 +494,14 @@ impl TickState {
             } else {
                 result.amount_in = swap_amount;
             }
-            result.amount_out = TickState::get_limit_order_output(
+            let matched_output = TickState::limit_order_output_u128(
                 result.amount_in,
                 self.tick,
                 swap_direction_zero_for_one,
             )?;
             // If the amount of limit order tokens matched is greater than the total unfilled amount,
             // it means the input cannot be fully consumed, so recalculate the input and output amounts
-            if result.amount_out > total_unfilled_amount {
+            if matched_output > U128::from(total_unfilled_amount) {
                 result.amount_out = total_unfilled_amount;
                 result.amount_in = TickState::get_limit_order_input(
                     total_unfilled_amount,
@@ -510,6 +518,8 @@ impl TickState {
                         .ok_or(ErrorCode::CalculateOverflow)?;
                 }
                 // Fee from output will be calculated at the end
+            } else {
+                result.amount_out = matched_output.as_u64();
             }
         } else {
             // swap_amount is the desired net output (after fee deduction if fee is from output)
@@ -1653,4 +1663,203 @@ pub mod tick_array_test {
             assert_eq!(padding, unpack_padding);
         }
     }
+    mod limit_order_conversion_test {
+        use super::*;
+
+        // ---- Boundary / grid sweeps over the full input space ----
+
+        // Tick set biased to extremes, zero, ±1, the ~20x band, and both signs.
+        const SWEEP_TICKS: [i32; 11] = [
+            tick_math::MIN_TICK,
+            tick_math::MIN_TICK + 1,
+            -200_000,
+            -30_000,
+            -1,
+            0,
+            1,
+            30_000,
+            200_000,
+            tick_math::MAX_TICK - 1,
+            tick_math::MAX_TICK,
+        ];
+        // Amounts spanning 0, 1, decimal scales, and the u64 extremes.
+        const SWEEP_AMOUNTS: [u64; 11] = [
+            0,
+            1,
+            2,
+            1_000_000,
+            1_000_000_000,
+            1_000_000_000_000,
+            1_000_000_000_000_000,
+            1_000_000_000_000_000_000,
+            5_000_000_000_000_000_000,
+            u64::MAX - 1,
+            u64::MAX,
+        ];
+
+        /// `get_limit_order_output` / `get_limit_order_input` must NEVER panic for any
+        /// tick×amount×direction, and must return the exact value when it fits u64 or
+        /// a graceful Err otherwise — verified against an independent reference.
+        #[test]
+        fn test_limit_order_conversion_sweep_no_panic_and_correct() {
+            let q64 = U128::from(fixed_point_64::Q64);
+            let u64max = U128::from(u64::MAX);
+
+            for &tick in &SWEEP_TICKS {
+                for &amt in &SWEEP_AMOUNTS {
+                    for zfo in [true, false] {
+                        // ----- get_limit_order_output -----
+                        let raw_out = if zfo {
+                            let p = tick_math::get_price_at_tick(tick, false).unwrap();
+                            U128::from(amt).mul_div_floor(p, q64)
+                        } else {
+                            let p = tick_math::get_price_at_tick(tick, true).unwrap();
+                            U128::from(amt).mul_div_floor(q64, p)
+                        };
+                        let expect_out = match raw_out {
+                            Some(r) if r <= u64max => Some(r.as_u64()),
+                            _ => None, // overflow (None) or > u64::MAX => Err expected
+                        };
+                        let got = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
+                            TickState::get_limit_order_output(amt, tick, zfo)
+                        }));
+                        assert!(
+                            got.is_ok(),
+                            "get_limit_order_output PANICKED amt={amt} tick={tick} zfo={zfo}"
+                        );
+                        match (got.unwrap(), expect_out) {
+                            (Ok(v), Some(e)) => assert_eq!(
+                                v, e,
+                                "output value mismatch amt={amt} tick={tick} zfo={zfo}"
+                            ),
+                            (Err(_), None) => {}
+                            (g, e) => panic!(
+                                "output Ok/Err mismatch amt={amt} tick={tick} zfo={zfo}: got={g:?} expect={e:?}"
+                            ),
+                        }
+
+                        // ----- get_limit_order_input -----
+                        let raw_in = if zfo {
+                            let p = tick_math::get_price_at_tick(tick, true).unwrap();
+                            U128::from(amt).mul_div_ceil(p, q64)
+                        } else {
+                            let p = tick_math::get_price_at_tick(tick, false).unwrap();
+                            U128::from(amt).mul_div_ceil(q64, p)
+                        };
+                        let expect_in = match raw_in {
+                            Some(r) if r <= u64max => Some(r.as_u64()),
+                            _ => None,
+                        };
+                        let got = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
+                            TickState::get_limit_order_input(amt, tick, zfo)
+                        }));
+                        assert!(
+                            got.is_ok(),
+                            "get_limit_order_input PANICKED amt={amt} tick={tick} zfo={zfo}"
+                        );
+                        match (got.unwrap(), expect_in) {
+                            (Ok(v), Some(e)) => assert_eq!(
+                                v, e,
+                                "input value mismatch amt={amt} tick={tick} zfo={zfo}"
+                            ),
+                            (Err(_), None) => {}
+                            (g, e) => panic!(
+                                "input Ok/Err mismatch amt={amt} tick={tick} zfo={zfo}: got={g:?} expect={e:?}"
+                            ),
+                        }
+                    }
+                }
+            }
+        }
+
+        /// Pin the exact u64::MAX crossover: at `threshold` the value still fits, at
+        /// `threshold + 1` it must flip to Err — the off-by-one a point test misses.
+        #[test]
+        fn test_limit_order_conversion_u64_threshold_boundary() {
+            let q64 = U128::from(fixed_point_64::Q64);
+            let u64max = U128::from(u64::MAX);
+
+            // Positive ticks: output multiplies by ~price, so it overflows as amount grows.
+            for &tick in &[1, 30_000, 200_000] {
+                let p = tick_math::get_price_at_tick(tick, false).unwrap();
+                // largest amt with floor(amt*p/Q64) <= u64::MAX
+                let threshold = u64max.mul_div_floor(q64, p).unwrap().as_u64();
+                for amt in [
+                    threshold.saturating_sub(1),
+                    threshold,
+                    threshold.saturating_add(1),
+                ] {
+                    let r = TickState::get_limit_order_output(amt, tick, true);
+                    let raw = U128::from(amt).mul_div_floor(p, q64).unwrap();
+                    if raw <= u64max {
+                        assert_eq!(r.unwrap(), raw.as_u64(), "tick={tick} amt={amt}");
+                    } else {
+                        assert!(r.is_err(), "tick={tick} amt={amt} expected graceful Err");
+                    }
+                }
+            }
+        }
+
+        /// `match_limit_order` must never panic and must never report a fill larger than
+        /// the available unfilled amount, across all directions, fee modes and bounds.
+        #[test]
+        fn test_match_limit_order_grid_no_panic_and_bounded() {
+            let swap_amounts: [u64; 7] = [
+                0,
+                1,
+                1_000_000,
+                1_000_000_000_000,
+                1_000_000_000_000_000_000,
+                5_000_000_000_000_000_000,
+                u64::MAX,
+            ];
+            let orders_amounts: [u64; 5] =
+                [0, 1, 1_000_000, 1_000_000_000_000_000_000, u64::MAX - 2];
+            let fee_rates: [u32; 2] = [0, 10_000];
+
+            for &tick in &SWEEP_TICKS {
+                for &swap_amount in &swap_amounts {
+                    for &orders_amount in &orders_amounts {
+                        // part_filled == 0, so total unfilled == orders_amount.
+                        for zfo in [true, false] {
+                            for is_base_input in [true, false] {
+                                for is_fee_on_input in [true, false] {
+                                    for &fee_rate in &fee_rates {
+                                        let outcome = std::panic::catch_unwind(
+                                            std::panic::AssertUnwindSafe(|| {
+                                                let mut t = build_tick(tick, 0, 0).take();
+                                                t.orders_amount = orders_amount;
+                                                t.order_phase = 1;
+                                                t.unfilled_ratio_x64 = fixed_point_64::Q64;
+                                                t.match_limit_order(
+                                                    swap_amount,
+                                                    zfo,
+                                                    is_base_input,
+                                                    fee_rate,
+                                                    is_fee_on_input,
+                                                )
+                                            }),
+                                        );
+                                        assert!(
+                                            outcome.is_ok(),
+                                            "match_limit_order PANICKED: tick={tick} swap={swap_amount} orders={orders_amount} zfo={zfo} base={is_base_input} feeon={is_fee_on_input} fee={fee_rate}"
+                                        );
+                                        if let Ok(Ok(res)) = outcome {
+                                            assert!(
+                                                res.amount_out <= orders_amount,
+                                                "fill {} exceeds unfilled {} at tick={tick} swap={swap_amount} zfo={zfo} base={is_base_input}",
+                                                res.amount_out,
+                                                orders_amount
+                                            );
+                                        }
+                                    }
+                                }
+                            }
+                        }
+                    }
+                }
+            }
+        }
+    }
+
 }
```
