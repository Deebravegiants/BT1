# [?] Fix max-value overflows in `set_max_path_length`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-12-28
Source: https://github.com/lightningdevkit/rust-lightning/commit/3e88b327ef12df573ac2385921e849bb3c3dba45
Type: security-commit

## Details
Fix max-value overflows in `set_max_path_length`

When either the amount or the `max_total_cltv_expiry_delta` are
set to max-value, `set_max_path_length` can trigger overflows in
`build_onion_payloads_callback`, leading to debug-panics.

## Patch
### lightning/src/ln/onion_utils.rs
```diff
@@ -239,7 +239,7 @@ where
 		// the intended recipient).
 		let value_msat = if cur_value_msat == 0 { hop.fee_msat } else { cur_value_msat };
 		let cltv = if cur_cltv == starting_htlc_offset {
-			hop.cltv_expiry_delta + starting_htlc_offset
+			hop.cltv_expiry_delta.saturating_add(starting_htlc_offset)
 		} else {
 			cur_cltv
 		};
@@ -307,7 +307,7 @@ where
 		if cur_value_msat >= 21000000 * 100000000 * 1000 {
 			return Err(APIError::InvalidRoute { err: "Channel fees overflowed?".to_owned() });
 		}
-		cur_cltv += hop.cltv_expiry_delta as u32;
+		cur_cltv = cur_cltv.saturating_add(hop.cltv_expiry_delta as u32);
 		if cur_cltv >= 500000000 {
 			return Err(APIError::InvalidRoute { err: "Channel CLTV overflowed?".to_owned() });
 		}
@@ -333,10 +333,10 @@ pub(crate) fn set_max_path_length(
 	.saturating_add(PAYLOAD_HMAC_LEN);
 
 	const OVERPAY_ESTIMATE_MULTIPLER: u64 = 3;
-	let final_value_msat_with_overpay_buffer = core::cmp::max(
-		route_params.final_value_msat.saturating_mul(OVERPAY_ESTIMATE_MULTIPLER),
-		MIN_FINAL_VALUE_ESTIMATE_WITH_OVERPAY,
-	);
+	let final_value_msat_with_overpay_buffer = route_params
+		.final_value_msat
+		.saturating_mul(OVERPAY_ESTIMATE_MULTIPLER)
+		.clamp(MIN_FINAL_VALUE_ESTIMATE_WITH_OVERPAY, 0x1000_0000);
 
 	let blinded_tail_opt = route_params
 		.payment_params
@@ -351,13 +351,15 @@ pub(crate) fn set_max_path_length(
 			excess_final_cltv_expiry_delta: 0,
 		});
 
+	let cltv_expiry_delta =
+		core::cmp::min(route_params.payment_params.max_total_cltv_expiry_delta, 0x1000_0000);
 	let unblinded_route_hop = RouteHop {
 		pubkey: PublicKey::from_slice(&[2; 33]).unwrap(),
 		node_features: NodeFeatures::empty(),
 		short_channel_id: 42,
 		channel_features: ChannelFeatures::empty(),
 		fee_msat: final_value_msat_with_overpay_buffer,
-		cltv_expiry_delta: route_params.payment_params.max_total_cltv_expiry_delta,
+		cltv_expiry_delta,
 		maybe_announced_channel: false,
 	};
 	let mut num_reserved_bytes: usize = 0;
@@ -1280,7 +1282,7 @@ fn decode_next_hop<T, R: ReadableArgs<T>, N: NextPacketBytes>(
 mod tests {
 	use crate::io;
 	use crate::ln::msgs;
-	use crate::routing::router::{Path, Route, RouteHop};
+	use crate::routing::router::{Path, PaymentParameters, Route, RouteHop};
 	use crate::types::features::{ChannelFeatures, NodeFeatures};
 	use crate::types::payment::PaymentHash;
 	use crate::util::ser::{VecWriter, Writeable, Writer};
@@ -1292,7 +1294,7 @@ mod tests {
 	use bitcoin::secp256k1::Secp256k1;
 	use bitcoin::secp256k1::{PublicKey, SecretKey};
 
-	use super::OnionKeys;
+	use super::*;
 
 	fn get_test_session_key() -> SecretKey {
 		let hex = "4141414141414141414141414141414141414141414141414141414141414141";
@@ -1607,4 +1609,19 @@ mod tests {
 			writer.write_all(&self.data[..])
 		}
 	}
+
+	#[test]
+	fn max_length_with_no_cltv_limit() {
+		// While users generally shouldn't do this, we shouldn't overflow when
+		// `max_total_cltv_expiry_delta` is `u32::MAX`.
+		let recipient = PublicKey::from_slice(&[2; 33]).unwrap();
+		let mut route_params = RouteParameters {
+			payment_params: PaymentParameters::for_keysend(recipient, u32::MAX, true),
+			final_value_msat: u64::MAX,
+			max_total_routing_fee_msat: Some(u64::MAX),
+		};
+		route_params.payment_params.max_total_cltv_expiry_delta = u32::MAX;
+		let recipient_onion = RecipientOnionFields::spontaneous_empty();
+		set_max_path_length(&mut route_params, &recipient_onion, None, None, 42).unwrap();
+	}
 }
```
