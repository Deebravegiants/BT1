### Title
Overpaid XCM execution fees are forfeited to `OnUnbalanced` instead of refunded when a user fills the holding register to capacity - ([File: polkadot/xcm/xcm-executor/src/lib.rs])

### Summary
`XcmExecutor::refund_surplus` (`polkadot/xcm/xcm-executor/src/lib.rs:540-596`) attempts to place the trader's weight refund back into the `holding` register, guarded by `ensure_can_subsume_assets` (`polkadot/xcm/xcm-executor/src/lib.rs:524-538`). When holding is already at its maximum permitted size and the refunded asset's key is not present in holding, the guard fails, and the executor "undoes" the refund by calling `trader.buy_weight()` again on the refund credit rather than returning it to the payer. That credit is then consumed by the trader and handed to the configured `OnUnbalanced` sink when the trader is dropped, instead of being returned to the account that overpaid.

### Finding Description
The relevant flow is:

1. `ensure_can_subsume_assets(assets_length)` (`polkadot/xcm/xcm-executor/src/lib.rs:524-538`) permits `holding.len()` to grow only up to `2 * holding_limit` in total across the message's lifetime, and every holding-adding instruction (`WithdrawAsset`, `ReserveAssetDeposited`, `ReceiveTeleportedAsset`, `ClaimAsset`, `ExchangeAsset`) enforces this bound before subsuming new assets: [1](#0-0) 
2. A user-controlled message can pay for execution with `BuyExecution`, fully consuming the paying asset out of holding (zero left over), then, in a *separate* instruction, `WithdrawAsset` a set of distinct "dust" assets whose count fills holding up to the `2 * holding_limit` cap. Since the fee-paying asset is no longer one of the assets occupying holding, this is legal under the same-length check, unlike the case where the fee asset's key still resides in holding (which the design otherwise protects against).
3. When `refund_surplus()` runs — either implicitly at `post_process` (`polkadot/xcm/xcm-executor/src/lib.rs:399-403`, error silently dropped) or explicitly via a `RefundSurplus` instruction — the trader produces a refund in the fee-paying asset's id, but that id is absent from holding and holding is already at the `2 * holding_limit` cap, so `ensure_can_subsume_assets(1)` returns `Err`. [2](#0-1) 
4. On that failure, the executor calls `self.trader.buy_weight(current_surplus, refund, ...)` to "give the refund back to the trader" instead of the user. This re-consumes the credit into the trader's internal state; when the trader is dropped (`polkadot/xcm/xcm-executor/src/lib.rs:403`), the credit is resolved via the configured `OnUnbalanced` handler (e.g., `ResolveTo<StakingPot, Balances>` in various runtime configs), not returned to the payer. [3](#0-2) 
5. `post_process` swallows the `HoldingWouldOverflow` error from the implicit refund attempt ("best-effort... we silently drop any error"), so the message still completes successfully while the fee credit has been silently forfeited. [4](#0-3) 

The `2x` headroom in `ensure_can_subsume_assets` is specifically designed so that when the fee-asset itself is still occupying a holding slot before `BuyExecution`, freeing that slot always creates enough room for its own refund (proven by the arithmetic: max reachable `holding.len()` is exactly `2 * holding_limit`, and removing the fee-asset key frees exactly one slot). However, this safety margin does **not** hold when the fee-paying asset is fully consumed and removed from holding *before* other distinct dust assets are subsequently loaded up to the `2 * holding_limit` cap — a sequencing fully controlled by the message author.

### Impact Explanation
Legitimately overpaid XCM execution fees are not returned to the account that paid them; instead, the credit is redirected to whatever `OnUnbalanced` sink the runtime configures for the `Trader` (e.g., `StakingPot`/treasury), a silent and deterministic loss of the user's own funds each time this pattern is used. Because each XCM message gets a fresh `XcmExecutor` (and fresh `Trader::new()` / empty `holding`) per `prepare_and_execute` call, the loss is confined to the message's own paying account — it is a self-inflicted, but fully attacker/user-controlled and repeatable, forfeiture of that user's overpaid fee, not a cross-user drain (trader/holding state is not shared across messages).

### Likelihood Explanation
The attacker needs no special privileges: any signed account (or contract/precompile issuing XCM, or a parachain sending an XCM to itself/another chain that it controls the message contents for) that owns enough distinct asset types to withdraw as "dust" can reliably reproduce this on every execution. The precondition — owning up to `2 * MaxAssetsIntoHolding` distinct asset ids — is achievable on chains with permissionless or cheap asset creation (e.g., `pallet-assets`), making the pattern fully reproducible and deterministic once holding is filled to capacity right after the fee asset's key is evicted.

### Recommendation
Do not "buy back" the refund into the trader silently forfeiting it to `OnUnbalanced` when holding cannot accept it. Instead, either (a) trap the un-subsumable refund via `Config::AssetTrap::drop_assets` so the payer can reclaim it with `ClaimAsset`, or (b) reserve capacity for the trader's own refund asset id in `ensure_can_subsume_assets`/holding-limit accounting so the refund is guaranteed to fit regardless of instruction ordering, rather than relying on the incidental slot freed by consuming the fee asset in `BuyExecution`.

### Proof of Concept
Rust unit test in `polkadot/xcm/xcm-executor/src/tests/` (using the existing `TestTrader`/mock harness):
1. Set `MaxAssetsIntoHolding = L` (small, e.g. 4) in the test config.
2. Build an `Xcm` that: `WithdrawAsset(fee_asset, exact_amount_for_huge_weight)`, `BuyExecution { fees: fee_asset_exact_amount, weight_limit: Limited(huge_weight) }`, then `WithdrawAsset` with `2*L` distinct dust asset ids (none equal to `fee_asset`), then a couple of cheap instructions, then `RefundSurplus`, `DepositAsset { assets: All, beneficiary: payer }`.
3. Assert: processing yields `Outcome::Incomplete { error: InstructionError { error: XcmError::HoldingWouldOverflow, .. }, .. }` when `RefundSurplus` is explicit, or, using the implicit end-of-program refund path, assert that the payer's post-execution asset balance for `fee_asset` does NOT include the expected refund (i.e., `asset_list(payer)` lacks the weight-refund amount), while the `OnUnbalanced`/fee-sink account balance increased by exactly that amount.
4. Repeat the run multiple times to show the loss is deterministic and repeatable on every execution that follows this pattern, quantifying the forfeited amount as `WeightToFee::weight_to_fee(current_surplus)`.

### Citations

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L399-403)
```rust
	pub fn post_process(mut self, xcm_weight: Weight) -> Outcome {
		// We silently drop any error from our attempt to refund the surplus as it's a charitable
		// thing so best-effort is all we will do.
		let _ = self.refund_surplus();
		drop(self.trader);
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L524-538)
```rust
	fn ensure_can_subsume_assets(&self, assets_length: usize) -> Result<(), XcmError> {
		// worst-case, holding.len becomes 2 * holding_limit.
		// this guarantees that if holding.len() == holding_limit and you have more than
		// `holding_limit` items (which has a best case outcome of holding.len() == holding_limit),
		// then the operation is guaranteed to succeed.
		let worst_case_holding_len = self.holding.len() + assets_length;
		tracing::trace!(
			target: "xcm::ensure_can_subsume_assets",
			?worst_case_holding_len,
			holding_limit = ?self.holding_limit,
			"Ensuring subsume assets work",
		);
		ensure!(worst_case_holding_len <= self.holding_limit * 2, XcmError::HoldingWouldOverflow);
		Ok(())
	}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L550-577)
```rust
		if current_surplus.any_gt(Weight::zero()) {
			if let Some(refund) = self.trader.refund_weight(current_surplus, &self.context) {
				// Check if adding the refund would overflow holding. This can happen if the
				// refund asset is not already in holding and holding is at max capacity.
				if refund
					.fungible
					.first_key_value()
					.map(|(id, _)| {
						!self.holding.fungible.contains_key(id) &&
							self.ensure_can_subsume_assets(1).is_err()
					})
					.unwrap_or(false)
				{
					// Can't add refund to holding - undo by buying back the weight.
					// This returns the refund credit to the trader where it will be
					// handled by OnUnbalanced when the trader is dropped.
					let _ = self
						.trader
						.buy_weight(current_surplus, refund, &self.context)
						.defensive_proof(
							"refund_weight returned an asset capable of buying weight; qed",
						);
					tracing::error!(
						target: "xcm::refund_surplus",
						"error: HoldingWouldOverflow",
					);
					return Err(XcmError::HoldingWouldOverflow);
				}
```
