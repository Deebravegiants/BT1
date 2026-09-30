# [?] Merge pull request #4716 from tnull/tnull/2026-05-fix-route-hint-overflow

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-06-18
Source: https://github.com/lightningdevkit/rust-lightning/commit/61e3cabc73a76da5ca8197f1095428cca521b932
Type: security-commit

## Details
Merge pull request #4716 from tnull/tnull/2026-05-fix-route-hint-overflow

Handle overflowing route-hint fee aggregates

## Patch
### lightning/src/routing/router.rs
```diff
@@ -2428,10 +2428,12 @@ impl<'a> PaymentPath<'a> {
 	/// contribution this path can make to the final value of the payment.
 	/// May be slightly lower than the actual max due to rounding errors when aggregating fees
 	/// along the path.
+	/// Returns an error with the index of a later hop to discard if the following hops' aggregate
+	/// fees overflow.
 	#[rustfmt::skip]
 	fn max_final_value_msat(
 		&self, used_liquidities: &HashMap<CandidateHopId, u64>, channel_saturation_pow_half: u8
-	) -> (usize, u64) {
+	) -> Result<(usize, u64), usize> {
 		let mut max_path_contribution = (0, u64::MAX);
 		for (idx, (hop, _)) in self.hops.iter().enumerate() {
 			let hop_effective_capacity_msat = hop.candidate.effective_capacity();
@@ -2447,7 +2449,8 @@ impl<'a> PaymentPath<'a> {
 			// Aggregate the fees of the hops that come after this one, and use those fees to compute the
 			// maximum amount that this hop can contribute to the final value received by the payee.
 			let (next_hops_aggregated_base, next_hops_aggregated_prop) =
-				crate::blinded_path::payment::compute_aggregated_base_prop_fee(next_hops_feerates_iter).unwrap();
+				crate::blinded_path::payment::compute_aggregated_base_prop_fee(next_hops_feerates_iter)
+					.map_err(|_| idx + 1)?;
 
 			// floor(((hop_max_msat - agg_base) * 1_000_000) / (1_000_000 + agg_prop))
 			let hop_max_final_value_contribution = (hop_max_msat as u128)
@@ -2464,7 +2467,19 @@ impl<'a> PaymentPath<'a> {
 			} else { debug_assert!(false); }
 		}
 
-		max_path_contribution
+		Ok(max_path_contribution)
+	}
+}
+
+fn mark_candidate_liquidity_exhausted(
+	used_liquidities: &mut HashMap<CandidateHopId, u64>, candidate: &CandidateRouteHop,
+) {
+	let exhausted = u64::max_value();
+	if let Some(scid) = candidate.short_channel_id() {
+		*used_liquidities.entry(CandidateHopId::Clear((scid, false))).or_default() = exhausted;
+		*used_liquidities.entry(CandidateHopId::Clear((scid, true))).or_default() = exhausted;
+	} else {
+		*used_liquidities.entry(candidate.id()).or_default() = exhausted;
 	}
 }
 
@@ -3644,7 +3659,17 @@ pub(crate) fn get_route<L: Logger, S: ScoreLookUp>(
 				// underpaid htlc_minimum_msat with fees.
 				debug_assert_eq!(payment_path.get_value_msat(), value_contribution_msat);
 				let (lowest_value_contrib_hop, max_path_contribution_msat) =
-					payment_path.max_final_value_msat(&used_liquidities, channel_saturation_pow_half);
+					match payment_path.max_final_value_msat(&used_liquidities, channel_saturation_pow_half) {
+						Ok(contribution) => contribution,
+						Err(candidate_idx_to_skip) => {
+							let candidate = &payment_path.hops[candidate_idx_to_skip].0.candidate;
+							log_trace!(logger,
+								"Ignoring path because aggregate fees including hop {} overflow.",
+								LoggedCandidateHop(candidate));
+							mark_candidate_liquidity_exhausted(&mut used_liquidities, candidate);
+							continue 'paths_collection;
+						}
+					};
 				let desired_value_contribution = cmp::min(max_path_contribution_msat, final_value_msat);
 				value_contribution_msat = payment_path.update_value_and_recompute_fees(desired_value_contribution);
 
@@ -9389,6 +9414,67 @@ mod tests {
 		assert_eq!(route.paths[0].hops[0].short_channel_id, 44);
 	}
 
+	#[test]
+	fn aggregated_prop_fee_overflow_fails_route() {
+		// If the fee cap is disabled, we may consider invoice hints with very large
+		// proportional fees. Aggregating those fees can overflow, in which case we should fail
+		// routing cleanly rather than panic.
+		let secp_ctx = Secp256k1::new();
+		let logger = Arc::new(ln_test_utils::TestLogger::new());
+		let network_graph = Arc::new(NetworkGraph::new(Network::Testnet, Arc::clone(&logger)));
+		let scorer = ln_test_utils::TestScorer::new();
+		let random_seed_bytes = [42; 32];
+		let config = UserConfig::default();
+
+		let (_, our_node_id, _, nodes) = get_nodes(&secp_ctx);
+		let route_hint = RouteHint(vec![
+			RouteHintHop {
+				src_node_id: nodes[0],
+				short_channel_id: 100,
+				fees: RoutingFees { base_msat: 0, proportional_millionths: u32::MAX },
+				cltv_expiry_delta: 10,
+				htlc_minimum_msat: None,
+				htlc_maximum_msat: None,
+			},
+			RouteHintHop {
+				src_node_id: nodes[1],
+				short_channel_id: 101,
+				fees: RoutingFees { base_msat: 0, proportional_millionths: u32::MAX },
+				cltv_expiry_delta: 10,
+				htlc_minimum_msat: None,
+				htlc_maximum_msat: None,
+			},
+		]);
+
+		let payment_params = PaymentParameters::from_node_id(nodes[2], 42)
+			.with_route_hints(vec![route_hint])
+			.unwrap()
+			.with_bolt11_features(channelmanager::provided_bolt11_invoice_features(&config))
+			.unwrap();
+		let first_hops = [get_channel_details(
+			Some(1),
+			nodes[0],
+			channelmanager::provided_init_features(&config),
+			100_000_000,
+		)];
+		let route_params = RouteParameters {
+			payment_params,
+			final_value_msat: 1,
+			max_total_routing_fee_msat: None,
+		};
+		let route = get_route(
+			&our_node_id,
+			&route_params,
+			&network_graph.read_only(),
+			Some(&first_hops.iter().collect::<Vec<_>>()),
+			Arc::clone(&logger),
+			&scorer,
+			&Default::default(),
+			&random_seed_bytes,
+		);
+		assert!(route.is_err());
+	}
+
 	#[test]
 	fn prefers_paths_by_cost_amt_ratio() {
 		// Previously, we preferred paths during MPP selection based on their absolute cost, rather
```
