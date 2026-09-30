# [?] fix calculate fee overflow bug

## Summary
Severity: Unknown
Chain: Solana
Component: raydium-io/raydium-clmm
Published: 2022-10-05
Source: https://github.com/raydium-io/raydium-clmm/commit/c3f9b412b45b2f11531f239db02c7931ec29019c
Type: security-commit

## Details
fix calculate fee overflow bug

## Patch
### programs/amm/src/instructions/increase_liquidity.rs
```diff
@@ -151,7 +151,7 @@ pub fn calculate_latest_token_fees(
         U128::from(fee_growth_inside_latest_x64.saturating_sub(fee_growth_inside_last_x64))
             .mul_div_floor(U128::from(liquidity), U128::from(fixed_point_64::Q64))
             .unwrap()
-            .as_u64();
+            .to_underflow_u64();
 
     last_total_fees.checked_add(fee_growth_delta).unwrap()
 }
```

### programs/amm/src/libraries/full_math.rs
```diff
@@ -78,6 +78,9 @@ pub trait MulDiv<RHS = Self> {
     /// # }
     /// ```
     fn mul_div_ceil(self, num: RHS, denom: RHS) -> Option<Self::Output>;
+
+    /// Return u64 not out of bounds
+    fn to_underflow_u64(self) -> u64;
 }
 
 pub trait Upcast {
@@ -122,6 +125,10 @@ impl MulDiv for u64 {
             Some(r.as_u64())
         }
     }
+
+    fn to_underflow_u64(self) -> u64 {
+        self
+    }
 }
 
 impl MulDiv for U128 {
@@ -146,6 +153,14 @@ impl MulDiv for U128 {
             Some(r.as_u128())
         }
     }
+
+    fn to_underflow_u64(self) -> u64 {
+        if self < U128::from(u64::MAX) {
+            self.as_u64()
+        } else {
+            0
+        }
+    }
 }
 
 impl MulDiv for U256 {
@@ -170,6 +185,14 @@ impl MulDiv for U256 {
             Some(r)
         }
     }
+
+    fn to_underflow_u64(self) -> u64 {
+        if self < U256::from(u64::MAX) {
+            self.as_u64()
+        } else {
+            0
+        }
+    }
 }
 
 #[cfg(test)]
```

### programs/amm/src/states/protocol_position.rs
```diff
@@ -70,12 +70,12 @@ impl ProtocolPositionState {
             U128::from(fee_growth_inside_0_x64.saturating_sub(self.fee_growth_inside_0_last_x64))
                 .mul_div_floor(U128::from(self.liquidity), U128::from(fixed_point_64::Q64))
                 .unwrap()
-                .as_u64();
+                .to_underflow_u64();
         let tokens_owed_1 =
             U128::from(fee_growth_inside_1_x64.saturating_sub(self.fee_growth_inside_1_last_x64))
                 .mul_div_floor(U128::from(self.liquidity), U128::from(fixed_point_64::Q64))
                 .unwrap()
-                .as_u64();
+                .to_underflow_u64();
 
         // Update the position
         if liquidity_delta != 0 {
@@ -91,10 +91,7 @@ impl ProtocolPositionState {
             self.token_fees_owed_1 = self.token_fees_owed_1.checked_add(tokens_owed_1).unwrap();
         }
         #[cfg(feature = "enable-log")]
-        msg!(
-            "protocol position reward_growths_inside:{:?}",
-            reward_growths_inside
-        );
+        msg!("protocol position reward_growths_inside:{:?}", reward_growths_inside);
         self.update_reward_growths_inside(reward_growths_inside);
         Ok(())
     }
```
