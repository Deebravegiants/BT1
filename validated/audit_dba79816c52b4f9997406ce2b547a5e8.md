Audit Report

## Title
`refund_surplus`'s holding-overflow "buy-back" fallback always fails and permanently burns the attacker's already-collected fee instead of refunding or crediting it - (File: `polkadot/xcm/xcm-executor/src/lib.rs`)

## Summary
When `XcmExecutor::refund_surplus` cannot merge a trader refund into `holding` (because `ensure_can_subsume_assets` fails), it attempts a "buy-back" via `self.trader.buy_weight(...)` to restore the credit to the trader. For `cumulus_primitives_utility::TakeFirstAssetTrader`, this call is unconditionally rejected by the trader's re-entrancy guard, since `refund_weight` never clears `outstanding_credit` back to `None`. The resulting `Err` is silently discarded via `defensive_proof`, dropping the `AssetsInHolding` wrapping the extracted `fungibles::Credit`, whose `Drop`/imbalance-resolution path decreases total issuance — burning the already-collected fee instead of refunding it to the user or crediting it to fee revenue.

## Finding Description
`TakeFirstAssetTrader::buy_weight` guards against re-entry with `if self.outstanding_credit.is_some() { return Err((payment, XcmError::NotWithdrawable)); }`, confirmed at cumulus/primitives/utility/src/lib.rs lines 180-183. [1](#0-0) 

`refund_weight` extracts a portion of `outstanding_credit` via `outstanding_credit.extract(...)` but never sets the field back to `None` — it remains `Some(...)` with a reduced balance. [2](#0-1) 

`XcmExecutor::refund_surplus` checks whether the refund can be subsumed into holding; if `ensure_can_subsume_assets(1)` fails for a new asset ID, it calls `self.trader.buy_weight(current_surplus, refund, &self.context)` as a "buy back," expecting success, and discards the result with `let _ = ...defensive_proof(...)`. [3](#0-2) 

`Defensive::defensive_proof` for `Result` only logs and passes through the original `Err` unchanged — it performs no recovery. [4](#0-3) 

Since `outstanding_credit` is still `Some(...)` at the time of the buy-back call (never reset by `refund_weight`), `buy_weight` always hits its re-entrancy guard and returns `Err((refund, XcmError::NotWithdrawable))`. This discards the tuple, including the `refund: AssetsInHolding` containing the withdrawn `fungibles::Credit`. `AssetsInHolding::fungible` holds `Box<dyn ImbalanceAccounting<u128>>` entries, confirmed in the struct definition at polkadot/xcm/xcm-executor/src/assets.rs lines 90-97; dropping this map resolves/drops the underlying imbalance, which for a `Credit` decreases total issuance (per the `OnDropCredit`/`Balanced` contract used throughout the codebase). [5](#0-4) 

The existing `ensure_can_subsume_assets` check is only an overflow guard on holding size, and does not address the trader re-entrancy semantics being violated by the fallback path. This makes the "buy back" recovery path dead code that always fails and always destroys value whenever it is exercised.

## Impact Explanation
Whenever this holding-overflow edge case is hit, the surplus fee amount that should have been refunded is neither returned to the user nor routed to `OnUnbalanced`/fee revenue — it is silently burned via the imbalance drop-issuance-decrease path. This is a genuine, unrecoverable loss of already-collected user funds, violating the invariant that debited funds must be fully accounted for (refunded, held, or credited as fee revenue). It also aborts the enclosing XCM program instruction with `XcmError::HoldingWouldOverflow`, compounding user-facing unexpected behavior.

## Likelihood Explanation
The trigger path is reachable by an unprivileged signed account via `pallet_xcm::execute` (or an equivalent XCM message), requiring only: filling `holding` with enough distinct asset IDs (feasible using permissionlessly-creatable `pallet-assets` asset IDs on chains like Asset Hub) to approach `2 * MaxAssetsIntoHolding`, then using a not-yet-held fee asset in `BuyExecution`/`PayFees`, consuming less weight than purchased, and calling `RefundSurplus`. No privileged origin or admin action is required, and the condition can also occur unintentionally for legitimate users with many distinct asset holdings, making it realistically repeatable.

## Recommendation
Do not rely on `WeightTrader::buy_weight`'s re-entrancy guard as a recovery mechanism in `refund_surplus`. Preferable fixes:
- Add a dedicated, guard-free `WeightTrader` method (e.g., `restore_refund`) to reinsert previously-extracted credit into `outstanding_credit`, or
- Make `TakeFirstAssetTrader::refund_weight`'s extraction reversible/transactional until the caller confirms successful placement into holding, or
- In `refund_surplus`, on buy-back failure, explicitly forward the discarded `refund` assets to `Config::FeeManager::handle_fee` (or an equivalent trap/claim mechanism) rather than allowing them to be silently dropped.

## Proof of Concept
As described in the report: construct an xcm-executor unit/integration test using `TakeFirstAssetTrader` with a small `MaxAssetsIntoHolding`, fill holding to the limit with distinct asset IDs via `WithdrawAsset`, issue `BuyExecution`/`PayFees` with a new fee asset ID and an amount exceeding `minimum_balance`, consume only part of the purchased weight, then call `RefundSurplus`. Assert that the instruction returns `Err(XcmError::HoldingWouldOverflow)`, that holding never receives the refund asset, and that total issuance of the fee asset decreases by more than the amount actually consumed for weight — demonstrating the surplus portion is burned rather than refunded or credited via `OnUnbalanced`/`FeeManager`.

### Citations

**File:** cumulus/primitives/utility/src/lib.rs (L180-183)
```rust
		// Make sure we don't enter twice
		if self.outstanding_credit.is_some() {
			return Err((payment, XcmError::NotWithdrawable));
		}
```

**File:** cumulus/primitives/utility/src/lib.rs (L243-278)
```rust
		let outstanding_credit = self.outstanding_credit.as_mut()?;
		let id = outstanding_credit.asset();
		let fun = Fungible(outstanding_credit.peek());
		let asset = (id.clone(), fun).into();

		// Get the local asset id in which we can refund fees.
		let (fungibles_asset_id, _) = Matcher::matches_fungibles(&asset).ok()?;
		let minimum_balance = Fungibles::minimum_balance(fungibles_asset_id.clone());

		// Calculate how much to refund based on unused weight.
		// This read should have already been cached in buy_weight.
		let refund_credit = FeeCharger::charge_weight_in_fungibles(fungibles_asset_id, weight)
			.ok()
			.map(|refund_balance| {
				// Ensure at least minimum_balance remains for the drop handler.
				// This is necessary for fully collateral-backed assets.
				if outstanding_credit.peek().saturating_sub(refund_balance) >= minimum_balance {
					outstanding_credit.extract(refund_balance)
				} else {
					// Keep at least ED in outstanding credit for the OnUnbalanced drop
					// handler. Refund only the surplus above ED (zero if outstanding < ED).
					let keep = minimum_balance.min(outstanding_credit.peek());
					let refund_amount = outstanding_credit.peek().saturating_sub(keep);
					outstanding_credit.extract(refund_amount)
				}
			})?;
		// Subtract the refunded weight from existing weight.
		self.weight_outstanding = self.weight_outstanding.saturating_sub(weight);

		// Only return refund if non-zero.
		if refund_credit.peek() != Zero::zero() {
			Some(AssetsInHolding::new_from_fungible_credit(asset.id, Box::new(refund_credit)))
		} else {
			None
		}
	}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L541-577)
```rust
	fn refund_surplus(&mut self) -> Result<(), XcmError> {
		let current_surplus = self.total_surplus.saturating_sub(self.total_refunded);
		tracing::trace!(
			target: "xcm::refund_surplus",
			total_surplus = ?self.total_surplus,
			total_refunded = ?self.total_refunded,
			?current_surplus,
			"Refunding surplus",
		);
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

**File:** substrate/frame/support/src/traits/misc.rs (L307-315)
```rust
	fn defensive_proof(self, proof: &'static str) -> Self {
		match self {
			Ok(inner) => Ok(inner),
			Err(e) => {
				defensive!(e, proof);
				Err(e)
			},
		}
	}
```

**File:** polkadot/xcm/xcm-executor/src/assets.rs (L90-97)
```rust
pub struct AssetsInHolding {
	/// The fungible assets.
	pub fungible: BTreeMap<AssetId, Box<dyn ImbalanceAccounting<u128>>>,
	/// The non-fungible assets.
	// TODO: Consider BTreeMap<AssetId, BTreeSet<AssetInstance>>
	//   or even BTreeMap<AssetId, SortedVec<AssetInstance>>
	pub non_fungible: BTreeSet<(AssetId, AssetInstance)>,
}
```
