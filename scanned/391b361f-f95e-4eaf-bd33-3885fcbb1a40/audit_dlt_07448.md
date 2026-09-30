# [?] Fix panic when calling `batch_funding_transaction_generated` early

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-08-16
Source: https://github.com/lightningdevkit/rust-lightning/commit/e2988543a06a2370a71bc531eec327eb520116bd
Type: security-commit

## Details
Fix panic when calling `batch_funding_transaction_generated` early

If a user calls `batch_funding_transaction_generated` before a
channel is ready to fund its possible to hit an `unwrap` when the
transaction-scanning logic attempts to fetch the channel's expected
output `scriptPubKey`.

While users shouldn't be doing this, we should also avoid the
panic, so here check the channel state first.

Found by the `full_stack_target` fuzzer.

## Patch
### lightning/src/ln/channel.rs
```diff
@@ -1565,6 +1565,22 @@ where
 		)
 	}
 
+	/// Returns true if this channel is waiting on a (batch) funding transaction to be provided.
+	///
+	/// If this method returns true, [`Self::into_unfunded_outbound_v1`] will also succeed.
+	pub fn ready_to_fund(&self) -> bool {
+		if !self.funding().is_outbound() {
+			return false;
+		}
+		match self.context().channel_state {
+			ChannelState::NegotiatingFunding(flags) => {
+				debug_assert!(matches!(self.phase, ChannelPhase::UnfundedOutboundV1(_)));
+				flags.is_our_init_sent() && flags.is_their_init_sent()
+			},
+			_ => false,
+		}
+	}
+
 	pub fn into_unfunded_outbound_v1(self) -> Result<OutboundV1Channel<SP>, Self> {
 		if let ChannelPhase::UnfundedOutboundV1(channel) = self.phase {
 			Ok(channel)
```

### lightning/src/ln/channel_open_tests.rs
```diff
@@ -2509,3 +2509,38 @@ pub fn test_funding_signed_event() {
 	nodes[0].node.get_and_clear_pending_msg_events();
 	nodes[1].node.get_and_clear_pending_msg_events();
 }
+
+#[xtest(feature = "_externalize_tests")]
+fn test_fund_pending_channel() {
+	// Previously, we would panic if a user called `batch_funding_transaction_generated` for a
+	// channel which wasn't ready to receive funding. While this isn't a major bug - users
+	// shouldn't do that - we shouldn't panic and should instead return an error.
+	let chanmon_cfgs = create_chanmon_cfgs(2);
+	let node_cfgs = create_node_cfgs(2, &chanmon_cfgs);
+	let node_chanmgrs = create_node_chanmgrs(2, &node_cfgs, &[None, None]);
+	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
+
+	let node_b_id = nodes[1].node.get_our_node_id();
+
+	nodes[0].node.create_channel(node_b_id, 100_000, 0, 42, None, None).unwrap();
+	let open_msg = get_event_msg!(nodes[0], MessageSendEvent::SendOpenChannel, node_b_id);
+
+	let tx = Transaction {
+		version: Version(2),
+		lock_time: LockTime::ZERO,
+		input: vec![],
+		output: vec![],
+	};
+	let pending_chan = [(&open_msg.common_fields.temporary_channel_id, &node_b_id)];
+	let res = nodes[0].node.batch_funding_transaction_generated(&pending_chan, tx);
+	if let Err(APIError::APIMisuseError { err }) = res {
+		assert_eq!(err, "Channel f7fee84016d554015f5166c0a0df6479942ef55fd70713883b0493493a38e13a with counterparty 0355f8d2238a322d16b602bd0ceaad5b01019fb055971eaadcc9b29226a4da6c23 is not an unfunded, outbound channel ready to fund");
+	} else {
+		panic!("Unexpected result {res:?}");
+	}
+	get_err_msg(&nodes[0], &node_b_id);
+	let reason = ClosureReason::ProcessingError {
+		err: "Error in transaction funding: Misuse error: Channel f7fee84016d554015f5166c0a0df6479942ef55fd70713883b0493493a38e13a with counterparty 0355f8d2238a322d16b602bd0ceaad5b01019fb055971eaadcc9b29226a4da6c23 is not an unfunded, outbound channel ready to fund".to_owned(),
+	};
+	check_closed_event!(nodes[0], 1, reason, [node_b_id], 100_000);
+}
```

### lightning/src/ln/channelmanager.rs
```diff
@@ -5608,42 +5608,48 @@ where
 			Err($api_err)
 		} } }
 
-		let funding_txo;
-		let (mut chan, msg_opt) = match peer_state.channel_by_id.remove(&temporary_channel_id)
-			.map(Channel::into_unfunded_outbound_v1)
-		{
-			Some(Ok(mut chan)) => {
-				match find_funding_output(&chan) {
-					Ok(found_funding_txo) => funding_txo = found_funding_txo,
-					Err(err) => {
-						let chan_err = ChannelError::close(err.to_owned());
-						let api_err = APIError::APIMisuseError { err: err.to_owned() };
-						return abandon_chan!(chan_err, api_err, chan);
-					},
+		let mut chan = match peer_state.channel_by_id.entry(temporary_channel_id) {
+			hash_map::Entry::Occupied(chan) => {
+				if !chan.get().ready_to_fund() {
+					return Err(APIError::APIMisuseError {
+						err: format!("Channel {temporary_channel_id} with counterparty {counterparty_node_id} is not an unfunded, outbound channel ready to fund"),
+					});
 				}
-
-				let logger = WithChannelContext::from(&self.logger, &chan.context, None);
-				let funding_res = chan.get_funding_created(funding_transaction, funding_txo, is_batch_funding, &&logger);
-				match funding_res {
-					Ok(funding_msg) => (chan, funding_msg),
-					Err((mut chan, chan_err)) => {
-						let api_err = APIError::ChannelUnavailable { err: "Signer refused to sign the initial commitment transaction".to_owned() };
-						return abandon_chan!(chan_err, api_err, chan);
-					}
+				match chan.remove().into_unfunded_outbound_v1() {
+					Ok(chan) => chan,
+					Err(chan) => {
+						debug_assert!(false, "ready_to_fund guarantees into_unfunded_outbound_v1 will succeed");
+						peer_state.channel_by_id.insert(temporary_channel_id, chan);
+						return Err(APIError::APIMisuseError {
+							err: "Invalid state, please report this bug".to_owned(),
+						});
+					},
 				}
 			},
-			Some(Err(chan)) => {
-				peer_state.channel_by_id.insert(temporary_channel_id, chan);
-				return Err(APIError::APIMisuseError {
-					err: format!(
-						"Channel with id {} for the passed counterparty node_id {} is not an unfunded, outbound V1 channel",
-						temporary_channel_id, counterparty_node_id),
-				})
+			hash_map::Entry::Vacant(_) => {
+				return Err(APIError::ChannelUnavailable {
+					err: format!("Channel {temporary_channel_id} with counterparty {counterparty_node_id} not found"),
+				});
 			},
-			None => return Err(APIError::ChannelUnavailable {err: format!(
-				"Channel with id {} not found for the passed counterparty node_id {}",
-				temporary_channel_id, counterparty_node_id),
-				}),
+		};
+
+		let funding_txo = match find_funding_output(&chan) {
+			Ok(found_funding_txo) => found_funding_txo,
+			Err(err) => {
+				let chan_err = ChannelError::close(err.to_owned());
+				let api_err = APIError::APIMisuseError { err: err.to_owned() };
+				return abandon_chan!(chan_err, api_err, chan);
+			},
+		};
+
+		let logger = WithChannelContext::from(&self.logger, &chan.context, None);
+		let funding_res = chan.get_funding_created(funding_transaction, funding_txo, is_batch_funding, &&logger);
+		let (mut chan, msg_opt) = match funding_res {
+			Ok(funding_msg) => (chan, funding_msg),
+			Err((mut chan, chan_err)) => {
+				let api_err = APIError::ChannelUnavailable { err: "Signer refused to sign the initial commitment transaction".to_owned() };
+				return abandon_chan!(chan_err, api_err, chan);
+			}
 		};
 
 		match peer_state.channel_by_id.entry(chan.context.channel_id()) {
```
