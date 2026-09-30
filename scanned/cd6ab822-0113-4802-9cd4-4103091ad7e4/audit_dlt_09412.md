# [?] Fix deadlock when closing an unavailable channel

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2023-10-11
Source: https://github.com/lightningdevkit/rust-lightning/commit/7cdb31ae200c48532f3d0dc7c0f8c722674add1e
Type: security-commit

## Details
Fix deadlock when closing an unavailable channel

## Patch
### lightning/src/ln/channelmanager.rs
```diff
@@ -2616,6 +2616,8 @@ where
 					// it does not exist for this peer. Either way, we can attempt to force-close it.
 					//
 					// An appropriate error will be returned for non-existence of the channel if that's the case.
+					mem::drop(peer_state_lock);
+					mem::drop(per_peer_state);
 					return self.force_close_channel_with_peer(&channel_id, counterparty_node_id, None, false).map(|_| ())
 				},
 			}
@@ -4001,7 +4003,7 @@ where
 		for channel_id in channel_ids {
 			if !peer_state.has_channel(channel_id) {
 				return Err(APIError::ChannelUnavailable {
-					err: format!("Channel with ID {} was not found for the passed counterparty_node_id {}", channel_id, counterparty_node_id),
+					err: format!("Channel with id {} not found for the passed counterparty node_id {}", channel_id, counterparty_node_id),
 				});
 			};
 		}
@@ -4112,7 +4114,7 @@ where
 						next_hop_channel_id, next_node_id)
 				}),
 				None => return Err(APIError::ChannelUnavailable {
-					err: format!("Channel with id {} not found for the passed counterparty node_id {}.",
+					err: format!("Channel with id {} not found for the passed counterparty node_id {}",
 						next_hop_channel_id, next_node_id)
 				})
 			}
@@ -10750,6 +10752,16 @@ mod tests {
 		check_api_error_message(expected_message, res_err)
 	}
 
+	fn check_channel_unavailable_error<T>(res_err: Result<T, APIError>, expected_channel_id: ChannelId, peer_node_id: PublicKey) {
+		let expected_message = format!("Channel with id {} not found for the passed counterparty node_id {}", expected_channel_id, peer_node_id);
+		check_api_error_message(expected_message, res_err)
+	}
+
+	fn check_api_misuse_error<T>(res_err: Result<T, APIError>) {
+		let expected_message = "No such channel awaiting to be accepted.".to_string();
+		check_api_error_message(expected_message, res_err)
+	}
+
 	fn check_api_error_message<T>(expected_err_message: String, res_err: Result<T, APIError>) {
 		match res_err {
 			Err(APIError::APIMisuseError { err }) => {
@@ -10794,6 +10806,36 @@ mod tests {
 		check_unkown_peer_error(nodes[0].node.update_channel_config(&unkown_public_key, &[channel_id], &ChannelConfig::default()), unkown_public_key);
 	}
 
+	#[test]
+	fn test_api_calls_with_unavailable_channel() {
+		// Tests that our API functions that expects a `counterparty_node_id` and a `channel_id`
+		// as input, behaves as expected if the `counterparty_node_id` is a known peer in the
+		// `ChannelManager::per_peer_state` map, but the peer state doesn't contain a channel with
+		// the given `channel_id`.
+		let chanmon_cfg = create_chanmon_cfgs(2);
+		let node_cfg = create_node_cfgs(2, &chanmon_cfg);
+		let node_chanmgr = create_node_chanmgrs(2, &node_cfg, &[None, None]);
+		let nodes = create_network(2, &node_cfg, &node_chanmgr);
+
+		let counterparty_node_id = nodes[1].node.get_our_node_id();
+
+		// Dummy values
+		let channel_id = ChannelId::from_bytes([4; 32]);
+
+		// Test the API functions.
+		check_api_misuse_error(nodes[0].node.accept_inbound_channel(&channel_id, &counterparty_node_id, 42));
+
+		check_channel_unavailable_error(nodes[0].node.close_channel(&channel_id, &counterparty_node_id), channel_id, counterparty_node_id);
+
+		check_channel_unavailable_error(nodes[0].node.force_close_broadcasting_latest_txn(&channel_id, &counterparty_node_id), channel_id, counterparty_node_id);
+
+		check_channel_unavailable_error(nodes[0].node.force_close_without_broadcasting_txn(&channel_id, &counterparty_node_id), channel_id, counterparty_node_id);
+
+		check_channel_unavailable_error(nodes[0].node.forward_intercepted_htlc(InterceptId([0; 32]), &channel_id, counterparty_node_id, 1_000_000), channel_id, counterparty_node_id);
+
+		check_channel_unavailable_error(nodes[0].node.update_channel_config(&counterparty_node_id, &[channel_id], &ChannelConfig::default()), channel_id, counterparty_node_id);
+	}
+
 	#[test]
 	fn test_connection_limiting() {
 		// Test that we limit un-channel'd peers and un-funded channels properly.
```

### lightning/src/ln/payment_tests.rs
```diff
@@ -1906,7 +1906,7 @@ fn do_test_intercepted_payment(test: InterceptTest) {
 	// Check for unknown channel id error.
 	let unknown_chan_id_err = nodes[1].node.forward_intercepted_htlc(intercept_id, &ChannelId::from_bytes([42; 32]), nodes[2].node.get_our_node_id(), expected_outbound_amount_msat).unwrap_err();
 	assert_eq!(unknown_chan_id_err , APIError::ChannelUnavailable  {
-		err: format!("Channel with id {} not found for the passed counterparty node_id {}.",
+		err: format!("Channel with id {} not found for the passed counterparty node_id {}",
 			log_bytes!([42; 32]), nodes[2].node.get_our_node_id()) });
 
 	if test == InterceptTest::Fail {
```
