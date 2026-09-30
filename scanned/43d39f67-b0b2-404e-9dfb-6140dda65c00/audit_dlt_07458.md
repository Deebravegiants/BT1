# [?] Fix deadlock when handling bad calls to `batch_funding.._generated`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-01-22
Source: https://github.com/lightningdevkit/rust-lightning/commit/983ca37a97eeabea86bbe864eb4688e86a4c41d4
Type: security-commit

## Details
Fix deadlock when handling bad calls to `batch_funding.._generated`

When handling calls to `batch_funding_transaction_generated` which
were missing outputs for one of the batch channels, we'd previously
deadlock when trying to clean up the now-closed channels. This
fixes that and adds a new test case for it.

Found by the full_stack_target fuzzer.

## Patch
### lightning/src/ln/channelmanager.rs
```diff
@@ -3984,6 +3984,7 @@ where
 						});
 				}
 			}
+			mem::drop(funding_batch_states);
 			for shutdown_result in shutdown_results.drain(..) {
 				self.finish_close_channel(shutdown_result);
 			}
```

### lightning/src/ln/shutdown_tests.rs
```diff
@@ -7,15 +7,16 @@
 // You may not use this file except in accordance with one or both of these
 // licenses.
 
-//! Tests of our shutdown and closing_signed negotiation logic.
+//! Tests of our shutdown and closing_signed negotiation logic as well as some assorted force-close
+//! handling tests.
 
 use crate::sign::{EntropySource, SignerProvider};
 use crate::chain::ChannelMonitorUpdateStatus;
 use crate::chain::transaction::OutPoint;
-use crate::events::{MessageSendEvent, HTLCDestination, MessageSendEventsProvider, ClosureReason};
+use crate::events::{Event, MessageSendEvent, HTLCDestination, MessageSendEventsProvider, ClosureReason};
 use crate::ln::channelmanager::{self, PaymentSendFailure, PaymentId, RecipientOnionFields, Retry, ChannelShutdownState, ChannelDetails};
 use crate::routing::router::{PaymentParameters, get_route, RouteParameters};
-use crate::ln::msgs;
+use crate::ln::{ChannelId, msgs};
 use crate::ln::msgs::{ChannelMessageHandler, ErrorAction};
 use crate::ln::onion_utils::INVALID_ONION_BLINDING;
 use crate::ln::script::ShutdownScript;
@@ -25,6 +26,8 @@ use crate::util::errors::APIError;
 use crate::util::config::UserConfig;
 use crate::util::string::UntrustedString;
 
+use bitcoin::{Transaction, TxOut};
+use bitcoin::blockdata::locktime::absolute::LockTime;
 use bitcoin::blockdata::script::Builder;
 use bitcoin::blockdata::opcodes;
 use bitcoin::network::constants::Network;
@@ -1375,3 +1378,41 @@ fn outbound_update_no_early_closing_signed() {
 	do_outbound_update_no_early_closing_signed(true);
 	do_outbound_update_no_early_closing_signed(false);
 }
+
+#[test]
+fn batch_funding_failure() {
+	// Provides test coverage of batch funding failure, which previously deadlocked
+	let chanmon_cfgs = create_chanmon_cfgs(4);
+	let node_cfgs = create_node_cfgs(4, &chanmon_cfgs);
+	let node_chanmgrs = create_node_chanmgrs(4, &node_cfgs, &[None, None, None, None]);
+	let nodes = create_network(4, &node_cfgs, &node_chanmgrs);
+
+	exchange_open_accept_chan(&nodes[0], &nodes[1], 1_000_000, 0);
+	exchange_open_accept_chan(&nodes[0], &nodes[2], 1_000_000, 0);
+
+	let events = nodes[0].node.get_and_clear_pending_events();
+	assert_eq!(events.len(), 2);
+	// Build a transaction which only has the output for one of the two channels we're trying to
+	// confirm. Previously this led to a deadlock in channel closure handling.
+	let mut tx = Transaction { version: 2, lock_time: LockTime::ZERO, input: Vec::new(), output: Vec::new() };
+	let mut chans = Vec::new();
+	for (idx, ev) in events.iter().enumerate() {
+		if let Event::FundingGenerationReady { temporary_channel_id, counterparty_node_id, output_script, .. } = ev {
+			if idx == 0 {
+				tx.output.push(TxOut { value: 1_000_000, script_pubkey: output_script.clone() });
+			}
+			chans.push((temporary_channel_id, counterparty_node_id));
+		} else { panic!(); }
+	}
+
+	// We should probably end up with an error for both channels, but currently we don't generate
+	// an error for the failing channel itself.
+	let err = "Error in transaction funding: Misuse error: No output matched the script_pubkey and value in the FundingGenerationReady event".to_string();
+	let close = [ExpectedCloseEvent::from_id_reason(ChannelId::v1_from_funding_txid(tx.txid().as_ref(), 0), true, ClosureReason::ProcessingError { err })];
+
+	nodes[0].node.batch_funding_transaction_generated(&chans, tx).unwrap_err();
+
+	get_event_msg!(nodes[0], MessageSendEvent::SendFundingCreated, nodes[1].node.get_our_node_id());
+	check_closed_events(&nodes[0], &close);
+	assert_eq!(nodes[0].node.list_channels().len(), 0);
+}
```
