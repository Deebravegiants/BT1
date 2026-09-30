# [?] Fix debug panic in onion utils on large custom TLVs or metadata.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2023-11-22
Source: https://github.com/lightningdevkit/rust-lightning/commit/e9bd893447d77e417ab7fed49365076ba390c495
Type: security-commit

## Details
Fix debug panic in onion utils on large custom TLVs or metadata.

We previously assumed that the final node's payload would be ~93 bytes, and had
code to ensure that the filler encoded after that payload is not all 0s. Now
with custom TLVs and metadata supported, the final node's payload may take up
the entire onion packet, so we can't assume that there are 64 bytes of filler
to check.

## Patch
### lightning/src/ln/onion_payment.rs
```diff
@@ -23,6 +23,7 @@ use crate::prelude::*;
 use core::ops::Deref;
 
 /// Invalid inbound onion payment.
+#[derive(Debug)]
 pub struct InboundOnionErr {
 	/// BOLT 4 error code.
 	pub err_code: u16,
```

### lightning/src/ln/onion_utils.rs
```diff
@@ -1021,18 +1021,20 @@ fn decode_next_hop<T, R: ReadableArgs<T>, N: NextPacketBytes>(shared_secret: [u8
 			if hmac == [0; 32] {
 				#[cfg(test)]
 				{
-					// In tests, make sure that the initial onion packet data is, at least, non-0.
-					// We could do some fancy randomness test here, but, ehh, whatever.
-					// This checks for the issue where you can calculate the path length given the
-					// onion data as all the path entries that the originator sent will be here
-					// as-is (and were originally 0s).
-					// Of course reverse path calculation is still pretty easy given naive routing
-					// algorithms, but this fixes the most-obvious case.
-					let mut next_bytes = [0; 32];
-					chacha_stream.read_exact(&mut next_bytes).unwrap();
-					assert_ne!(next_bytes[..], [0; 32][..]);
-					chacha_stream.read_exact(&mut next_bytes).unwrap();
-					assert_ne!(next_bytes[..], [0; 32][..]);
+					if chacha_stream.read.position() < hop_data.len() as u64 - 64 {
+						// In tests, make sure that the initial onion packet data is, at least, non-0.
+						// We could do some fancy randomness test here, but, ehh, whatever.
+						// This checks for the issue where you can calculate the path length given the
+						// onion data as all the path entries that the originator sent will be here
+						// as-is (and were originally 0s).
+						// Of course reverse path calculation is still pretty easy given naive routing
+						// algorithms, but this fixes the most-obvious case.
+						let mut next_bytes = [0; 32];
+						chacha_stream.read_exact(&mut next_bytes).unwrap();
+						assert_ne!(next_bytes[..], [0; 32][..]);
+						chacha_stream.read_exact(&mut next_bytes).unwrap();
+						assert_ne!(next_bytes[..], [0; 32][..]);
+					}
 				}
 				return Ok((msg, None)); // We are the final destination for this packet
 			} else {
```

### lightning/src/ln/payment_tests.rs
```diff
@@ -19,8 +19,9 @@ use crate::events::{ClosureReason, Event, HTLCDestination, MessageSendEvent, Mes
 use crate::ln::channel::{EXPIRE_PREV_CONFIG_TICKS, commit_tx_fee_msat, get_holder_selected_channel_reserve_satoshis, ANCHOR_OUTPUT_VALUE_SATOSHI};
 use crate::ln::channelmanager::{BREAKDOWN_TIMEOUT, MPP_TIMEOUT_TICKS, MIN_CLTV_EXPIRY_DELTA, PaymentId, PaymentSendFailure, RecentPaymentDetails, RecipientOnionFields, HTLCForwardInfo, PendingHTLCRouting, PendingAddHTLCInfo};
 use crate::ln::features::{Bolt11InvoiceFeatures, ChannelTypeFeatures};
-use crate::ln::{msgs, ChannelId, PaymentSecret, PaymentPreimage};
+use crate::ln::{msgs, ChannelId, PaymentHash, PaymentSecret, PaymentPreimage};
 use crate::ln::msgs::ChannelMessageHandler;
+use crate::ln::onion_utils;
 use crate::ln::outbound_payment::{IDEMPOTENCY_TIMEOUT_TICKS, Retry};
 use crate::routing::gossip::{EffectiveCapacity, RoutingFees};
 use crate::routing::router::{get_route, Path, PaymentParameters, Route, Router, RouteHint, RouteHintHop, RouteHop, RouteParameters, find_route};
@@ -31,10 +32,14 @@ use crate::util::errors::APIError;
 use crate::util::ser::Writeable;
 use crate::util::string::UntrustedString;
 
+use bitcoin::hashes::Hash;
+use bitcoin::hashes::sha256::Hash as Sha256;
 use bitcoin::network::constants::Network;
+use bitcoin::secp256k1::{Secp256k1, SecretKey};
 
 use crate::prelude::*;
 
+use crate::ln::functional_test_utils;
 use crate::ln::functional_test_utils::*;
 use crate::routing::gossip::NodeId;
 #[cfg(feature = "std")]
@@ -4194,3 +4199,59 @@ fn  test_htlc_forward_considers_anchor_outputs_value() {
 	check_closed_broadcast(&nodes[2], 1, true);
 	check_added_monitors(&nodes[2], 1);
 }
+
+#[test]
+fn peel_payment_onion_custom_tlvs() {
+	let chanmon_cfgs = create_chanmon_cfgs(2);
+	let node_cfgs = create_node_cfgs(2, &chanmon_cfgs);
+	let node_chanmgrs = create_node_chanmgrs(2, &node_cfgs, &[None, None]);
+	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
+	create_announced_chan_between_nodes(&nodes, 0, 1);
+	let secp_ctx = Secp256k1::new();
+
+	let amt_msat = 1000;
+	let payment_params = PaymentParameters::for_keysend(nodes[1].node.get_our_node_id(),
+		TEST_FINAL_CLTV, false);
+	let route_params = RouteParameters::from_payment_params_and_value(payment_params, amt_msat);
+	let route = functional_test_utils::get_route(&nodes[0], &route_params).unwrap();
+	let mut recipient_onion = RecipientOnionFields::spontaneous_empty()
+		.with_custom_tlvs(vec![(414141, vec![42; 1200])]).unwrap();
+	let prng_seed = chanmon_cfgs[0].keys_manager.get_secure_random_bytes();
+	let session_priv = SecretKey::from_slice(&prng_seed[..]).expect("RNG is busted");
+	let keysend_preimage = PaymentPreimage([42; 32]);
+	let payment_hash = PaymentHash(Sha256::hash(&keysend_preimage.0).to_byte_array());
+
+	let (onion_routing_packet, first_hop_msat, cltv_expiry) = onion_utils::create_payment_onion(
+		&secp_ctx, &route.paths[0], &session_priv, amt_msat, recipient_onion.clone(),
+		nodes[0].best_block_info().1, &payment_hash, &Some(keysend_preimage), prng_seed
+	).unwrap();
+
+	let update_add = msgs::UpdateAddHTLC {
+		channel_id: ChannelId([0; 32]),
+		htlc_id: 42,
+		amount_msat: first_hop_msat,
+		payment_hash,
+		cltv_expiry,
+		skimmed_fee_msat: None,
+		onion_routing_packet,
+		blinding_point: None,
+	};
+	let peeled_onion = crate::ln::onion_payment::peel_payment_onion(
+		&update_add, &&chanmon_cfgs[1].keys_manager, &&chanmon_cfgs[1].logger, &secp_ctx,
+		nodes[1].best_block_info().1, true, false
+	).unwrap();
+	assert_eq!(peeled_onion.incoming_amt_msat, Some(amt_msat));
+	match peeled_onion.routing {
+		PendingHTLCRouting::ReceiveKeysend {
+			payment_data, payment_metadata, custom_tlvs, ..
+		} => {
+			#[cfg(not(c_bindings))]
+			assert_eq!(&custom_tlvs, recipient_onion.custom_tlvs());
+			#[cfg(c_bindings)]
+			assert_eq!(custom_tlvs, recipient_onion.custom_tlvs());
+			assert!(payment_metadata.is_none());
+			assert!(payment_data.is_none());
+		},
+		_ => panic!()
+	}
+}
```
