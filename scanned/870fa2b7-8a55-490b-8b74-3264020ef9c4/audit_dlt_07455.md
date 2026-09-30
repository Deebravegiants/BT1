# [?] Force-close channels on underflow

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-12-09
Source: https://github.com/lightningdevkit/rust-lightning/commit/a652980045b1f4ff0f80cb83bc4aef464f819e00
Type: security-commit

## Details
Force-close channels on underflow

Following up on the previous commit, where we added debug_asserts
within `build_closing_transaction` to ensure neither
`value_to_holder` nor `value_to_counterparty` underflow, we now also
force-close the channel in the (presumably impossible) event that it
did happen.

## Patch
### lightning/src/ln/channel.rs
```diff
@@ -4351,7 +4351,7 @@ impl<SP: Deref> Channel<SP> where
 	}
 
 	#[inline]
-	fn build_closing_transaction(&self, proposed_total_fee_satoshis: u64, skip_remote_output: bool) -> (ClosingTransaction, u64) {
+	fn build_closing_transaction(&self, proposed_total_fee_satoshis: u64, skip_remote_output: bool) -> Result<(ClosingTransaction, u64), ChannelError> {
 		assert!(self.context.pending_inbound_htlcs.is_empty());
 		assert!(self.context.pending_outbound_htlcs.is_empty());
 		assert!(self.context.pending_update_fee.is_none());
@@ -4369,11 +4369,17 @@ impl<SP: Deref> Channel<SP> where
 		}
 
 		debug_assert!(value_to_counterparty >= 0);
+		if value_to_counterparty < 0 {
+			return Err(ChannelError::close(format!("Value to counterparty below 0: {}", value_to_counterparty)))
+		}
 		if skip_remote_output || value_to_counterparty as u64 <= self.context.holder_dust_limit_satoshis {
 			value_to_counterparty = 0;
 		}
 
 		debug_assert!(value_to_holder >= 0);
+		if value_to_holder < 0 {
+			return Err(ChannelError::close(format!("Value to holder below 0: {}", value_to_holder)))
+		}
 		if value_to_holder as u64 <= self.context.holder_dust_limit_satoshis {
 			value_to_holder = 0;
 		}
@@ -4384,7 +4390,7 @@ impl<SP: Deref> Channel<SP> where
 		let funding_outpoint = self.funding_outpoint().into_bitcoin_outpoint();
 
 		let closing_transaction = ClosingTransaction::new(value_to_holder as u64, value_to_counterparty as u64, holder_shutdown_script, counterparty_shutdown_script, funding_outpoint);
-		(closing_transaction, total_fee_satoshis)
+		Ok((closing_transaction, total_fee_satoshis))
 	}
 
 	fn funding_outpoint(&self) -> OutPoint {
@@ -6138,19 +6144,27 @@ impl<SP: Deref> Channel<SP> where
 			if let Some((fee, skip_remote_output, fee_range, holder_sig)) = self.context.last_sent_closing_fee.clone() {
 				debug_assert!(holder_sig.is_none());
 				log_trace!(logger, "Attempting to generate pending closing_signed...");
-				let (closing_tx, fee) = self.build_closing_transaction(fee, skip_remote_output);
-				let closing_signed = self.get_closing_signed_msg(&closing_tx, skip_remote_output,
-					fee, fee_range.min_fee_satoshis, fee_range.max_fee_satoshis, logger);
-				let signed_tx = if let (Some(ClosingSigned { signature, .. }), Some(counterparty_sig)) =
-					(closing_signed.as_ref(), self.context.last_received_closing_sig) {
-					let funding_redeemscript = self.context.get_funding_redeemscript();
-					let sighash = closing_tx.trust().get_sighash_all(&funding_redeemscript, self.context.channel_value_satoshis);
-					debug_assert!(self.context.secp_ctx.verify_ecdsa(&sighash, &counterparty_sig,
-						&self.context.get_counterparty_pubkeys().funding_pubkey).is_ok());
-					Some(self.build_signed_closing_transaction(&closing_tx, &counterparty_sig, signature))
-				} else { None };
-				let shutdown_result = signed_tx.as_ref().map(|_| self.shutdown_result_coop_close());
-				(closing_signed, signed_tx, shutdown_result)
+				let closing_transaction_result = self.build_closing_transaction(fee, skip_remote_output);
+				match closing_transaction_result {
+					Ok((closing_tx, fee)) => {
+						let closing_signed = self.get_closing_signed_msg(&closing_tx, skip_remote_output,
+																		 fee, fee_range.min_fee_satoshis, fee_range.max_fee_satoshis, logger);
+						let signed_tx = if let (Some(ClosingSigned { signature, .. }), Some(counterparty_sig)) =
+							(closing_signed.as_ref(), self.context.last_received_closing_sig) {
+							let funding_redeemscript = self.context.get_funding_redeemscript();
+							let sighash = closing_tx.trust().get_sighash_all(&funding_redeemscript, self.context.channel_value_satoshis);
+							debug_assert!(self.context.secp_ctx.verify_ecdsa(&sighash, &counterparty_sig,
+																			 &self.context.get_counterparty_pubkeys().funding_pubkey).is_ok());
+							Some(self.build_signed_closing_transaction(&closing_tx, &counterparty_sig, signature))
+						} else { None };
+						let shutdown_result = signed_tx.as_ref().map(|_| self.shutdown_result_coop_close());
+						(closing_signed, signed_tx, shutdown_result)
+					}
+					Err(err) => {
+						let shutdown = self.context.force_shutdown(true, ClosureReason::ProcessingError {err: err.to_string()});
+						(None, None, Some(shutdown))
+					}
+				}
 			} else { (None, None, None) }
 		} else { (None, None, None) };
 
@@ -6618,7 +6632,7 @@ impl<SP: Deref> Channel<SP> where
 		let (our_min_fee, our_max_fee) = self.calculate_closing_fee_limits(fee_estimator);
 
 		assert!(self.context.shutdown_scriptpubkey.is_some());
-		let (closing_tx, total_fee_satoshis) = self.build_closing_transaction(our_min_fee, false);
+		let (closing_tx, total_fee_satoshis) = self.build_closing_transaction(our_min_fee, false)?;
 		log_trace!(logger, "Proposing initial closing_signed for our counterparty with a fee range of {}-{} sat (with initial proposal {} sats)",
 			our_min_fee, our_max_fee, total_fee_satoshis);
 
@@ -6852,7 +6866,7 @@ impl<SP: Deref> Channel<SP> where
 
 		let funding_redeemscript = self.context.get_funding_redeemscript();
 		let mut skip_remote_output = false;
-		let (mut closing_tx, used_total_fee) = self.build_closing_transaction(msg.fee_satoshis, skip_remote_output);
+		let (mut closing_tx, used_total_fee) = self.build_closing_transaction(msg.fee_satoshis, skip_remote_output)?;
 		if used_total_fee != msg.fee_satoshis {
 			return Err(ChannelError::close(format!("Remote sent us a closing_signed with a fee other than the value they can claim. Fee in message: {}. Actual closing tx fee: {}", msg.fee_satoshis, used_total_fee)));
 		}
@@ -6864,7 +6878,7 @@ impl<SP: Deref> Channel<SP> where
 				// The remote end may have decided to revoke their output due to inconsistent dust
 				// limits, so check for that case by re-checking the signature here.
 				skip_remote_output = true;
-				closing_tx = self.build_closing_transaction(msg.fee_satoshis, skip_remote_output).0;
+				closing_tx = self.build_closing_transaction(msg.fee_satoshis, skip_remote_output)?.0;
 				let sighash = closing_tx.trust().get_sighash_all(&funding_redeemscript, self.context.channel_value_satoshis);
 				secp_check!(self.context.secp_ctx.verify_ecdsa(&sighash, &msg.signature, self.context.counterparty_funding_pubkey()), "Invalid closing tx signature from peer".to_owned());
 			},
@@ -6895,7 +6909,7 @@ impl<SP: Deref> Channel<SP> where
 					(closing_tx, $new_fee)
 				} else {
 					skip_remote_output = false;
-					self.build_closing_transaction($new_fee, skip_remote_output)
+					self.build_closing_transaction($new_fee, skip_remote_output)?
 				};
 
 				let closing_signed = self.get_closing_signed_msg(&closing_tx, skip_remote_output, used_fee, our_min_fee, our_max_fee, logger);
```
