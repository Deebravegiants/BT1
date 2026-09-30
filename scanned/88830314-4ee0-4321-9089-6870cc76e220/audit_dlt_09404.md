# [?] Merge pull request #3709 from joostjager/fix-attr-failure-crash

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-04-04
Source: https://github.com/lightningdevkit/rust-lightning/commit/42ab42a1e8226c73c3fc3c7ac346cc954d1dec55
Type: security-commit

## Details
Merge pull request #3709 from joostjager/fix-attr-failure-crash

Fix long route failure attribution

## Patch
### lightning/src/ln/onion_utils.rs
```diff
@@ -1144,6 +1144,10 @@ where
 		.expect("Route we used spontaneously grew invalid keys in the middle of it?");
 	}
 
+	// In the best case, paths can be up to 27 hops. But attribution data can only be conveyed back to the sender from
+	// the first 20 hops. Determine the number of hops to be used for attribution data.
+	let attributable_hop_count = usize::min(path.hops.len(), MAX_HOPS);
+
 	// Handle packed channel/node updates for passing back for the route handler
 	let mut iterator = onion_keys.into_iter().enumerate().peekable();
 	while let Some((route_hop_idx, (route_hop_option, shared_secret))) = iterator.next() {
@@ -1215,11 +1219,13 @@ where
 		// Check attr error HMACs if present.
 		if let Some(ref mut attribution_data) = encrypted_packet.attribution_data {
 			// Only consider hops in the regular path for attribution data. Failures in a blinded path are not attributable.
-			if route_hop_idx < path.hops.len() {
-				// Calculate position relative to the final hop. The final hop is at position 0. The failure node does not
-				// need to come from the final node, but we need to look at the chain of HMACs that does include all data up
-				// to the final node. For a more nearby failure, the verified HMACs will include some zero padding data.
-				let position = path.hops.len() - route_hop_idx - 1;
+			if route_hop_idx < attributable_hop_count {
+				// Calculate position relative to the last attributable hop. The last attributable hop is at position 0.
+				// The failure node does not need to come from the last attributable hop, but we need to look at the
+				// chain of HMACs that does include all data up to the last attributable hop. For a more nearby failure,
+				// the verified HMACs will include some zero padding data. Failures beyond the last attributable hop
+				// will not be attributable.
+				let position = attributable_hop_count - route_hop_idx - 1;
 				let hold_time = attribution_data.verify(
 					&encrypted_packet.data,
 					shared_secret.as_ref(),
@@ -3169,6 +3175,79 @@ mod tests {
 		assert_eq!(decrypted_failure.short_channel_id, Some(0));
 	}
 
+	#[test]
+	fn test_long_route_attributable_failure() {
+		// Test a long route that exceeds the reach of attribution data.
+
+		let secp_ctx = Secp256k1::new();
+		const LEGACY_MAX_HOPS: usize = 27;
+
+		// Construct a route with 27 hops.
+		let mut hops = Vec::new();
+		for i in 0..LEGACY_MAX_HOPS {
+			let mut secret_bytes = [0; 32];
+			secret_bytes[0] = (i + 1) as u8;
+			let secret_key = SecretKey::from_slice(&secret_bytes).unwrap();
+			let pubkey = secret_key.public_key(&secp_ctx);
+
+			hops.push(RouteHop {
+				pubkey,
+				channel_features: ChannelFeatures::empty(),
+				node_features: NodeFeatures::empty(),
+				short_channel_id: i as u64,
+				fee_msat: 0,
+				cltv_expiry_delta: 0,
+				maybe_announced_channel: true,
+			});
+		}
+		let path = Path { hops, blinded_tail: None };
+
+		// Calculate shared secrets.
+		let mut onion_keys = Vec::new();
+		let session_key = get_test_session_key();
+		construct_onion_keys_generic_callback(
+			&secp_ctx,
+			&path.hops,
+			None,
+			&session_key,
+			|shared_secret, _, _, _, _| onion_keys.push(shared_secret),
+		)
+		.unwrap();
+
+		// Construct the htlc source.
+		let logger = TestLogger::new();
+		let htlc_source = HTLCSource::OutboundRoute {
+			path,
+			session_priv: session_key,
+			first_hop_htlc_msat: 0,
+			payment_id: PaymentId([1; 32]),
+		};
+
+		// Iterate over all possible failure positions and check that the cases that can be attributed are.
+		for failure_pos in 0..LEGACY_MAX_HOPS {
+			// Create a failure packet with bogus data.
+			let packet = vec![1u8; 292];
+			let mut onion_error =
+				OnionErrorPacket { data: packet, attribution_data: Some(AttributionData::new()) };
+
+			// Apply the processing that the preceding hops would apply.
+			for i in (0..failure_pos).rev() {
+				let shared_secret = onion_keys[i].secret_bytes();
+				process_failure_packet(&mut onion_error, &shared_secret, 0);
+				super::crypt_failure_packet(&shared_secret, &mut onion_error);
+			}
+
+			// Decrypt the failure.
+			let decrypted_failure =
+				process_onion_failure(&secp_ctx, &&logger, &htlc_source, onion_error);
+
+			// Expect attribution up to hop 20.
+			let expected_failed_chan =
+				if failure_pos < MAX_HOPS { Some(failure_pos as u64) } else { None };
+			assert_eq!(decrypted_failure.short_channel_id, expected_failed_chan);
+		}
+	}
+
 	#[test]
 	fn test_unreadable_failure_packet_onion() {
 		// Create a failure packet with a valid hmac but unreadable failure message.
```
