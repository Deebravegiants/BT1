### Title
PGAS fee refund failure burns the entire reserved fee instead of `actual_fee` when the payer's account is dusted below the asset ED - (File: `substrate/frame/transaction-payment/pgas-allowance/src/lib.rs`)

### Summary
In `ChargePGAS::post_dispatch_details` (`Pre::PGAS` branch), when the refund owed back to the payer cannot be deposited via `fungibles::Balanced::resolve`, the pallet burns the *entire* `reserved` credit rather than just `actual_fee`. Because PGAS withdrawal at `prepare` uses `Preservation::Expendable`, a payer can legitimately (and deterministically) drain their own PGAS account to zero, after which any nonzero refund below the asset's existential deposit will fail to deposit, triggering the full-reserved burn.

### Finding Description
At `prepare` (`substrate/frame/transaction-payment/pgas-allowance/src/lib.rs:300-308`), the full `fee` is withdrawn from the payer with `Preservation::Expendable`, which — as the pallet's own test `pgas_below_ed_dusts_account` (`substrate/frame/transaction-payment/pgas-allowance/src/tests.rs:177-213`) confirms — is allowed to dust the account to exactly `0`.

At `post_dispatch_details` (`substrate/frame/transaction-payment/pgas-allowance/src/lib.rs:344-374`), the reserved credit is split into `consumed` (`actual_fee`) and `fee_refund` (the unused portion). If `fee_refund` is nonzero, the code calls `<T::Assets as fungibles::Balanced<T::AccountId>>::resolve(&who, fee_refund)` (line 364). The default `resolve` implementation (`substrate/frame/support/src/traits/tokens/fungibles/regular.rs:563-579`) calls `deposit(... Precision::Exact)`, which goes through `increase_balance` (`regular.rs:217-246`): if `new_balance < minimum_balance` (i.e., the deposited amount is below the asset's ED) **and** `Precision::Exact` is used, it returns `Err(TokenError::BelowMinimum)` rather than succeeding.

Since the payer's PGAS balance is `0` after `prepare` dusted it, any `fee_refund` smaller than the asset's `minimum_balance` will deterministically fail this check. On that `Err`, the pallet's `match` (lines 364-373) burns `reserved` (the full originally-withdrawn fee) instead of `actual_fee`, silently absorbing the honest refund difference (`reserved - actual_fee`) as an extra burn, and reports it via `Event::PGASFeePaid { who, actual_fee: burned }` with `burned == reserved`.

No check in `validate`, `prepare`, or `post_dispatch_details` prevents the payer from choosing an exact PGAS balance that dusts to zero, nor does anything require `fee_refund >= minimum_balance` before attempting `resolve`.

### Impact Explanation
A user (or an attacker targeting their own account, since the affected account is the same signer who submitted the transaction) loses `reserved - actual_fee` PGAS beyond the fee actually owed for the resources consumed — this is a direct, reproducible accounting inconsistency violating the invariant that failed refunds must not cause the user to lose more than `actual_fee`. Because the burn path is silent (only a `log::debug!`) and the emitted `PGASFeePaid` event reports the inflated `burned` amount as if it were the "actual fee," downstream tooling relying on this event for fee accounting will also be misled.

### Likelihood Explanation
Fully reachable by an unprivileged signed user through the normal extrinsic path (no special origin/proxy/multisig needed):
1. Fund the PGAS account with exactly the anticipated `fee` (`reserved`), leaving zero PGAS margin.
2. Submit a filter-matching call whose declared weight (`info`) overestimates the actual weight consumed, such that `fee_refund = reserved - actual_fee` is nonzero but smaller than the PGAS asset's `minimum_balance`.
3. `prepare` withdraws the full `fee`, dusting the account to `0` (as shown by the existing `pgas_below_ed_dusts_account` test).
4. `post_dispatch_details` attempts `resolve(&who, fee_refund)`, which fails via `TokenError::BelowMinimum` because depositing an amount below ED into a zero-balance account under `Precision::Exact` is rejected.
5. The full `reserved` is burned instead of `actual_fee`.

This is deterministic and repeatable — it is not a race condition or timing-dependent exploit, just a controllable balance/weight-refund combination.

### Recommendation
Before attempting `resolve`, check whether `fee_refund.peek() < T::Assets::minimum_balance(PGASAssetId)` and the account's post-withdrawal balance is `0`; in that case, treat the dust as legitimately non-refundable (fold it into `OnDropCredit`/burn accounting explicitly) but only burn `fee_refund`, not the already-consumed `consumed` amount twice, and ensure the emitted event still reflects `actual_fee` separately from any extra unrecoverable dust, e.g., emit a distinct event/field for "dust absorbed" versus "actual fee charged," or use `Preservation::Preserve`/`BestEffort` semantics consistent with not exceeding `actual_fee + minimum_balance` loss.

### Proof of Concept
Extend `pgas_refund_on_unused_weight` in `substrate/frame/transaction-payment/pgas-allowance/src/tests.rs`:
1. Set `pgas_initial` exactly equal to the computed `reserved` fee (so `prepare` dusts Alice's PGAS balance to `0`, as in `pgas_below_ed_dusts_account`).
2. Choose `claimed`/`actual` weights so `fee_refund = reserved - actual_fee` is nonzero but `< Assets::minimum_balance(PGAS_ASSET_ID)`.
3. Call `post_dispatch_details` and assert:
   - `Assets::balance(PGAS_ASSET_ID, ALICE) == 0` (refund did not land),
   - the emitted `Event::PGASFeePaid { who: ALICE, actual_fee }` has `actual_fee == reserved` (not the true `actual_fee` computed from weight), demonstrating the extra burn of `reserved - actual_fee` beyond what was actually owed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** substrate/frame/transaction-payment/pgas-allowance/src/lib.rs (L285-315)
```rust
	fn prepare(
		self,
		val: Self::Val,
		origin: &OriginFor<T>,
		call: &T::RuntimeCall,
		info: &DispatchInfoOf<T::RuntimeCall>,
		len: usize,
	) -> Result<Self::Pre, TransactionValidityError> {
		let inner_weight = self.inner.weight(call);
		let charge_pgas = <T as Config>::WeightInfo::charge_pgas();
		let charge_pgas_skip = <T as Config>::WeightInfo::charge_pgas_skip();
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

**File:** substrate/frame/transaction-payment/pgas-allowance/src/lib.rs (L337-376)
```rust
	fn post_dispatch_details(
		pre: Self::Pre,
		info: &DispatchInfoOf<T::RuntimeCall>,
		post_info: &PostDispatchInfoOf<T::RuntimeCall>,
		len: usize,
		result: &DispatchResult,
	) -> Result<Weight, TransactionValidityError> {
		match pre {
			Pre::PGAS { who, credit, weight_refund } => {
				let mut actual_post_info = *post_info;
				actual_post_info.refund(weight_refund);
				let actual_fee = pallet_transaction_payment::Pallet::<T>::compute_actual_fee(
					len as u32,
					info,
					&actual_post_info,
					Zero::zero(),
				);

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

**File:** substrate/frame/support/src/traits/tokens/fungibles/regular.rs (L563-579)
```rust
	fn resolve(
		who: &AccountId,
		credit: Credit<AccountId, Self>,
	) -> Result<(), Credit<AccountId, Self>> {
		let v = credit.peek();
		let debt = match Self::deposit(credit.asset(), who, v, Exact) {
			Err(_) => return Err(credit),
			Ok(d) => d,
		};
		if let Ok(result) = credit.offset(debt) {
			let result = result.try_drop();
			debug_assert!(result.is_ok(), "ok deposit return must be equal to credit value; qed");
		} else {
			debug_assert!(false, "debt.asset is credit.asset; qed");
		}
		Ok(())
	}
```

**File:** substrate/frame/transaction-payment/pgas-allowance/src/tests.rs (L136-172)
```rust
fn pgas_refund_on_unused_weight() {
	let pgas_initial = 1_000;
	ExtBuilder::default()
		.with_pgas(vec![(ALICE, pgas_initial)])
		.build()
		.execute_with(|| {
			let call = pgas_call();
			let len = 10;
			let claimed = Weight::from_parts(100, 0);
			let actual = Weight::from_parts(40, 0);
			let info = info_from_weight(claimed);

			let reserved =
				pallet_transaction_payment::Pallet::<Runtime>::compute_fee(len as u32, &info, 0);
			let actual_fee = pallet_transaction_payment::Pallet::<Runtime>::compute_actual_fee(
				len as u32,
				&info,
				&post_info_from_weight(actual),
				0,
			);
			assert!(reserved > actual_fee);

			let (pre, _) = new_ext()
				.validate_and_prepare(Some(ALICE).into(), &call, &info, len, 0)
				.unwrap();
			assert_eq!(Assets::balance(PGAS_ASSET_ID, ALICE), pgas_initial - reserved);

			assert_ok!(<Ext as sp_runtime::traits::TransactionExtension<RuntimeCall>>::post_dispatch_details(
				pre,
				&info,
				&post_info_from_weight(actual),
				len,
				&Ok(()),
			));
			assert_eq!(Assets::balance(PGAS_ASSET_ID, ALICE), pgas_initial - actual_fee);
		});
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
