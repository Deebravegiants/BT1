# [?] Fix overflow in lightning-invoice amount_pico_btc.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-04-30
Source: https://github.com/lightningdevkit/rust-lightning/commit/c6ae9288b9e6cfba7c1e95b0f840435b561ec15d
Type: security-commit

## Details
Fix overflow in lightning-invoice amount_pico_btc.

## Patch
### lightning-invoice/src/lib.rs
```diff
@@ -1068,9 +1068,10 @@ impl RawBolt11Invoice {
 		find_all_extract!(self.known_tagged_fields(), TaggedField::PrivateRoute(ref x), x).collect()
 	}
 
+	/// Returns `None` if no amount is set or on overflow.
 	pub fn amount_pico_btc(&self) -> Option<u64> {
-		self.hrp.raw_amount.map(|v| {
-			v * self.hrp.si_prefix.as_ref().map_or(1_000_000_000_000, |si| { si.multiplier() })
+		self.hrp.raw_amount.and_then(|v| {
+			v.checked_mul(self.hrp.si_prefix.as_ref().map_or(1_000_000_000_000, |si| { si.multiplier() }))
 		})
 	}
 
```
