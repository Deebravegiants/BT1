# [?] binary-option: Fixed three integer overflows (#3121)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2022-12-08
Source: https://github.com/solana-labs/solana-program-library/commit/8922d20697f1d771f68af93cdf3b692702f9a007
Type: security-commit

## Details
binary-option: Fixed three integer overflows (#3121)

* Fixed three integer overflows in binary-option

* Update binary-option/program/src/state.rs

Change error type to AmountOverflow.

Co-authored-by: Jon Cinque <jon.cinque@gmail.com>

Co-authored-by: Jon Cinque <jon.cinque@gmail.com>

## Patch
### binary-option/program/src/error.rs
```diff
@@ -28,6 +28,8 @@ pub enum BinaryOptionError {
     PublicKeysShouldBeUnique,
     #[error("TradePricesIncorrect")]
     TradePricesIncorrect,
+    #[error("AmountOverflow")]
+    AmountOverflow,
 }
 
 impl From<BinaryOptionError> for ProgramError {
```

### binary-option/program/src/processor.rs
```diff
@@ -234,7 +234,10 @@ pub fn process_trade(
     ];
 
     // Validate data
-    if buy_price + sell_price != u64::pow(10, binary_option.decimals as u32) {
+    let total_price = buy_price
+        .checked_add(sell_price)
+        .ok_or(BinaryOptionError::TradePricesIncorrect)?;
+    if total_price != u64::pow(10, binary_option.decimals as u32) {
         return Err(BinaryOptionError::TradePricesIncorrect.into());
     }
     if binary_option.settled {
@@ -411,7 +414,7 @@ pub fn process_trade(
                 seeds,
             )?;
             if n > n_b + n_s {
-                binary_option.increment_supply(n - n_b - n_s);
+                binary_option.increment_supply(n - n_b - n_s)?;
             } else {
                 binary_option.decrement_supply(n - n_b - n_s)?;
             }
@@ -707,7 +710,10 @@ pub fn process_collect(program_id: &Pubkey, accounts: &[AccountInfo]) -> Program
         seeds,
     )?;
     if reward > 0 {
-        let amount = (reward * escrow_account.amount) / binary_option.circulation;
+        let amount = reward
+            .checked_mul(escrow_account.amount)
+            .ok_or(BinaryOptionError::AmountOverflow)?;
+        let amount = amount / binary_option.circulation;
         spl_token_transfer_signed(
             token_program_info,
             escrow_account_info,
```

### binary-option/program/src/state.rs
```diff
@@ -28,8 +28,12 @@ impl BinaryOption {
         Ok(binary_option)
     }
 
-    pub fn increment_supply(&mut self, n: u64) {
-        self.circulation += n;
+    pub fn increment_supply(&mut self, n: u64) -> ProgramResult {
+        self.circulation = self
+            .circulation
+            .checked_add(n)
+            .ok_or(BinaryOptionError::AmountOverflow)?;
+        Ok(())
     }
 
     pub fn decrement_supply(&mut self, n: u64) -> ProgramResult {
```
