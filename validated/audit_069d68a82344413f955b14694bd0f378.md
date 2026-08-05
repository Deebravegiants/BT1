Audit Report

## Title
`refund_surplus`'s holding-overflow "buy-back" fallback always fails and permanently burns the attacker's already-collected fee instead of refunding or crediting it - (File: `polkadot/xcm/xcm-executor/src/lib.rs`)

## Summary
When `RefundSurplus` cannot merge a refund into `holding` because `ensure_can_subsume_assets` fails, `XcmExecutor::refund_surplus` attempts to "undo" the refund by calling `self.trader.buy_weight(...)` again on the trader. For `cumulus_primitives_utility::TakeFirstAssetTrader`, this call is guaranteed to fail because `buy_weight`'s re-entrancy guard (`outstanding_credit.is_some()`) remains `true` after the earlier `refund_weight` call, which only mutates the existing credit via `extract` and never resets `outstanding_credit` to `None`. The failed result is discarded with `let _ = ...defensive_proof(...)`, dropping the `AssetsInHolding`/`fungibles::Credit` and triggering its issuance-decreasing drop handler — burning the fee rather than refunding or crediting it.

## Finding Description
The code exactly matches the report's citations:

- `TakeFirstAssetTrader::buy_weight` returns `Err((payment, XcmError::NotWithdrawable))` whenever `self.outstanding_credit.is_some()`: [1](#0-0) 
- `TakeFirstAssetTrader::refund_weight` only calls `outstanding_credit.extract(...)` inside the existing `Some(credit)`, and never sets `self.outstanding_credit = None`: [2](#0-1) 
- `XcmExecutor::refund_surplus` detects a holding-capacity problem via `ensure_can_subsume_assets`, and on failure calls `self.trader.buy_weight(current_surplus, refund, &self.context)` again, discarding the `Err` result (which contains the `refund` `AssetsInHolding`) with `let _ = ... .defensive_proof(...)`: [3](#0-2) 
- `Defensive::defensive_proof` for `Result` only logs via `defensive!` and returns the original `Err` unchanged — it performs no recovery: [4](#0-3) 

Because `outstanding_credit` is never cleared by `refund_weight`, the "buy back" `buy_weight` call inside the overflow branch will *always* hit the re-entrancy guard and return `Err`, discarding the `refund` `AssetsInHolding` value that wraps the previously-withdrawn `fungibles::Credit`. This confirms the code path: `ensure_can_subsume_assets` is a pure capacity check on `holding` and has no knowledge of the trader's internal re-entrancy invariant, so it provides no protection against this failure mode. Dropping an `AssetsInHolding` built from a fungible credit ultimately drops the underlying `Imbalance`/`Credit`, whose `OnDropCredit` handler (e.g. `fungibles::DecreaseIssuance`, as used throughout the codebase including `pallet_assets`'s `DecreaseIssuanceWithEvent`) decreases total issuance on drop rather than returning value to the user: [5](#0-4) [6](#0-5) 

## Impact Explanation
This is a genuine value-destruction bug: an amount of fee funds already withdrawn from a user (via `buy_weight` during `BuyExecution`/`PayFees`) that should be refunded to `holding` (and ultimately to the user) is instead permanently burned through the issuance-decrease drop path, with no compensating benefit to the user, chain fee-revenue account, or `OnUnbalanced`/`FeeManager` handler. The triggering instruction also returns `Err(XcmError::HoldingWouldOverflow)`, aborting the remainder of the program. This matches an in-scope "user funds destroyed/not fully backed" impact class for the XCM executor and `TakeFirstAssetTrader` configuration used by Cumulus-based chains.

## Likelihood Explanation
The trigger path is reachable by an unprivileged signed account via `pallet_xcm::execute` or an XCMP-delivered program processed by the same executor, requiring no privileged origin. It requires the attacker to (a) fill `holding` to a point where a new asset ID cannot be subsumed (feasible via many low-value `WithdrawAsset`/teleport operations on distinct asset IDs, which is realistic on chains like Asset Hub that allow permissionless creation of many `pallet-assets` IDs), and (b) use a fee asset for `BuyExecution`/`PayFees` not already present in holding, with `total_surplus > total_refunded` at `RefundSurplus` time. This is a deterministic, code-verified bug in the fallback path (not a probabilistic race) and is fully reproducible by any user configuring their own XCM program with moderate crafting effort; it also occurs unintentionally, since it is triggered by ordinary holding-overflow bookkeeping.

## Recommendation
Fix the "buy back" recovery path in `XcmExecutor::refund_surplus` so it does not rely on `WeightTrader::buy_weight`'s re-entrancy guard:
- Introduce a dedicated `WeightTrader` method (e.g. `restore_refund`/`un_refund`) that re-merges a previously extracted refund back into `outstanding_credit` without triggering the "already bought" check, or
- Make `TakeFirstAssetTrader::refund_weight`'s extraction reversible/transactional until the caller confirms successful placement into holding, or
- When the buy-back fails in `refund_surplus`, explicitly route the `refund` assets to `Config::FeeManager::handle_fee` (or an equivalent trap/claim mechanism) instead of silently dropping them, ensuring funds are treated as legitimate fee revenue rather than burned via the imbalance drop handler.

## Proof of Concept
An xcm-executor test using `TakeFirstAssetTrader` as the configured `Trader`:
1. Configure a small `MaxAssetsIntoHolding` (e.g. 2).
2. `WithdrawAsset` for `holding_limit` distinct asset IDs to fill `holding` to capacity.
3. `BuyExecution`/`PayFees` using a distinct asset C (not already in holding), amount = `minimum_balance(C) + X`, with weight limit `W`, causing `TakeFirstAssetTrader::buy_weight` to set `outstanding_credit`.
4. Execute an instruction consuming less than `W`, producing `total_surplus > 0`.
5. Trigger `RefundSurplus`; assert:
   - The instruction returns `Err(XcmError::HoldingWouldOverflow)`.
   - `holding` never receives asset C back.
   - Asset C's total issuance decreases by more than the amount actually consumed for weight (i.e., the surplus portion is additionally burned), confirming the refund credit was dropped instead of returned to the user or an `OnUnbalanced`/`FeeManager` handler.

### Citations

**File:** cumulus/primitives/utility/src/lib.rs (L180-183)
```rust
		// Make sure we don't enter twice
		if self.outstanding_credit.is_some() {
			return Err((payment, XcmError::NotWithdrawable));
		}
```

**File:** cumulus/primitives/utility/src/lib.rs (L243-268)
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
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L562-577)
```rust
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

**File:** substrate/frame/support/src/traits/tokens/fungibles/regular.rs (L427-436)
```rust
/// Simple handler for an imbalance drop which decreases the total issuance of the system by the
/// imbalance amount. Used for leftover credit.
pub struct DecreaseIssuance<AccountId, U>(PhantomData<(AccountId, U)>);
impl<AccountId, U: Unbalanced<AccountId>> HandleImbalanceDrop<U::AssetId, U::Balance>
	for DecreaseIssuance<AccountId, U>
{
	fn handle(asset: U::AssetId, amount: U::Balance) {
		U::set_total_issuance(asset.clone(), U::total_issuance(asset).saturating_sub(amount))
	}
}
```

**File:** substrate/frame/assets/src/impl_fungibles.rs (L131-142)
```rust
/// Simple handler for an imbalance drop which decreases the total issuance of the system by the
/// imbalance amount. Used for leftover credit. Emits event.
pub struct DecreaseIssuanceWithEvent<T, I>(PhantomData<(T, I)>);
impl<T: Config<I>, I: 'static>
	fungibles::HandleImbalanceDrop<<T as Config<I>>::AssetId, <T as Config<I>>::Balance>
	for DecreaseIssuanceWithEvent<T, I>
{
	fn handle(asset_id: <T as Config<I>>::AssetId, amount: <T as Config<I>>::Balance) {
		fungibles::DecreaseIssuance::<T::AccountId, Pallet<T, I>>::handle(asset_id.clone(), amount);
		Pallet::<T, I>::deposit_event(Event::BurnedCredit { asset_id, amount });
	}
}
```
