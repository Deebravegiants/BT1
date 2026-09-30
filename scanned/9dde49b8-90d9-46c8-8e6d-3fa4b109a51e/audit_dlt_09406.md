# [?] Add onion failure packet length check to prevent out of bounds error

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-03-26
Source: https://github.com/lightningdevkit/rust-lightning/commit/10fe63d5da5b9893987d7fda883a7fb78d379e0d
Type: security-commit

## Details
Add onion failure packet length check to prevent out of bounds error

Fixes an oversight in the refactor in commit
ea0f099ddb5dc74a441a34b821d315c19b1315ef when moving the decoding of the
packet.

## Patch
### lightning/src/ln/onion_route_tests.rs
```diff
@@ -692,6 +692,13 @@ fn test_onion_failure() {
 		}, || nodes[2].node.fail_htlc_backwards(&payment_hash), false, None,
 		Some(NetworkUpdate::NodeFailure { node_id: route.paths[0].hops[1].pubkey, is_permanent: true }),
 		Some(channels[1].0.contents.short_channel_id), None);
+
+	run_onion_failure_test_with_fail_intercept("bogus err packet that is too short for an hmac", 200, &nodes,
+		&route, &payment_hash, &payment_secret, |_msg| {}, |msg| {
+			msg.reason = vec![1, 2, 3];
+		}, || nodes[2].node.fail_htlc_backwards(&payment_hash), false, None,
+		None, None, None);
+
 	run_onion_failure_test_with_fail_intercept("0-length channel update in intermediate node UPDATE onion failure",
 		100, &nodes, &route, &payment_hash, &payment_secret, |msg| {
 			msg.amount_msat -= 1;
```

### lightning/src/ln/onion_utils.rs
```diff
@@ -991,6 +991,29 @@ where
 		_ => unreachable!(),
 	};
 
+	// Check that there is at least enough data for an hmac, otherwise none of the checking that we may do makes sense.
+	// Also prevent slice out of bounds further down.
+	if encrypted_packet.data.len() < 32 {
+		log_warn!(
+			logger,
+			"Non-attributable failure encountered on route {}",
+			path.hops.iter().map(|h| h.pubkey.to_string()).collect::<Vec<_>>().join("->")
+		);
+
+		// Signal that we failed permanently. Without a valid hmac, we can't identify the failing node and we can't
+		// apply a penalty. Therefore there is nothing more we can do other than failing the payment.
+		return DecodedOnionFailure {
+			network_update: None,
+			short_channel_id: None,
+			payment_failed_permanently: true,
+			failed_within_blinded_path: false,
+			#[cfg(any(test, feature = "_test_utils"))]
+			onion_error_code: None,
+			#[cfg(any(test, feature = "_test_utils"))]
+			onion_error_data: None,
+		};
+	}
+
 	// Learnings from the HTLC failure to inform future payment retries and scoring.
 	struct FailureLearnings {
 		network_update: Option<NetworkUpdate>,
```
