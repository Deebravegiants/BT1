# [?] Fix race condition causing async payment failure

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-09-18
Source: https://github.com/lightningdevkit/rust-lightning/commit/ade1f3484aebf17dc9bae1633dec2d3350d4ea4d
Type: security-commit

## Details
Fix race condition causing async payment failure

As the LSP of an async sender, when we receive an update_add with the hold_htlc
flag set, after its onion is decoded we transition the pending HTLC to the
ChannelManager::pending_intercepted_htlcs.  However, if we receive the
release_held_htlc message from the receiver *before* we've had a chance to make
this transition, we'll fail to release the HTLC and it will sit in the pending
intercepts map until it is failed backwards.

To fix this race condition, if we receive release_held_htlc from the recipient
we'll not only check the pending_intercepted_htlcs map for the presence of this
HTLC but also check the map where we keep HTLCs prior to their onions being
decoded.

## Patch
### lightning/src/blinded_path/message.rs
```diff
@@ -587,6 +587,20 @@ pub enum AsyncPaymentsContext {
 		/// An identifier for the HTLC that should be released by us as the sender's always-online
 		/// channel counterparty to the often-offline recipient.
 		intercept_id: InterceptId,
+		/// The short channel id alias corresponding to the to-be-released inbound HTLC, to help locate
+		/// the HTLC internally if the [`ReleaseHeldHtlc`] races our node decoding the held HTLC's
+		/// onion.
+		///
+		/// We use the outbound scid alias because it is stable even if the channel splices, unlike
+		/// regular short channel ids.
+		///
+		/// [`ReleaseHeldHtlc`]: crate::onion_message::async_payments::ReleaseHeldHtlc
+		prev_outbound_scid_alias: u64,
+		/// The id of the to-be-released HTLC, to help locate the HTLC internally if the
+		/// [`ReleaseHeldHtlc`] races our node decoding the held HTLC's onion.
+		///
+		/// [`ReleaseHeldHtlc`]: crate::onion_message::async_payments::ReleaseHeldHtlc
+		htlc_id: u64,
 	},
 }
 
@@ -645,6 +659,8 @@ impl_writeable_tlv_based_enum!(AsyncPaymentsContext,
 	},
 	(6, ReleaseHeldHtlc) => {
 		(0, intercept_id, required),
+		(2, prev_outbound_scid_alias, required),
+		(4, htlc_id, required),
 	},
 );
 
```

### lightning/src/ln/async_payments_tests.rs
```diff
@@ -3349,3 +3349,70 @@ fn fail_held_htlcs_when_cfg_unset() {
 		PaymentFailureReason::RetriesExhausted,
 	);
 }
+
+#[test]
+fn release_htlc_races_htlc_onion_decode() {
+	// Test that an async sender's LSP will release held HTLCs even if they receive the
+	// release_held_htlc message before they have a chance to process the held HTLC's onion. This was
+	// previously broken.
+	let chanmon_cfgs = create_chanmon_cfgs(4);
+	let node_cfgs = create_node_cfgs(4, &chanmon_cfgs);
+
+	let (sender_cfg, recipient_cfg) = (often_offline_node_cfg(), often_offline_node_cfg());
+	let mut sender_lsp_cfg = test_default_channel_config();
+	sender_lsp_cfg.enable_htlc_hold = true;
+	let mut invoice_server_cfg = test_default_channel_config();
+	invoice_server_cfg.accept_forwards_to_priv_channels = true;
+
+	let node_chanmgrs = create_node_chanmgrs(
+		4,
+		&node_cfgs,
+		&[Some(sender_cfg), Some(sender_lsp_cfg), Some(invoice_server_cfg), Some(recipient_cfg)],
+	);
+	let nodes = create_network(4, &node_cfgs, &node_chanmgrs);
+	create_unannounced_chan_between_nodes_with_value(&nodes, 0, 1, 1_000_000, 0);
+	create_announced_chan_between_nodes_with_value(&nodes, 1, 2, 1_000_000, 0);
+	create_unannounced_chan_between_nodes_with_value(&nodes, 2, 3, 1_000_000, 0);
+	unify_blockheight_across_nodes(&nodes);
+	let sender = &nodes[0];
+	let sender_lsp = &nodes[1];
+	let invoice_server = &nodes[2];
+	let recipient = &nodes[3];
+
+	let amt_msat = 5000;
+	let (static_invoice, peer_id, static_invoice_om) =
+		build_async_offer_and_init_payment(amt_msat, &nodes);
+	let payment_hash =
+		lock_in_htlc_for_static_invoice(&static_invoice_om, peer_id, sender, sender_lsp);
+
+	// The LSP has not transitioned the HTLC to the intercepts map internally because
+	// process_pending_htlc_forwards has not been called.
+	let (peer_id, held_htlc_om) =
+		extract_held_htlc_available_oms(sender, &[sender_lsp, invoice_server, recipient])
+			.pop()
+			.unwrap();
+	recipient.onion_messenger.handle_onion_message(peer_id, &held_htlc_om);
+
+	// Extract the release_htlc_om and ensure the sender's LSP will release the HTLC on the next call
+	// to process_pending_htlc_forwards, even though the HTLC was not yet officially intercepted when
+	// the release message arrived.
+	let (peer_id, release_htlc_om) =
+		extract_release_htlc_oms(recipient, &[sender, sender_lsp, invoice_server]).pop().unwrap();
+	sender_lsp.onion_messenger.handle_onion_message(peer_id, &release_htlc_om);
+
+	sender_lsp.node.process_pending_htlc_forwards();
+	let mut events = sender_lsp.node.get_and_clear_pending_msg_events();
+	assert_eq!(events.len(), 1);
+	let ev = remove_first_msg_event_to_node(&invoice_server.node.get_our_node_id(), &mut events);
+	check_added_monitors!(sender_lsp, 1);
+
+	let path: &[&Node] = &[invoice_server, recipient];
+	let args = PassAlongPathArgs::new(sender_lsp, path, amt_msat, payment_hash, ev);
+	let claimable_ev = do_pass_along_path(args).unwrap();
+
+	let route: &[&[&Node]] = &[&[sender_lsp, invoice_server, recipient]];
+	let keysend_preimage = extract_payment_preimage(&claimable_ev);
+	let (res, _) =
+		claim_payment_along_route(ClaimAlongRouteArgs::new(sender, route, keysend_preimage));
+	assert_eq!(res, Some(PaidBolt12Invoice::StaticInvoice(static_invoice)));
+}
```

### lightning/src/ln/channelmanager.rs
```diff
@@ -3509,6 +3509,7 @@ macro_rules! emit_initial_channel_ready_event {
 macro_rules! handle_monitor_update_completion {
 	($self: ident, $peer_state_lock: expr, $peer_state: expr, $per_peer_state_lock: expr, $chan: expr) => { {
 		let channel_id = $chan.context.channel_id();
+		let outbound_scid_alias = $chan.context().outbound_scid_alias();
 		let counterparty_node_id = $chan.context.get_counterparty_node_id();
 		#[cfg(debug_assertions)]
 		{
@@ -3521,7 +3522,7 @@ macro_rules! handle_monitor_update_completion {
 		let mut updates = $chan.monitor_updating_restored(&&logger,
 			&$self.node_signer, $self.chain_hash, &*$self.config.read().unwrap(),
 			$self.best_block.read().unwrap().height,
-			|htlc_id| $self.path_for_release_held_htlc(htlc_id, &channel_id, &counterparty_node_id));
+			|htlc_id| $self.path_for_release_held_htlc(htlc_id, outbound_scid_alias, &channel_id, &counterparty_node_id));
 		let channel_update = if updates.channel_ready.is_some()
 			&& $chan.context.is_usable()
 			&& $peer_state.is_connected
@@ -5623,11 +5624,17 @@ where
 	/// [`HeldHtlcAvailable`] onion message, so the recipient's [`ReleaseHeldHtlc`] response will be
 	/// received to our node.
 	fn path_for_release_held_htlc(
-		&self, htlc_id: u64, channel_id: &ChannelId, counterparty_node_id: &PublicKey,
+		&self, htlc_id: u64, prev_outbound_scid_alias: u64, channel_id: &ChannelId,
+		counterparty_node_id: &PublicKey,
 	) -> BlindedMessagePath {
 		let intercept_id =
 			InterceptId::from_htlc_id_and_chan_id(htlc_id, channel_id, counterparty_node_id);
-		self.flow.path_for_release_held_htlc(intercept_id, &*self.entropy_source)
+		self.flow.path_for_release_held_htlc(
+			intercept_id,
+			prev_outbound_scid_alias,
+			htlc_id,
+			&*self.entropy_source,
+		)
 	}
 
 	/// Signals that no further attempts for the given payment should occur. Useful if you have a
@@ -11302,14 +11309,15 @@ This indicates a bug inside LDK. Please report this error at https://github.com/
 						// disconnect, so Channel's reestablish will never hand us any holding cell
 						// freed HTLCs to fail backwards. If in the future we no longer drop pending
 						// add-HTLCs on disconnect, we may be handed HTLCs to fail backwards here.
+						let outbound_scid_alias = chan.context.outbound_scid_alias();
 						let res = chan.channel_reestablish(
 							msg,
 							&&logger,
 							&self.node_signer,
 							self.chain_hash,
 							&self.config.read().unwrap(),
 							&*self.best_block.read().unwrap(),
-							|htlc_id| self.path_for_release_held_htlc(htlc_id, &msg.channel_id, counterparty_node_id)
+							|htlc_id| self.path_for_release_held_htlc(htlc_id, outbound_scid_alias, &msg.channel_id, counterparty_node_id)
 						);
 						let responses = try_channel_entry!(self, peer_state, res, chan_entry);
 						let mut channel_update = None;
@@ -11786,11 +11794,12 @@ This indicates a bug inside LDK. Please report this error at https://github.com/
 		// Returns whether we should remove this channel as it's just been closed.
 		let unblock_chan = |chan: &mut Channel<SP>, pending_msg_events: &mut Vec<MessageSendEvent>| -> Option<ShutdownResult> {
 			let channel_id = chan.context().channel_id();
+			let outbound_scid_alias = chan.context().outbound_scid_alias();
 			let logger = WithChannelContext::from(&self.logger, &chan.context(), None);
 			let node_id = chan.context().get_counterparty_node_id();
 			if let Some(msgs) = chan.signer_maybe_unblocked(
 				self.chain_hash, &&logger,
-				|htlc_id| self.path_for_release_held_htlc(htlc_id, &channel_id, &node_id)
+				|htlc_id| self.path_for_release_held_htlc(htlc_id, outbound_scid_alias, &channel_id, &node_id)
 			) {
 				if chan.context().is_connected() {
 					if let Some(msg) = msgs.open_channel {
@@ -15029,7 +15038,34 @@ where
 					);
 				}
 			},
-			AsyncPaymentsContext::ReleaseHeldHtlc { intercept_id } => {
+			AsyncPaymentsContext::ReleaseHeldHtlc {
+				intercept_id,
+				prev_outbound_scid_alias,
+				htlc_id,
+			} => {
+				// It's possible the release_held_htlc message raced ahead of us transitioning the pending
+				// update_add to `Self::pending_intercept_htlcs`. If that's the case, update the pending
+				// update_add to indicate that the HTLC should be released immediately.
+				//
+				// Check for the HTLC here before checking `pending_intercept_htlcs` to avoid a different
+				// race where the HTLC gets transitioned to `pending_intercept_htlcs` after we drop that
+				// map's lock but before acquiring the `decode_update_add_htlcs` lock.
+				let mut decode_update_add_htlcs = self.decode_update_add_htlcs.lock().unwrap();
+				if let Some(htlcs) = decode_update_add_htlcs.get_mut(&prev_outbound_scid_alias) {
+					for update_add in htlcs.iter_mut() {
+						if update_add.htlc_id == htlc_id {
+							log_trace!(
+								self.logger,
+								"Marking held htlc with intercept_id {} as ready to release",
+								intercept_id
+							);
+							update_add.hold_htlc.take();
+							return;
+						}
+					}
+				}
+				core::mem::drop(decode_update_add_htlcs);
+
 				let mut htlc = {
 					let mut pending_intercept_htlcs =
 						self.pending_intercepted_htlcs.lock().unwrap();
```

### lightning/src/offers/flow.rs
```diff
@@ -1227,14 +1227,17 @@ where
 	///
 	/// [`ReleaseHeldHtlc`]: crate::onion_message::async_payments::ReleaseHeldHtlc
 	pub fn path_for_release_held_htlc<ES: Deref>(
-		&self, intercept_id: InterceptId, entropy: ES,
+		&self, intercept_id: InterceptId, prev_outbound_scid_alias: u64, htlc_id: u64, entropy: ES,
 	) -> BlindedMessagePath
 	where
 		ES::Target: EntropySource,
 	{
 		// In the future, we should support multi-hop paths here.
-		let context =
-			MessageContext::AsyncPayments(AsyncPaymentsContext::ReleaseHeldHtlc { intercept_id });
+		let context = MessageContext::AsyncPayments(AsyncPaymentsContext::ReleaseHeldHtlc {
+			intercept_id,
+			prev_outbound_scid_alias,
+			htlc_id,
+		});
 		let num_dummy_hops = PADDED_PATH_LENGTH.saturating_sub(1);
 		BlindedMessagePath::new_with_dummy_hops(
 			&[],
```
