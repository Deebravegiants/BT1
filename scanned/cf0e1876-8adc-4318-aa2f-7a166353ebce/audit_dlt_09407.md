# [?] Fix overflow in invoice amount setter.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-04-30
Source: https://github.com/lightningdevkit/rust-lightning/commit/0ea58d0713e1b20d46c44a3a078c7da5f299d3ca
Type: security-commit

## Details
Fix overflow in invoice amount setter.

## Patch
### lightning-invoice/src/lib.rs
```diff
@@ -577,7 +577,13 @@ impl<D: tb::Bool, H: tb::Bool, T: tb::Bool, C: tb::Bool, S: tb::Bool, M: tb::Boo
 
 	/// Sets the amount in millisatoshis. The optimal SI prefix is chosen automatically.
 	pub fn amount_milli_satoshis(mut self, amount_msat: u64) -> Self {
-		let amount = amount_msat * 10; // Invoices are denominated in "pico BTC"
+		let amount = match amount_msat.checked_mul(10) { // Invoices are denominated in "pico BTC"
+			Some(amt) => amt,
+			None => {
+				self.error = Some(CreationError::InvalidAmount);
+				return self
+			}
+		};
 		let biggest_possible_si_prefix = SiPrefix::values_desc()
 			.iter()
 			.find(|prefix| amount % prefix.multiplier() == 0)
```
