# [?] Avoid panic when reorged claims cannot merge

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-07-30
Source: https://github.com/lightningdevkit/rust-lightning/commit/f1dc848727639e34cc98b26db32a6059b4bff3aa
Type: security-commit

## Details
Avoid panic when reorged claims cannot merge

Previously, a deep reorg could resurrect an HTLC package at a height
where it was no longer mergeable with its surviving claim. This caused
`OnchainTxHandler::blocks_disconnected` to panic on an assertion.

When merging fails, we now preserve the resurrected package in
`locktimed_packages` so normal block processing registers and broadcasts
it as an independent claim. Add a regression test covering the reorg and
subsequent broadcast.

Thanks to Kyle W. Santiago for reporting this issue.

Co-authored-by: Elias Rohrer <dev@tnull.de>

## Patch
### lightning/src/chain/onchaintx.rs
```diff
@@ -1180,14 +1180,24 @@ impl<ChannelSigner: EcdsaChannelSigner> OnchainTxHandler<ChannelSigner> {
 
 						if let Some(pending_claim) = self.claimable_outpoints.get(package.outpoints()[0]) {
 							if let Some(request) = self.pending_claim_requests.get_mut(&pending_claim.0) {
-								assert!(request.merge_package(package, new_best_height + 1).is_ok());
-								// Using a HashMap guarantee us than if we have multiple outpoints getting
-								// resurrected only one bump claim tx is going to be broadcast
-								bump_candidates.insert(pending_claim.clone(), request.clone());
+								if request.can_merge_with(&package, new_best_height + 1) {
+									assert!(request.merge_package(package, new_best_height + 1).is_ok());
+									// Using a HashMap guarantee us than if we have multiple outpoints getting
+									// resurrected only one bump claim tx is going to be broadcast
+									bump_candidates.insert(pending_claim.clone(), request.clone());
+									continue;
+								}
 							}
 						}
+						// While we really should push the new package through the generation below
+						// (as it is not, in fact, locktimed to a later height), to avoid additional
+						// complexity we shove the package in the locktimed set instead, which will
+						// result in it getting handled when the reorg processing finishes and the
+						// new tip is connected.
+						let package_locktime = package.package_locktime(0);
+						self.locktimed_packages.entry(package_locktime).or_default().push(package);
 					},
-					_ => {},
+					OnchainEvent::Claim { .. } => {},
 				}
 			} else {
 				self.onchain_events_awaiting_threshold_conf.push(entry);
```

### lightning/src/ln/reorg_tests.rs
```diff
@@ -1357,3 +1357,207 @@ fn test_split_htlc_expiry_tracking() {
 	do_test_split_htlc_expiry_tracking(true, false, true);
 	do_test_split_htlc_expiry_tracking(false, false, true);
 }
+
+fn do_test_reorg_resurrect_split_htlc_package_with_future_locktime(style: ConnectStyle) {
+	// Exercises a failed `request.merge_package(..)` in `OnchainTxHandler::blocks_disconnected`.
+	//
+	// Two of our outbound HTLCs land on the counterparty's commitment with `cltv_expiry` two
+	// blocks apart. If the commitment confirms at a height at or past the *later* expiry, both
+	// timeout claims are immediately spendable, so their `package_locktime` agree and they
+	// aggregate into a single claim. The counterparty then claims only the earlier-expiring HTLC
+	// with its preimage, which splits that input back out into a `ContentiousOutpoint`. On a reorg
+	// back below the later expiry, the split-off package's locktime requirement has been met but
+	// the surviving one's has not, so the two are no longer mergeable and the assert's condition
+	// is false.
+	let chanmon_cfgs = create_chanmon_cfgs(2);
+	let node_cfgs = create_node_cfgs(2, &chanmon_cfgs);
+	// A legacy (non-anchor) channel is required: with anchors the counterparty aggregates both of
+	// its HTLC-success claims into one transaction, which would spend *every* outpoint in our
+	// claim and take the `is_claim_subset_of_tx` path instead of splitting.
+	let legacy_cfg = test_legacy_channel_config();
+	let node_chanmgrs =
+		create_node_chanmgrs(2, &node_cfgs, &[Some(legacy_cfg.clone()), Some(legacy_cfg)]);
+	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
+	*nodes[0].connect_style.borrow_mut() = style;
+	let node_id_0 = nodes[0].node.get_our_node_id();
+	let node_id_1 = nodes[1].node.get_our_node_id();
+
+	let (_, _, chan_id, funding_tx) =
+		create_announced_chan_between_nodes_with_value(&nodes, 0, 1, 10_000_000, 0);
+
+	// Two outbound HTLCs with different amounts (so we can tell their commitment outputs apart)
+	// and `cltv_expiry` exactly two blocks apart.
+	let amt_a_msat = 100_000_000;
+	let amt_b_msat = 200_000_000;
+	let (preimage_a, payment_hash_a, ..) = route_payment(&nodes[0], &[&nodes[1]], amt_a_msat);
+	connect_blocks(&nodes[0], 2);
+	connect_blocks(&nodes[1], 2);
+	let (preimage_b, payment_hash_b, ..) = route_payment(&nodes[0], &[&nodes[1]], amt_b_msat);
+
+	let (cltv_a, cltv_b) = {
+		let chans = nodes[0].node.list_channels();
+		assert_eq!(chans.len(), 1);
+		let mut htlcs = chans[0].pending_outbound_htlcs.clone();
+		assert_eq!(htlcs.len(), 2, "{htlcs:?}");
+		htlcs.sort_by_key(|h| h.cltv_expiry);
+		assert_eq!(htlcs[0].amount_msat, amt_a_msat);
+		assert_eq!(htlcs[1].amount_msat, amt_b_msat);
+		(htlcs[0].cltv_expiry, htlcs[1].cltv_expiry)
+	};
+	println!("[repro] A height after routing = {}", nodes[0].best_block_info().1);
+	println!("[repro] cltv_a = {cltv_a}, cltv_b = {cltv_b}");
+	assert_eq!(cltv_b, cltv_a + 2, "need the expiries exactly 2 apart");
+
+	nodes[0].node.peer_disconnected(node_id_1);
+	nodes[1].node.peer_disconnected(node_id_0);
+
+	// Give node B both preimages so it will claim both HTLCs on-chain.
+	nodes[1].node.claim_funds(preimage_a);
+	expect_payment_claimed!(nodes[1], payment_hash_a, amt_a_msat);
+	nodes[1].node.claim_funds(preimage_b);
+	expect_payment_claimed!(nodes[1], payment_hash_b, amt_b_msat);
+	check_added_monitors(&nodes[1], 2);
+
+	// Node B force-closes, giving us its commitment transaction.
+	let err = "Channel force-closed".to_string();
+	nodes[1].node.force_close_broadcasting_latest_txn(&chan_id, &node_id_0, err).unwrap();
+	check_closed_broadcast(&nodes[1], 1, false);
+	check_added_monitors(&nodes[1], 1);
+	let message = "Channel force-closed".to_owned();
+	let reason = ClosureReason::HolderForceClosed { broadcasted_latest_txn: Some(true), message };
+	check_closed_event(&nodes[1], 1, reason, &[node_id_0], 10_000_000);
+
+	// On a legacy channel node B knows both preimages, so it broadcasts its commitment together
+	// with a separate, pre-signed HTLC-success transaction per HTLC.
+	let mut bs_txn = nodes[1].tx_broadcaster.txn_broadcast();
+	println!("[repro] node B broadcast {} txn on force-close", bs_txn.len());
+	assert_eq!(bs_txn.len(), 3, "{bs_txn:?}");
+	let commitment_tx = bs_txn.remove(0);
+	check_spends!(commitment_tx, funding_tx);
+	let commitment_txid = commitment_tx.compute_txid();
+	for tx in bs_txn.iter() {
+		check_spends!(tx, commitment_tx);
+		assert_eq!(tx.input.len(), 1);
+	}
+	// Take only the HTLC-success transaction for the *earlier*-expiring HTLC, identified by the
+	// value of the commitment output it spends.
+	let partial_claim_tx = bs_txn
+		.into_iter()
+		.find(|tx| {
+			tx.input.len() == 1
+				&& tx.input[0].previous_output.txid == commitment_txid
+				&& commitment_tx.output[tx.input[0].previous_output.vout as usize].value.to_sat()
+					== amt_a_msat / 1000
+		})
+		.expect("node B should have a single-input HTLC-success tx for the earlier HTLC");
+	println!(
+		"[repro] node B partial claim spends {}:{} (value {} sat)",
+		partial_claim_tx.input[0].previous_output.txid,
+		partial_claim_tx.input[0].previous_output.vout,
+		commitment_tx.output[partial_claim_tx.input[0].previous_output.vout as usize]
+			.value
+			.to_sat(),
+	);
+
+	// Advance node A so that the block containing the commitment lands at exactly `cltv_b`. Note
+	// this stays below `cltv_a + LATENCY_GRACE_PERIOD_BLOCKS`, so node A does not force-close on
+	// its own first.
+	let a_height = nodes[0].best_block_info().1;
+	assert!(a_height < cltv_b - 1, "a_height {a_height} cltv_b {cltv_b}");
+	connect_blocks(&nodes[0], cltv_b - 1 - a_height);
+	assert_eq!(nodes[0].best_block_info().1, cltv_b - 1);
+	assert_eq!(nodes[0].tx_broadcaster.txn_broadcast().len(), 0);
+
+	mine_transaction(&nodes[0], &commitment_tx);
+	let commitment_conf_height = nodes[0].best_block_info().1;
+	println!("[repro] commitment confirmed on A at height {commitment_conf_height}");
+	assert_eq!(commitment_conf_height, cltv_b);
+	check_closed_broadcast(&nodes[0], 1, false);
+	let reason = ClosureReason::CommitmentTxConfirmed;
+	check_closed_event(&nodes[0], 1, reason, &[node_id_1], 10_000_000);
+	check_added_monitors(&nodes[0], 1);
+
+	// Both timeout claims must have aggregated into a single transaction, otherwise the path we
+	// are trying to reach does not exist.
+	{
+		let txn = nodes[0].tx_broadcaster.txn_broadcast();
+		println!("[repro] node A broadcast {} txn when the commitment confirmed:", txn.len());
+		for tx in txn.iter() {
+			println!(
+				"[repro]   txid {} locktime {} inputs {:?}",
+				tx.compute_txid(),
+				tx.lock_time.to_consensus_u32(),
+				tx.input.iter().map(|i| i.previous_output).collect::<Vec<_>>(),
+			);
+		}
+		let aggregated = txn
+			.iter()
+			.find(|tx| {
+				tx.input.len() == 2
+					&& tx.input.iter().all(|i| i.previous_output.txid == commitment_txid)
+			})
+			.expect("node A must aggregate both HTLC timeout claims into one transaction");
+		assert_eq!(aggregated.lock_time.to_consensus_u32(), cltv_b);
+	}
+
+	// Now confirm the counterparty's preimage claim of the earlier HTLC, splitting it back out of
+	// our aggregated claim.
+	mine_transaction(&nodes[0], &partial_claim_tx);
+	let spend_conf_height = nodes[0].best_block_info().1;
+	println!("[repro] node B's partial claim confirmed on A at height {spend_conf_height}");
+	{
+		let txn = nodes[0].tx_broadcaster.txn_broadcast();
+		println!("[repro] node A broadcast {} txn after the split:", txn.len());
+		for tx in txn.iter() {
+			println!(
+				"[repro]   txid {} locktime {} inputs {:?}",
+				tx.compute_txid(),
+				tx.lock_time.to_consensus_u32(),
+				tx.input.iter().map(|i| i.previous_output).collect::<Vec<_>>(),
+			);
+		}
+	}
+
+	// Node A learned both preimages from node B's on-chain claim, so drain the resulting payment
+	// events; we want the only possible failure below to be the one we are testing for.
+	nodes[0].node.get_and_clear_pending_events();
+	check_added_monitors(&nodes[0], 1);
+
+	// Reorg back to `cltv_b - 2`, which is `cltv_a`. The resurrected package (locktime `cltv_a`)
+	// is spendable, but the surviving request still requires locktime `cltv_b`.
+	let disconnect = spend_conf_height - cltv_b + 2;
+	let new_best_height = spend_conf_height - disconnect;
+	println!(
+		"[repro] disconnecting {disconnect} blocks: new_best_height will be {new_best_height} \
+		 (cltv_a {cltv_a}, cltv_b {cltv_b}); re-merge is evaluated at {}",
+		new_best_height + 1,
+	);
+	assert!(cltv_a <= new_best_height);
+	assert!(new_best_height + 1 < cltv_b);
+	disconnect_blocks(&nodes[0], disconnect);
+	println!("[repro] survived the disconnect, height now {}", nodes[0].best_block_info().1);
+
+	// The failed merge must not discard the resurrected package. On the next block it should be
+	// registered as an independent claim and broadcast on its own.
+	connect_blocks(&nodes[0], 1);
+	let early_htlc_outpoint = partial_claim_tx.input[0].previous_output;
+	let txn = nodes[0].tx_broadcaster.txn_broadcast();
+	let independent_claim = txn
+		.iter()
+		.find(|tx| tx.input.len() == 1 && tx.input[0].previous_output == early_htlc_outpoint)
+		.expect("the resurrected HTLC package must be broadcast as an independent claim");
+	assert_eq!(independent_claim.lock_time.to_consensus_u32(), new_best_height + 1);
+}
+
+#[test]
+fn test_reorg_resurrect_split_htlc_package_with_future_locktime() {
+	// `FullBlockDisconnectionsSkippingViaListen` issues a single `blocks_disconnected` call with
+	// the fork point, which is what `lightning-block-sync` does after detecting a reorg. The
+	// styles which instead walk the chain backwards one block at a time re-merge successfully on
+	// the first (shallowest) disconnection, and the `*ReorgsOnlyTip` styles go through
+	// `transaction_unconfirmed`, which disconnects only to `entry.height - 1`; neither reaches the
+	// case below.
+	do_test_reorg_resurrect_split_htlc_package_with_future_locktime(
+		ConnectStyle::FullBlockDisconnectionsSkippingViaListen,
+	);
+}
```
