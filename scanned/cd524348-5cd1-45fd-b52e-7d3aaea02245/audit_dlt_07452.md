# [?] Fix debug panic in full_stack fuzz test

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-02-13
Source: https://github.com/lightningdevkit/rust-lightning/commit/e93aa019eff7a0d7545a622de091c49f55bf19f5
Type: security-commit

## Details
Fix debug panic in full_stack fuzz test

d4bd56fc41e8714574407ffcd064be21cb42e539 changed the logic for calling
unset_funding_info such that it may be called on a channel that was
already in ChannelPhase::Funded when handling funding_signed. This
caused a debug panic in the full_stack fuzz test when calling
FundedChannel::unset_funding_info. Fix this by only calling
unset_funding_info on watch_channel error, as was previously the case.

This also reverts moving the channel back into
ChannelPhase::UnfundedOutboundV1, which should be fine since the channel
is about to be removed.

## Patch
### lightning/src/ln/channel.rs
```diff
@@ -1412,29 +1412,6 @@ impl<SP: Deref> Channel<SP> where
 		result.map(|monitor| (self.as_funded_mut().expect("Channel should be funded"), monitor))
 	}
 
-	pub fn unset_funding_info(&mut self) {
-		let phase = core::mem::replace(&mut self.phase, ChannelPhase::Undefined);
-		if let ChannelPhase::Funded(mut funded_chan) = phase {
-			funded_chan.unset_funding_info();
-
-			let context = funded_chan.context;
-			let unfunded_context = UnfundedChannelContext {
-				unfunded_channel_age_ticks: 0,
-				holder_commitment_point: HolderCommitmentPoint::new(&context.holder_signer, &context.secp_ctx),
-			};
-			let unfunded_chan = OutboundV1Channel {
-				context,
-				unfunded_context,
-				signer_pending_open_channel: false,
-			};
-			self.phase = ChannelPhase::UnfundedOutboundV1(unfunded_chan);
-		} else {
-			self.phase = phase;
-		};
-
-		debug_assert!(!matches!(self.phase, ChannelPhase::Undefined));
-	}
-
 	pub fn funding_tx_constructed<L: Deref>(
 		&mut self, signing_session: InteractiveTxSigningSession, logger: &L
 	) -> Result<(msgs::CommitmentSigned, Option<Event>), ChannelError>
```

### lightning/src/ln/channelmanager.rs
```diff
@@ -8241,24 +8241,22 @@ This indicates a bug inside LDK. Please report this error at https://github.com/
 					.and_then(|(funded_chan, monitor)| {
 						self.chain_monitor
 							.watch_channel(funded_chan.context.channel_id(), monitor)
-							.map(|persist_status| (funded_chan, persist_status))
 							.map_err(|()| {
+								// We weren't able to watch the channel to begin with, so no
+								// updates should be made on it. Previously, full_stack_target
+								// found an (unreachable) panic when the monitor update contained
+								// within `shutdown_finish` was applied.
+								funded_chan.unset_funding_info();
 								ChannelError::close("Channel ID was a duplicate".to_owned())
 							})
+							.map(|persist_status| (funded_chan, persist_status))
 					})
 				{
 					Ok((funded_chan, persist_status)) => {
 						handle_new_monitor_update!(self, persist_status, peer_state_lock, peer_state, per_peer_state, funded_chan, INITIAL_MONITOR);
 						Ok(())
 					},
-					Err(e) => {
-						// We weren't able to watch the channel to begin with, so no
-						// updates should be made on it. Previously, full_stack_target
-						// found an (unreachable) panic when the monitor update contained
-						// within `shutdown_finish` was applied.
-						chan.unset_funding_info();
-						try_channel_entry!(self, peer_state, Err(e), chan_entry)
-					},
+					Err(e) => try_channel_entry!(self, peer_state, Err(e), chan_entry),
 				}
 			},
 			hash_map::Entry::Vacant(_) => return Err(MsgHandleErrInternal::send_err_msg_no_close("Failed to find corresponding channel".to_owned(), msg.channel_id))
```
