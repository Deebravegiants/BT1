### No vulnerability found for this question.

**Analysis:** The sequence WithdrawAsset(fees) -> BuyExecution(fees) -> PayFees(fees) -> DepositAsset does not enable double-spending of the same asset units, because both `BuyExecution` and `PayFees` draw from the *same finite* `holding` register via `AssetsInHolding::try_take`, which physically removes the taken amount from that register rather than duplicating it.

In `BuyExecution`, the executor calls `self_ref.holding.try_take(fees.clone().into())`, consuming that amount from `holding`, then returns unspent change back to `holding` via `subsume_assets`. [1](#0-0) 

`PayFees` subsequently calls `self_ref.holding.try_take(asset.into())` on the same `holding` register — if `BuyExecution` already consumed the relevant balance, only the leftover (unspent change from `BuyExecution`, if any) remains available for `PayFees` to take. `PayFees` cannot take more than currently exists in `holding`; `try_take` fails with `XcmError::NotHoldingFees` if the balance is insufficient. [2](#0-1) 

The `already_paid_fees` flag only prevents a *second* `PayFees` instruction in the same program from re-executing (it's a no-op guard for idempotency of `PayFees` itself, not a cross-instruction accounting gate with `BuyExecution`), and it is correctly reset on rollback via `transactional_process_with_custom_rollback`. [3](#0-2) 

The `asset_used_in_buy_execution` field is only used later for delivery-fee asset selection in `calculate_asset_for_delivery_fees`/`take_fee`, not as a bypass for holding-register accounting — it does not grant any additional balance or duplicate assets. [4](#0-3) 

Because `holding` is a single bounded register whose total can never exceed what was actually withdrawn via `WithdrawAsset`, sequential `try_take` calls (whether from `BuyExecution` then `PayFees`, or vice versa) can only ever consume up to that bounded total — there is no accounting path that allows the same withdrawn units to be counted twice. The independent `trader.buy_weight` calls in each instruction affect weight/fee-market accounting per instruction (each instruction buys weight for its own declared purpose), but this does not translate into duplicated *asset* debits from `holding`, since the assets passed to `buy_weight` were already physically removed from `holding` by `try_take` beforehand. This matches the documented design in the PRDoc where `PayFees` is meant to coexist with (and eventually replace) `BuyExecution`, with unspent assets from `PayFees` moved to the separate `fees` register (recoverable only via `RefundSurplus`), which is intentional and does not constitute a double-spend of origin-debited assets. [5](#0-4) 

Existing regression tests (`already_paid_fees_rolls_back_on_error`, `custom_rollback_is_invoked_on_error`) already validate that `already_paid_fees` and holding/fees register invariants behave correctly under error and rollback conditions, confirming the register bookkeeping is sound for this mixed sequencing. [6](#0-5) [7](#0-6)

### Citations

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L677-716)
```rust
	/// Calculates the amount of asset used in `PayFees` or `BuyExecution` that would be
	/// charged for swapping to `asset_needed_for_fees`.
	///
	/// The calculation is done by `Config::AssetExchanger`.
	/// If neither `PayFees` or `BuyExecution` were used, or no swap is required,
	/// it will just return `asset_needed_for_fees`.
	fn calculate_asset_for_delivery_fees(&self, asset_needed_for_fees: Asset) -> Asset {
		let Some(asset_wanted_for_fees) =
			// we try to swap first asset in the fees register (should only ever be one),
			self.fees.fungible.first_key_value().map(|(id, _)| id).or_else(|| {
				// or the one used in BuyExecution
				self.asset_used_in_buy_execution.as_ref()
			})
			// if it is different than what we need
			.filter(|&id| asset_needed_for_fees.id.ne(id))
		else {
			// either nothing to swap or we're already holding the right asset
			return asset_needed_for_fees
		};
		Config::AssetExchanger::quote_exchange_price(
			&(asset_wanted_for_fees.clone(), Fungible(0)).into(),
			&asset_needed_for_fees.clone().into(),
			false, // Minimal.
		)
		.and_then(|necessary_assets| {
			// We only use the first asset for fees.
			// If this is not enough to swap for the fee asset then it will error later down
			// the line.
			necessary_assets.into_inner().into_iter().next()
		})
		.unwrap_or_else(|| {
			// If we can't convert, then we return the original asset.
			// It will error later in any case.
			tracing::trace!(
				target: "xcm::calculate_asset_for_delivery_fees",
				?asset_wanted_for_fees, "Could not convert fees",
			);
			asset_needed_for_fees
		})
	}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1457-1471)
```rust
				self.transactional_process(|self_ref| {
					// pay for `weight` using up to `fees` of the holding register.
					let max_fee =
						self_ref.holding.try_take(fees.clone().into()).map_err(|e| {
							tracing::error!(target: "xcm::process_instruction::buy_execution", ?e, ?fees,
							"Failed to take fees from holding");
							XcmError::NotHoldingFees
						})?;
					let unspent = self_ref.trader.buy_weight(weight, max_fee, &self_ref.context).map_err(|(unspent, e)| {
						self_ref.holding.subsume_assets(unspent);
						e
					})?;
					self_ref.holding.subsume_assets(unspent);
					Ok(())
				})
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1473-1510)
```rust
			PayFees { asset } => {
				// If we've already paid for fees, do nothing.
				if self.already_paid_fees {
					return Ok(());
				}
				// Make sure `PayFees` won't be processed again.
				self.already_paid_fees = true;
				// The max we're willing to pay for fees is decided by the `asset` operand.
				tracing::trace!(
					target: "xcm::executor::PayFees",
					asset_for_fees = ?asset,
					message_weight = ?self.message_weight,
				);
				// Pay for execution fees.
				self.transactional_process_with_custom_rollback(
					|self_ref| {
						let max_fee =
							self_ref.holding.try_take(asset.into()).map_err(|error| {
								tracing::debug!(
									target: "xcm::process_instruction::pay_fees", ?error,
									"Failed to take fees from holding"
								);
								XcmError::NotHoldingFees
							})?;
						let unspent =
							self_ref.trader.buy_weight(self_ref.message_weight, max_fee.into(), &self_ref.context).map_err(|(unspent, e)| {
								self_ref.fees.subsume_assets(unspent);
								e
							})?;
						// Move unspent to the `fees` register, it can later be moved to holding by calling `RefundSurplus`.
						self_ref.fees.subsume_assets(unspent);
						Ok(())
					},
					|self_ref| {
						self_ref.already_paid_fees = false;
					},
				)
			},
```

**File:** prdoc/stable2412/pr_5420.prdoc (L10-24)
```text
    description: |
      In XCMv5, there's a new instruction, `PayFees`, which is meant to be a replacement for `BuyExecution`.
      This instruction takes only one parameter, the `asset` that you are willing to use for fee payment.
      There's no parameter for limiting the weight, the amount of the `asset` you put in is the limit of
      how much you're willing to pay.
      This instruction works much better with delivery fees.
      `BuyExecution` will still be around to ensure backwards-compatibility, however, the benefits of the new
      instruction are a good incentive to switch.
      The proposed workflow is to estimate fees using the `XcmPaymentApi` and `DryRunApi`, then to put those
      values in `PayFees` and watch your message go knowing you covered all the necessary fees.
      You can add a little bit more just in case if you want.
      `RefundSurplus` now gets back all of the assets that were destined for fee payment so you can deposit
      them somewhere.
      BEWARE, make sure you're not sending any other message after you call `RefundSurplus`, if not, it will
      error.
```

**File:** polkadot/xcm/xcm-executor/src/tests/pay_fees.rs (L323-346)
```rust
#[test]
fn already_paid_fees_rolls_back_on_error() {
	// Make sure the sender has enough funds to withdraw.
	add_asset(SENDER, (Here, 100u128));

	let xcm = Xcm::<TestCall>::builder()
		.withdraw_asset((Here, 100u128))
		.pay_fees((Here, 200u128))
		.deposit_asset(All, RECIPIENT)
		.build();

	let (mut vm, _) = instantiate_executor(SENDER, xcm.clone());

	// Program fails.
	assert!(vm.bench_process(xcm).is_err());

	// Everything left in the `holding` register.
	assert_eq!(get_first_fungible(vm.holding()).unwrap(), (Here, 100u128).into());
	// Nothing in the `fees` register.
	assert_eq!(get_first_fungible(vm.fees()), None);

	// Already paid fees is false.
	assert_eq!(vm.already_paid_fees(), false);
}
```

**File:** polkadot/xcm/xcm-executor/src/tests/transactional.rs (L86-109)
```rust
fn custom_rollback_is_invoked_on_error() {
	add_asset(SENDER, (Here, 100u128));

	// First program: withdraw, then PayFees with an asset NOT in holding → fails.
	let xcm1 = Xcm::<TestCall>(vec![
		WithdrawAsset((Here, 100u128).into()),
		PayFees { asset: (Parent, 10u128).into() },
	]);

	let (mut vm, _weight) = instantiate_executor(SENDER, xcm1.clone());
	// PayFees fails because (Parent, 10) is not in holding.
	assert!(vm.bench_process(xcm1).is_err());

	// The custom rollback should have reset `already_paid_fees` to false.
	// Verify by running a second program: if the flag was properly rolled back,
	// PayFees will buy weight and populate the `fees` register.
	let xcm2 = Xcm::<TestCall>(vec![PayFees { asset: (Here, 10u128).into() }]);

	assert!(vm.bench_process(xcm2).is_ok());

	// If `already_paid_fees` was stuck as `true`, PayFees would have been a no-op and
	// the fees register would be empty. The custom rollback ensures it was reset.
	assert!(get_first_fungible(vm.fees()).is_some());
}
```
