# [?] Avoid panicking when attempting to send an oversized message

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-08-04
Source: https://github.com/lightningdevkit/rust-lightning/commit/c5fdc3bf018c702bf6815f45b0496df1966dcf2f
Type: security-commit

## Details
Avoid panicking when attempting to send an oversized message

While this code should remain unreachable as it likely indicates
we're going to end up force-closing a channel due to being unable
to communicate with a peer, we shouldn't bring down the whole
process for it if we can avoid it.

Co-Authored-By: Claude <noreply@anthropic.com>

## Patch
### lightning/src/ln/peer_handler.rs
```diff
@@ -1542,7 +1542,8 @@ impl<
 						handler.next_onion_message_for_peer(peer_node_id)
 					{
 						let msg = Message::OnionMessage(next_onion_message);
-						self.enqueue_message(peer, msg);
+						// OMs are delivered on a best-effort basis, drop if unsendable.
+						let _ = self.enqueue_message(peer, msg);
 					}
 				}
 			}
@@ -1564,15 +1565,15 @@ impl<
 								announce.contents.short_channel_id + 1,
 							);
 							let msg = Message::ChannelAnnouncement(announce);
-							self.enqueue_message(peer, msg);
+							let _ = self.enqueue_message(peer, msg);
 
 							if let Some(update_a) = update_a_option {
 								let msg = Message::ChannelUpdate(update_a);
-								self.enqueue_message(peer, msg);
+								let _ = self.enqueue_message(peer, msg);
 							}
 							if let Some(update_b) = update_b_option {
 								let msg = Message::ChannelUpdate(update_b);
-								self.enqueue_message(peer, msg);
+								let _ = self.enqueue_message(peer, msg);
 							}
 						} else {
 							peer.sync_status =
@@ -1584,7 +1585,7 @@ impl<
 						if let Some(msg) = handler.get_next_node_announcement(None) {
 							peer.sync_status = InitSyncTracker::NodesSyncing(msg.contents.node_id);
 							let msg = Message::NodeAnnouncement(msg);
-							self.enqueue_message(peer, msg);
+							let _ = self.enqueue_message(peer, msg);
 						} else {
 							peer.sync_status = InitSyncTracker::NoSyncRequested;
 						}
@@ -1595,7 +1596,7 @@ impl<
 						if let Some(msg) = handler.get_next_node_announcement(Some(&sync_node_id)) {
 							peer.sync_status = InitSyncTracker::NodesSyncing(msg.contents.node_id);
 							let msg = Message::NodeAnnouncement(msg);
-							self.enqueue_message(peer, msg);
+							let _ = self.enqueue_message(peer, msg);
 						} else {
 							peer.sync_status = InitSyncTracker::NoSyncRequested;
 						}
@@ -1703,10 +1704,15 @@ impl<
 	}
 
 	/// Append a message to a peer's pending outbound/write buffer
-	fn enqueue_message(&self, peer: &mut Peer, message: Message<CMH::CustomMessage>) {
+	///
+	/// Returns `Err(())` if the message was too large to send (and was thus dropped). This may
+	/// result in us getting out of sync with the peer!
+	fn enqueue_message(
+		&self, peer: &mut Peer, message: Message<CMH::CustomMessage>,
+	) -> Result<(), ()> {
 		let their_node_id = peer.their_node_id.map(|p| p.0);
+		let logger = WithContext::from(&self.logger, their_node_id, None, None);
 		if their_node_id.is_some() {
-			let logger = WithContext::from(&self.logger, their_node_id, None, None);
 			if is_gossip_msg(message.type_id()) {
 				log_gossip!(logger, "Enqueueing message {:?}", message);
 			} else {
@@ -1716,7 +1722,17 @@ impl<
 			debug_assert!(false, "node_id should be set by the time we send a message");
 		}
 		peer.msgs_sent_since_pong += 1;
-		peer.pending_outbound_buffer.push_back(peer.channel_encryptor.encrypt_message(message).expect("TODO: Handled in the next commit"));
+		let msg_ty = message.type_id();
+		match peer.channel_encryptor.encrypt_message(message) {
+			Ok(encrypted_msg) => {
+				peer.pending_outbound_buffer.push_back(encrypted_msg);
+				Ok(())
+			},
+			Err(()) => {
+				log_error!(logger, "Failed to encrypt a message of type {}, dropping it!", msg_ty);
+				Err(())
+			},
+		}
 	}
 
 	fn do_read_event(
@@ -1769,13 +1785,13 @@ impl<
 									msgs::ErrorAction::SendErrorMessage { msg } => {
 										log_debug!(logger, "Error handling message{}; sending error message with: {}", OptionalFromDebugger(&peer_node_id), e.err);
 										let msg = Message::Error(msg);
-										self.enqueue_message($peer, msg);
+										let _ = self.enqueue_message($peer, msg);
 										continue;
 									},
 									msgs::ErrorAction::SendWarningMessage { msg, log_level } => {
 										log_given_level!(logger, log_level, "Error handling message{}; sending warning message with: {}", OptionalFromDebugger(&peer_node_id), e.err);
 										let msg = Message::Warning(msg);
-										self.enqueue_message($peer, msg);
+										let _ = self.enqueue_message($peer, msg);
 										continue;
 									},
 								}
@@ -1871,7 +1887,7 @@ impl<
 								),
 							};
 							let msg = Message::Init(resp);
-							self.enqueue_message(peer, msg);
+							self.enqueue_message(peer, msg).map_err(|()| PeerHandleError {})?;
 						},
 						NextNoiseStep::ActThree => {
 							let res = peer
@@ -1892,7 +1908,7 @@ impl<
 								),
 							};
 							let msg = Message::Init(resp);
-							self.enqueue_message(peer, msg);
+							self.enqueue_message(peer, msg).map_err(|()| PeerHandleError {})?;
 						},
 						NextNoiseStep::NoiseComplete => {
 							if peer.pending_read_is_header {
@@ -1956,7 +1972,7 @@ impl<
 													channel_id,
 													data,
 												});
-												self.enqueue_message(peer, msg);
+												let _ = self.enqueue_message(peer, msg);
 												continue;
 											},
 											(_, Some(ty)) if is_gossip_msg(ty) => {
@@ -1970,7 +1986,7 @@ impl<
 													channel_id,
 													data,
 												});
-												self.enqueue_message(peer, msg);
+												let _ = self.enqueue_message(peer, msg);
 												continue;
 											},
 											(msgs::DecodeError::UnknownRequiredFeature, _) => {
@@ -2399,7 +2415,7 @@ impl<
 				if msg.ponglen < 65532 {
 					let resp = msgs::Pong { byteslen: msg.ponglen };
 					let msg = Message::Pong(resp);
-					self.enqueue_message(&mut *peer_mutex.lock().unwrap(), msg);
+					let _ = self.enqueue_message(&mut *peer_mutex.lock().unwrap(), msg);
 				}
 			},
 			Message::Pong(_msg) => {
@@ -2826,6 +2842,27 @@ impl<
 					}};
 				}
 
+				macro_rules! enqueue_message_to_peer {
+					($peer: expr, $node_id: expr, $msg: expr) => {{
+						if self.enqueue_message($peer, $msg).is_err() {
+							peers_to_disconnect
+								.insert(*$node_id, (None, "a message we failed to send"));
+							None
+						} else {
+							Some(())
+						}
+					}};
+				}
+
+				macro_rules! enqueue_message_to {
+					($node_id: expr, $msg: expr) => {{
+						match get_peer_for_forwarding!($node_id) {
+							Some(mut peer) => enqueue_message_to_peer!(&mut *peer, $node_id, $msg),
+							None => None,
+						}
+					}};
+				}
+
 				let route_handler = &self.message_handler.route_handler;
 				let chan_handler = &self.message_handler.chan_handler;
 				let onion_message_handler = &self.message_handler.onion_message_handler;
@@ -2843,7 +2880,7 @@ impl<
 								node_id,
 							);
 							let msg = Message::PeerStorage(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendPeerStorageRetrieval { ref node_id, msg } => {
 							log_debug!(
@@ -2852,35 +2889,35 @@ impl<
 								node_id,
 							);
 							let msg = Message::PeerStorageRetrieval(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendAcceptChannel { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.common_fields.temporary_channel_id), None), "Handling SendAcceptChannel event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.common_fields.temporary_channel_id);
 							let msg = Message::AcceptChannel(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendAcceptChannelV2 { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.common_fields.temporary_channel_id), None), "Handling SendAcceptChannelV2 event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.common_fields.temporary_channel_id);
 							let msg = Message::AcceptChannelV2(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendOpenChannel { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.common_fields.temporary_channel_id), None), "Handling SendOpenChannel event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.common_fields.temporary_channel_id);
 							let msg = Message::OpenChannel(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendOpenChannelV2 { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.common_fields.temporary_channel_id), None), "Handling SendOpenChannelV2 event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.common_fields.temporary_channel_id);
 							let msg = Message::OpenChannelV2(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendFundingCreated { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.temporary_channel_id), None), "Handling SendFundingCreated event in peer_handler for node {} for channel {} (which becomes {})",
@@ -2890,21 +2927,21 @@ impl<
 							// TODO: If the peer is gone we should generate a DiscardFunding event
 							// indicating to the wallet that they should just throw away this funding transaction
 							let msg = Message::FundingCreated(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendFundingSigned { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendFundingSigned event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::FundingSigned(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendChannelReady { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendChannelReady event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::ChannelReady(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendStfu { ref node_id, msg } => {
 							let logger = WithContext::from(
@@ -2917,7 +2954,7 @@ impl<
 									node_id,
 									&msg.channel_id);
 							let msg = Message::Stfu(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendSpliceInit { ref node_id, msg } => {
 							let logger = WithContext::from(
@@ -2930,7 +2967,7 @@ impl<
 									node_id,
 									&msg.channel_id);
 							let msg = Message::SpliceInit(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendSpliceAck { ref node_id, msg } => {
 							let logger = WithContext::from(
@@ -2943,7 +2980,7 @@ impl<
 									node_id,
 									&msg.channel_id);
 							let msg = Message::SpliceAck(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendSpliceLocked { ref node_id, msg } => {
 							let logger = WithContext::from(
@@ -2956,77 +2993,77 @@ impl<
 									node_id,
 									&msg.channel_id);
 							let msg = Message::SpliceLocked(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxAddInput { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxAddInput event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxAddInput(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxAddOutput { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxAddOutput event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxAddOutput(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxRemoveInput { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxRemoveInput event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxRemoveInput(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxRemoveOutput { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxRemoveOutput event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxRemoveOutput(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxComplete { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxComplete event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxComplete(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxSignatures { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxSignatures event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxSignatures(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxInitRbf { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxInitRbf event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxInitRbf(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxAckRbf { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxAckRbf event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxAckRbf(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendTxAbort { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendTxAbort event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::TxAbort(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendAnnouncementSignatures { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendAnnouncementSignatures event in peer_handler for node {} for channel {})",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::AnnouncementSignatures(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::UpdateHTLCs {
 							ref node_id,
@@ -3051,23 +3088,23 @@ impl<
 							let mut peer = get_peer_for_forwarding!(node_id)?;
 							for msg in update_fulfill_htlcs {
 								let msg = Message::UpdateFulfillHTLC(msg);
-								self.enqueue_message(&mut *peer, msg);
+								enqueue_message_to_peer!(&mut *peer, node_id, msg)?;
 							}
 							for msg in update_fail_htlcs {
 								let msg = Message::UpdateFailHTLC(msg);
-								self.enqueue_message(&mut *peer, msg);
+								enqueue_message_to_peer!(&mut *peer, node_id, msg)?;
 							}
 							for msg in update_fail_malformed_htlcs {
 								let msg = Message::UpdateFailMalformedHTLC(msg);
-								self.enqueue_message(&mut *peer, msg);
+								enqueue_message_to_peer!(&mut *peer, node_id, msg)?;
 							}
 							for msg in update_add_htlcs {
 								let msg = Message::UpdateAddHTLC(msg);
-								self.enqueue_message(&mut *peer, msg);
+								enqueue_message_to_peer!(&mut *peer, node_id, msg)?;
 							}
 							if let Some(msg) = update_fee {
 								let msg = Message::UpdateFee(msg);
-								self.enqueue_message(&mut *peer, msg);
+								enqueue_message_to_peer!(&mut *peer, node_id, msg)?;
 							}
 							if commitment_signed.len() > 1 {
 								let msg = msgs::StartBatch {
@@ -3076,42 +3113,42 @@ impl<
 									message_type: Some(msgs::CommitmentSigned::TYPE),
 								};
 								let msg = Message::StartBatch(msg);
-								self.enqueue_message(&mut *peer, msg);
+								enqueue_message_to_peer!(&mut *peer, node_id, msg)?;
 							}
 							for msg in commitment_signed {
 								let msg = Message::CommitmentSigned(msg);
-								self.enqueue_message(&mut *peer, msg);
+								enqueue_message_to_peer!(&mut *peer, node_id, msg)?;
 							}
 						},
 						MessageSendEvent::SendRevokeAndACK { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendRevokeAndACK event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::RevokeAndACK(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendClosingSigned { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendClosingSigned event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::ClosingSigned(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						#[cfg(simple_close)]
 						MessageSendEvent::SendClosingComplete { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendClosingComplete event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::ClosingComplete(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						#[cfg(simple_close)]
 						MessageSendEvent::SendClosingSig { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendClosingSig event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::ClosingSig(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendShutdown { ref node_id, msg } => {
 							log_debug!(
@@ -3124,14 +3161,14 @@ impl<
 								"Handling Shutdown event in peer_handler",
 							);
 							let msg = Message::Shutdown(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendChannelReestablish { ref node_id, msg } => {
 							log_debug!(WithContext::from(&self.logger, Some(*node_id), Some(msg.channel_id), None), "Handling SendChannelReestablish event in peer_handler for node {} for channel {}",
 									node_id,
 									&msg.channel_id);
 							let msg = Message::ChannelReestablish(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendChannelAnnouncement {
 							ref node_id,
@@ -3142,12 +3179,9 @@ impl<
 									node_id,
 									msg.contents.short_channel_id);
 							let msg = Message::ChannelAnnouncement(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 							let update_msg = Message::ChannelUpdate(update_msg);
-							self.enqueue_message(
-								&mut *get_peer_for_forwarding!(node_id)?,
-								update_msg,
-							);
+							enqueue_message_to!(node_id, update_msg)?;
 						},
 						MessageSendEvent::BroadcastChannelAnnouncement { msg, update_msg } => {
 							log_debug!(self.logger, "Handling BroadcastChannelAnnouncement event in peer_handler for short channel id {}", msg.contents.short_channel_id);
@@ -3241,7 +3275,7 @@ impl<
 								msg.contents.short_channel_id
 							);
 							let msg = Message::ChannelUpdate(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::HandleError { node_id, action } => {
 							let logger = WithContext::from(&self.logger, Some(node_id), None, None);
@@ -3259,16 +3293,22 @@ impl<
 									// processing most messages.
 									let msg =
 										msg.map(|msg| Message::<CMH::CustomMessage>::Error(msg));
-									peers_to_disconnect.insert(node_id, msg);
+									peers_to_disconnect
+										.insert(node_id, (msg, "DisconnectPeer HandleError"));
 								},
 								msgs::ErrorAction::DisconnectPeerWithWarning { msg } => {
 									log_trace!(logger, "Handling DisconnectPeer HandleError event in peer_handler with message {}",
 										 log_msg!(msg.data));
 									// We do not have the peers write lock, so we just store that we're
 									// about to disconnect the peer and do it after we finish
 									// processing most messages.
-									peers_to_disconnect
-										.insert(node_id, Some(Message::Warning(msg)));
+									peers_to_disconnect.insert(
+										node_id,
+										(
+											Some(Message::Warning(msg)),
+											"DisconnectPeerWithWarning HandleError",
+										),
+									);
 								},
 								msgs::ErrorAction::IgnoreAndLog(level) => {
 									log_given_level!(
@@ -3288,19 +3328,13 @@ impl<
 									log_trace!(logger, "Handling SendErrorMessage HandleError event in peer_handler with message {}",
 											log_msg!(msg.data));
 									let msg = Message::Error(msg);
-									self.enqueue_message(
-										&mut *get_peer_for_forwarding!(&node_id)?,
-										msg,
-									);
+									enqueue_message_to!(&node_id, msg)?;
 								},
 								msgs::ErrorAction::SendWarningMessage { msg, ref log_level } => {
 									log_given_level!(logger, *log_level, "Handling SendWarningMessage HandleError event in peer_handler with message {}",
 											log_msg!(msg.data));
 									let msg = Message::Warning(msg);
-									self.enqueue_message(
-										&mut *get_peer_for_forwarding!(&node_id)?,
-										msg,
-									);
+									enqueue_message_to!(&node_id, msg)?;
 								},
 							}
 						},
@@ -3310,14 +3344,14 @@ impl<
 								msg.first_blocknum,
 								msg.number_of_blocks);
 							let msg = Message::QueryChannelRange(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendShortIdsQuery { ref node_id, msg } => {
 							log_gossip!(WithContext::from(&self.logger, Some(*node_id), None, None), "Handling SendShortIdsQuery event in peer_handler with num_scids={}",
 
 								msg.short_channel_ids.len());
 							let msg = Message::QueryShortChannelIds(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendReplyChannelRange { ref node_id, msg } => {
 							log_gossip!(WithContext::from(&self.logger, Some(*node_id), None, None), "Handling SendReplyChannelRange event in peer_handler with num_scids={} first_blocknum={} number_of_blocks={}, sync_complete={}",
@@ -3327,15 +3361,15 @@ impl<
 								msg.number_of_blocks,
 								msg.sync_complete);
 							let msg = Message::ReplyChannelRange(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 						MessageSendEvent::SendGossipTimestampFilter { ref node_id, msg } => {
 							log_gossip!(WithContext::from(&self.logger, Some(*node_id), None, None), "Handling SendGossipTimestampFilter event in peer_handler with first_timestamp={}, timestamp_range={}",
 
 								msg.first_timestamp,
 								msg.timestamp_range);
 							let msg = Message::GossipTimestampFilter(msg);
-							self.enqueue_message(&mut *get_peer_for_forwarding!(node_id)?, msg);
+							enqueue_message_to!(node_id, msg)?;
 						},
 					}
 					Some(())
@@ -3362,16 +3396,7 @@ impl<
 				}
 
 				for (node_id, msg) in custom_message_handler.get_and_clear_pending_msg() {
-					if peers_to_disconnect.get(&node_id).is_some() {
-						continue;
-					}
-					let mut peer = if let Some(peer) = get_peer_for_forwarding!(&node_id) {
-						peer
-					} else {
-						continue;
-					};
-					let msg = Message::Custom(msg);
-					self.enqueue_message(&mut peer, msg);
+					enqueue_message_to!(&node_id, Message::Custom(msg));
 				}
 
 				for (descriptor, peer_mutex) in peers.iter() {
@@ -3389,7 +3414,7 @@ impl<
 			if !peers_to_disconnect.is_empty() {
 				let mut peers_lock = self.peers.write().unwrap();
 				let peers = &mut *peers_lock;
-				for (node_id, msg) in peers_to_disconnect.drain() {
+				for (node_id, (msg, reason)) in peers_to_disconnect.drain() {
 					// Note that since we are holding the peers *write* lock we can
 					// remove from node_id_to_descriptor immediately (as no other
 					// thread can be holding the peer lock if we have the global write
@@ -3401,12 +3426,12 @@ impl<
 						if let Some(peer_mutex) = peers.remove(&descriptor) {
 							let mut peer = peer_mutex.lock().unwrap();
 							if let Some(msg) = msg {
-								self.enqueue_message(&mut *peer, msg);
 								// This isn't guaranteed to work, but if there is enough free
 								// room in the send buffer, put the error message there...
+								let _ = self.enqueue_message(&mut *peer, msg);
 								self.do_attempt_write_data(&mut descriptor, &mut *peer, false);
 							}
-							self.do_disconnect(descriptor, &*peer, "DisconnectPeer HandleError");
+							self.do_disconnect(descriptor, &*peer, reason);
 						} else {
 							debug_assert!(false, "Missing connection for peer");
 						}
@@ -3527,7 +3552,7 @@ impl<
 			peer.awaiting_pong_timer_tick_intervals = -1;
 			let ping = msgs::Ping { ponglen: 0, byteslen: 64 };
 			let msg: Message<CMH::CustomMessage> = Message::Ping(ping);
-			self.enqueue_message(peer, msg);
+			let _ = self.enqueue_message(peer, msg);
 		}
 	}
 
@@ -3599,7 +3624,7 @@ impl<
 					peer.awaiting_pong_timer_tick_intervals = 1;
 					let ping = msgs::Ping { ponglen: 0, byteslen: 64 };
 					let msg = Message::Ping(ping);
-					self.enqueue_message(&mut *peer, msg);
+					let _ = self.enqueue_message(&mut *peer, msg);
 					break;
 				}
 				self.do_attempt_write_data(
@@ -4284,7 +4309,7 @@ mod tests {
 
 		let not_init_msg = msgs::Ping { ponglen: 4, byteslen: 0 };
 		let msg: Message<()> = Message::Ping(not_init_msg);
-		let msg_bytes = dup_encryptor.encrypt_message(msg);
+		let msg_bytes = dup_encryptor.encrypt_message(msg).unwrap();
 		assert!(peers[0].read_event(&mut fd_dup, &msg_bytes).is_err());
 	}
 
@@ -4391,6 +4416,39 @@ mod tests {
 		}
 	}
 
+	// An oversized message trips a `debug_assert` in the encryptor before the error makes it back to
+	// us, so we can only observe the graceful handling with debug assertions disabled.
+	#[test]
+	#[cfg(not(debug_assertions))]
+	fn test_message_send_failure_disconnects() {
+		// Test that a peer we failed to send a message to gets disconnected, ensuring they know to
+		// resync rather than waiting forever on a message which is never going to arrive.
+		let cfgs = create_peermgr_cfgs(2);
+		let peers = create_network(2, &cfgs);
+		let (fd_a, _fd_b) = establish_connection(&peers[0], &peers[1]);
+
+		let id_b = peers[1].node_signer.get_node_id(Recipient::Node).unwrap();
+		assert!(peers[0].peer_by_node_id(&id_b).is_some());
+		assert!(!fd_a.disconnect.load(Ordering::Acquire));
+
+		// Queue an `error` which is too long to fit on the wire, which we'll thus fail to send.
+		let len = crate::ln::peer_channel_encryptor::LN_MAX_MSG_LEN + 1;
+		let msg = msgs::ErrorMessage { channel_id: ChannelId([0; 32]), data: "A".repeat(len) };
+		let action = msgs::ErrorAction::SendErrorMessage { msg };
+		let event = MessageSendEvent::HandleError { node_id: id_b, action };
+		cfgs[0].chan_handler.pending_events.lock().unwrap().push(event);
+
+		peers[0].process_events();
+
+		assert!(fd_a.disconnect.load(Ordering::Acquire));
+		assert!(peers[0].list_peers().is_empty());
+		assert!(peers[0].peer_by_node_id(&id_b).is_none());
+
+		// The message handlers should have been informed of the disconnection.
+		assert!(cfgs[0].chan_handler.conn_tracker.connected_peers.lock().unwrap().is_empty());
+		assert!(cfgs[0].routing_handler.conn_tracker.connected_peers.lock().unwrap().is_empty());
+	}
+
 	#[test]
 	fn test_do_attempt_write_data() {
 		// Create 2 peers with custom TestRoutingMessageHandlers and connect them.
@@ -4668,7 +4726,7 @@ mod tests {
 					data: "no disconnect plz".to_string(),
 				};
 				let msg = Message::Warning(warning);
-				peer_a.enqueue_message(&mut peer_b, msg);
+				peer_a.enqueue_message(&mut peer_b, msg).unwrap();
 			}
 			peer_a.process_events();
 			let msg = fd_a.outbound_data.lock().unwrap().split_off(0);
```
