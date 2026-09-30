# [?] apollo_consensus_orchestrator: anchor L1 gas-price margin to local reference and harden overflow (#14589)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-07-02
Source: https://github.com/starkware-libs/sequencer/commit/5a98bd1e3619bdd878cdd60f1d4bbcf67a2a69ab
Type: security-commit

## Details
apollo_consensus_orchestrator: anchor L1 gas-price margin to local reference and harden overflow (#14589)

within_margin anchored the tolerance band to the proposer-supplied price (number1),
so the accepted band scaled with attacker input: a proposer could inflate the L1 gas
price up to ~1.111x the local reference instead of the intended 1.10x (M-17). The same
line also did an unchecked u128 * u128 that can overflow on large WEI prices.

Anchor the band to the locally-trusted reference and use saturating_mul. The accepted
band is now the symmetric [reference*(1-m), reference*(1+m)]. Parameters renamed to
proposed/reference to make the trusted argument unambiguous; call sites already pass
(proposed, reference) so no call-site change is needed.

Adds regression cases including the inflated-proposal exploit (1111 vs 1000 at 10% must
be rejected), boundary-inclusive cases, and overflow-hardening cases with u128::MAX.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### crates/apollo_consensus_orchestrator/src/validate_proposal.rs
```diff
@@ -418,16 +418,23 @@ async fn is_proposal_init_valid(
     Ok(())
 }
 
-fn within_margin(number1: GasPrice, number2: GasPrice, margin_percent: u128) -> bool {
+/// Returns whether `proposed` is within `margin_percent` of the locally-trusted `reference`,
+/// i.e. within the symmetric band `[reference*(1-m), reference*(1+m)]`.
+///
+/// The band is anchored to `reference` (the node's own L1 oracle read), not to the
+/// proposer-supplied `proposed`: anchoring to `proposed` would let a malicious proposer scale the
+/// band width with its own input and widen it in its favor.
+fn within_margin(proposed: GasPrice, reference: GasPrice, margin_percent: u128) -> bool {
     // For small numbers (e.g., less than 10 wei, if margin is 10%), even an off-by-one
     // error might be bigger than the margin, even if it is just a rounding error.
     // We make an exception for such mismatch, and don't bother checking percentages
     // if the difference in price is only one wei.
-    if number1.0.abs_diff(number2.0) <= GAS_PRICE_ABS_DIFF_MARGIN {
+    if proposed.0.abs_diff(reference.0) <= GAS_PRICE_ABS_DIFF_MARGIN {
         return true;
     }
-    let margin = (number1.0 * margin_percent) / 100;
-    number1.0.abs_diff(number2.0) <= margin
+    // Saturate: `reference.0 * margin_percent` can overflow u128 on large WEI prices.
+    let margin = reference.0.saturating_mul(margin_percent) / 100;
+    proposed.0.abs_diff(reference.0) <= margin
 }
 
 // The second proposal part when validating a proposal must be:
```

### crates/apollo_consensus_orchestrator/src/validate_proposal_test.rs
```diff
@@ -544,17 +544,34 @@ async fn invalid_starknet_version() {
         if msg.contains("starknet_version mismatch")));
 }
 
+// Cases are (proposed, reference, margin_percent, expected). The band is anchored to `reference`.
 #[rstest]
 #[case::big_number_in_margin(1000, 1050, 10, true)]
 #[case::big_number_out_of_margin(1000, 1150, 10, false)]
 #[case::small_number_in_margin(9, 10, 10, true)]
 #[case::small_number_out_of_margin(9, 11, 10, false)]
 #[case::identical_numbers(12345, 12345, 1, true)]
+// Reference-anchored margin is 1000*10/100 = 100 < diff 111, so this is rejected; a
+// proposed-anchored margin would be 1111*10/100 = 111 and would wrongly accept it.
+#[case::inflated_proposed_rejected(1111, 1000, 10, false)]
+#[case::upper_bound_inclusive(1100, 1000, 10, true)]
+#[case::lower_bound_inclusive(900, 1000, 10, true)]
+#[case::deflated_proposed_rejected(889, 1000, 10, false)]
+// Equal values hit the abs_diff early return, before the margin multiply.
+#[case::large_identical_no_overflow(u128::MAX, u128::MAX, 10, true)]
+// Differs by >1 wei, so this reaches and exercises the saturating multiply on a huge reference.
+#[case::large_within_no_overflow(u128::MAX - 5, u128::MAX, 10, true)]
 fn test_within_margin(
-    #[case] a: u128,
-    #[case] b: u128,
+    #[case] proposed: u128,
+    #[case] reference: u128,
     #[case] margin: u128,
     #[case] expected: bool,
 ) {
-    assert_eq!(within_margin(GasPrice(a), GasPrice(b), margin), expected);
+    assert_eq!(within_margin(GasPrice(proposed), GasPrice(reference), margin), expected);
+}
+
+// A far-out proposed against a huge reference must reject without overflowing the margin multiply.
+#[test]
+fn within_margin_large_reference_does_not_overflow() {
+    assert!(!within_margin(GasPrice(1), GasPrice(u128::MAX), 10));
 }
```
