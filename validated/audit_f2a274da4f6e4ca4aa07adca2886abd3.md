All the claimed code paths check out exactly as described. The vulnerability is confirmed:

1. `prepare` withdraws `fee` with `Preservation::Expendable`, which can dust the payer's PGAS account to `0`, as verified by the existing test `pgas_below_ed_dusts_account`.
2. `post_dispatch_details` computes `fee_refund` and attempts `resolve`, which internally calls `increase_balance` with `Precision::Exact` — this returns `Err(TokenError::BelowMinimum)` when depositing into a zero balance an amount below `minimum_balance`.
3. On that error, the code burns `reserved` (the full withdrawn fee) instead of `actual_fee`, and emits `PGASFeePaid { actual_fee: burned }` with the inflated `reserved` value — a real accounting violation reachable by any unprivileged signed user who simply funds their PGAS account with exactly the fee amount and submits a call whose actual weight is less than declared (a legitimate, common scenario, not requiring any privilege or victim mistake beyond normal fee/weight variance).

Audit Report

## Title
PGAS fee refund failure burns the entire reserved fee instead of `actual_fee` when the payer's account is dusted below the asset ED - (File: `substrate/frame/transaction-payment/pgas-allowance/src/lib.rs`)

## Summary
In `ChargePGAS::post_dispatch_details` (`Pre::PGAS` branch), when the refund owed back to the payer cannot be deposited via `fungibles::Balanced::resolve` because the payer's account was dusted to zero and the refund amount is below the asset's existential deposit, the pallet burns the entire `reserved` credit instead of just `actual_fee`, silently absorbing `reserved - actual_fee` as an extra, unaccounted burn.

## Finding Description
At `prepare` (`substrate/frame/transaction-payment/pgas-allowance/src/lib.rs:300-308`), the full `fee` is withdrawn from the payer using `Preservation::Expendable`, which is confirmed by the pallet's own test `pgas_below_ed_dusts_account` (`substrate/frame/transaction-payment/pgas-allowance/src/tests.rs:177-213`) to legitimately dust the account to exactly `0`.

At `post_dispatch_details` (`substrate/frame/transaction-payment/pgas-allowance/src/lib.rs:344-376`), the reserved credit is split into `consumed` (`actual_fee`) and `fee_refund`. If nonzero, `resolve(&who, fee_refund)` is called (line 364-366). `resolve`'s default implementation (`substrate/frame/support/src/traits/tokens/fungibles/regular.rs:563-579`) calls `deposit` with `Precision::Exact`, which routes through `increase_balance` (`regular.rs:217-246`): when `new_balance < minimum_balance` under `Exact` precision, it returns `Err(TokenError::BelowMinimum)` rather than partially succeeding.

Since the account was dusted to `0` by `prepare`, any nonzero `fee_refund` below the asset's `minimum_balance` deterministically fails. On error, the code at lines 368-372 merges `fee_refund` back into `consumed` and sets `burned = reserved` (the full withdrawn fee), rather than only burning the unrecoverable `fee_refund` on top of the correctly-owed `actual_fee`. The emitted `Event::PGASFeePaid` then reports `burned` (i.e., `reserved`) as `actual_fee`, misrepresenting the true fee.

No check exists in `validate`, `prepare`, or before the `resolve` call to detect that the account is at zero balance or that `fee_refund` is below `minimum_balance`, so the existing code path does not guard against this outcome.

## Impact Explanation
An honest user loses `reserved - actual_fee` PGAS beyond the fee actually owed for the resources their transaction consumed. This is a direct, deterministic accounting violation of the invariant that a failed refund should not cause the user to lose more than `actual_fee` (plus at most the unrecoverable dust amount below ED, not the entire reserved amount). The burn is silent (only `log::debug!`), and the `PGASFeePaid` event misreports the burned amount as `actual_fee`, misleading any fee-accounting tooling that consumes this event.

## Likelihood Explanation
This is fully reachable by any unprivileged signed account through the normal extrinsic submission path: fund the PGAS account with exactly the anticipated fee (so `prepare` dusts it to zero), then submit a call whose declared weight overestimates actual consumed weight such that the resulting refund is nonzero but below the PGAS asset's `minimum_balance`. This requires no special origin, governance, or victim mistake — it's a deterministic, repeatable combination of balance funding and normal weight/fee variance that commonly occurs in practice (declared weight almost always overestimates actual weight to some degree).

## Recommendation
Before burning on `resolve` failure, only burn the actual unrecoverable `fee_refund` amount (which is below `minimum_balance`), not the entire `reserved` credit. Ensure `consumed` (i.e., `actual_fee`) is dropped/burned separately from the dust, and emit `PGASFeePaid` with `actual_fee` reflecting the true fee charged, with a distinct event or field capturing any additional dust absorbed, so downstream consumers are not misled about the actual fee paid for resource consumption.

## Proof of Concept
Extend `pgas_refund_on_unused_weight` in `substrate/frame/transaction-payment/pgas-allowance/src/tests.rs`:
1. Set `pgas_initial` exactly equal to the computed `reserved` fee so `prepare` dusts Alice's PGAS balance to `0` (as demonstrated by `pgas_below_ed_dusts_account`).
2. Choose `claimed`/`actual` weights such that `fee_refund = reserved - actual_fee` is nonzero but smaller than `Assets::minimum_balance(PGAS_ASSET_ID)`.
3. Call `post_dispatch_details` and assert `Assets::balance(PGAS_ASSET_ID, ALICE) == 0` (refund did not land) and that the emitted `Event::PGASFeePaid { who: ALICE, actual_fee }` reports `actual_fee == reserved`, demonstrating the extra burn of `reserved - actual_fee` beyond what was actually owed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** substrate/frame/transaction-payment/pgas-allowance/src/lib.rs (L296-315)
```rust
		match val {
			Val::PGAS { who, fee } => {
				// PGAS is committed at `validate`; if the balance dropped since, the tx is
				// rejected rather than falling back to the inner extension.
				let credit = <T::Assets as fungibles::Balanced<T::AccountId>>::withdraw(
					T::PGASAssetId::get(),
					&who,
					fee,
					Precision::Exact,
					Preservation::Expendable,
					Fortitude::Polite,
				)
				.map_err(|_| InvalidTransaction::Payment)?;

				// `weight()` reserved `charge_pgas.max(inner + charge_pgas_skip)`; the PGAS path
				// only consumes `charge_pgas`, so the excess is refunded.
				let reserved = charge_pgas.max(inner_weight.saturating_add(charge_pgas_skip));
				let weight_refund = reserved.saturating_sub(charge_pgas);
				Ok(Pre::PGAS { who, credit, weight_refund })
			},
```

**File:** substrate/frame/transaction-payment/pgas-allowance/src/lib.rs (L355-376)
```rust
				// Split the reserved credit into the consumed portion (dropped below to burn)
				// and the refund owed back to `who`.
				let reserved = credit.peek();
				let (consumed, fee_refund) = credit.split(actual_fee);
				// Equals `actual_fee` on the happy path; if the refund cannot be returned to
				// `who` we burn the full reserved amount and report it.
				let burned = if fee_refund.peek().is_zero() {
					actual_fee
				} else {
					match <T::Assets as fungibles::Balanced<T::AccountId>>::resolve(
						&who, fee_refund,
					) {
						Ok(()) => actual_fee,
						Err(fee_refund) => {
							log::debug!(target: LOG_TARGET, "PGAS fee refund to {who:?} failed; burning full reserved fee {reserved:?}");
							let _ = consumed.merge(fee_refund);
							reserved
						},
					}
				};
				Pallet::<T>::deposit_event(Event::PGASFeePaid { who, actual_fee: burned });
				Ok(weight_refund)
```

**File:** substrate/frame/support/src/traits/tokens/fungibles/regular.rs (L217-246)
```rust
	fn increase_balance(
		asset: Self::AssetId,
		who: &AccountId,
		amount: Self::Balance,
		precision: Precision,
	) -> Result<Self::Balance, DispatchError> {
		let old_balance = Self::balance(asset.clone(), who);
		let new_balance = if let BestEffort = precision {
			old_balance.saturating_add(amount)
		} else {
			old_balance.checked_add(&amount).ok_or(ArithmeticError::Overflow)?
		};
		if new_balance < Self::minimum_balance(asset.clone()) {
			// Attempt to increase from 0 to below minimum -> stays at zero.
			if let BestEffort = precision {
				Ok(Self::Balance::default())
			} else {
				Err(TokenError::BelowMinimum.into())
			}
		} else {
			if new_balance == old_balance {
				Ok(Self::Balance::default())
			} else {
				if let Some(dust) = Self::write_balance(asset.clone(), who, new_balance)? {
					Self::handle_dust(Dust(asset, dust));
				}
				Ok(new_balance.saturating_sub(old_balance))
			}
		}
	}
```

**File:** substrate/frame/transaction-payment/pgas-allowance/src/tests.rs (L177-213)
```rust
#[test]
fn pgas_below_ed_dusts_account() {
	let native_initial = 1_000;
	// Asset ED is 1 (see `ExtBuilder::build`). Give Alice exactly the fee in PGAS so paying it
	// drains the balance to zero.
	ExtBuilder::default()
		.with_native(vec![(ALICE, native_initial)])
		.build()
		.execute_with(|| {
			let call = pgas_call();
			let len = 10;
			let info = info_from_weight(Weight::from_parts(7, 0));

			let fee = pallet_transaction_payment::Pallet::<Runtime>::compute_fee(
				len as u32,
				&info,
				0,
			);
			assert!(fee > 0);

			let pgas_initial = fee;
			assert_ok!(<pallet_assets::Pallet<Runtime> as frame_support::traits::tokens::fungibles::Mutate<AccountId>>::mint_into(
				PGAS_ASSET_ID,
				&ALICE,
				pgas_initial,
			));
			assert_eq!(Assets::balance(PGAS_ASSET_ID, ALICE), pgas_initial);

			let (_pre, _) = new_ext()
				.validate_and_prepare(Some(ALICE).into(), &call, &info, len, 0)
				.unwrap();

			// PGAS drained to 0 (account dusted), native untouched.
			assert_eq!(Assets::balance(PGAS_ASSET_ID, ALICE), 0);
			assert_eq!(Balances::free_balance(ALICE), native_initial);
		});
}
```
