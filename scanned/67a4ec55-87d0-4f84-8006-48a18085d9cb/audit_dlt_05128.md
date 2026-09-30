# [?] Fix underflow in blinded path amt_to_forward

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-06-15
Source: https://github.com/lightningdevkit/rust-lightning/commit/e560ec170682d36e363361c6e8f09c958edd237b
Type: security-commit

## Details
Fix underflow in blinded path amt_to_forward

If we have a high (200%+) proportional fee as an intermediate blinded node
combined with a low inbound amount, we previously had some code that calculated
the outbound amount of the forward that would've underflowed. This would've
caused a panic in debug builds and caused us to relay a payment that should've
been rejected (due to being unable to cover our high fee) in release builds.

Reported by Project Loupe.

## Patch
### lightning/src/blinded_path/payment.rs
```diff
@@ -940,7 +940,7 @@ pub(crate) fn amt_to_forward_msat(
 		(post_base_fee_inbound_amt * 1_000_000 + 1_000_000 + prop - 1) / (prop + 1_000_000);
 
 	let fee = ((amt_to_forward * prop) / 1_000_000) + base;
-	if inbound_amt - fee < amt_to_forward {
+	if inbound_amt.checked_sub(fee)? < amt_to_forward {
 		// Rounding up the forwarded amount resulted in underpaying this node, so take an extra 1 msat
 		// in fee to compensate.
 		amt_to_forward -= 1;
@@ -1415,4 +1415,19 @@ mod tests {
 		.unwrap();
 		assert_eq!(blinded_payinfo.htlc_maximum_msat, 3997);
 	}
+
+	#[test]
+	fn amt_to_forward_msat_underflow() {
+		// `amt_to_forward_msat` is documented to return `None` if underflow occurs, but the
+		// `inbound_amt - fee` subtraction was previously unguarded. With a high proportional fee
+		// and a small inbound amount, rounding the forwarded amount up leaves `fee` larger than
+		// `inbound_amt`, so the subtraction underflows (panicking in debug builds and returning a
+		// nonsensical result in release). Ensure we instead return `None`.
+		let payment_relay = PaymentRelay {
+			cltv_expiry_delta: 0,
+			fee_proportional_millionths: u32::MAX,
+			fee_base_msat: 1,
+		};
+		assert!(super::amt_to_forward_msat(2, &payment_relay).is_none());
+	}
 }
```
