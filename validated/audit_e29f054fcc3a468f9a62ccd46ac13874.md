[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** substrate/frame/assets-freezer/src/lib.rs (L143-168)
```rust
	fn update_freezes(
		asset: T::AssetId,
		who: &T::AccountId,
		freezes: BoundedSlice<
			IdAmount<T::RuntimeFreezeReason, T::Balance>,
			VariantCountOf<T::RuntimeFreezeReason>,
		>,
	) -> DispatchResult {
		let prev_frozen = FrozenBalances::<T, I>::get(asset.clone(), who).unwrap_or_default();
		let after_frozen = freezes.into_iter().map(|f| f.amount).max().unwrap_or_else(Zero::zero);
		FrozenBalances::<T, I>::set(asset.clone(), who, Some(after_frozen));
		if freezes.is_empty() {
			Freezes::<T, I>::remove(asset.clone(), who);
			FrozenBalances::<T, I>::remove(asset.clone(), who);
		} else {
			Freezes::<T, I>::insert(asset.clone(), who, freezes);
		}
		if prev_frozen > after_frozen {
			let amount = prev_frozen.saturating_sub(after_frozen);
			Self::deposit_event(Event::Thawed { asset_id: asset, who: who.clone(), amount });
		} else if after_frozen > prev_frozen {
			let amount = after_frozen.saturating_sub(prev_frozen);
			Self::deposit_event(Event::Frozen { asset_id: asset, who: who.clone(), amount });
		}
		Ok(())
	}
```

**File:** substrate/frame/assets/src/functions.rs (L99-106)
```rust
	pub(super) fn ensure_account_can_die(id: T::AssetId, who: &T::AccountId) -> DispatchResult {
		ensure!(
			T::Holder::balance_on_hold(id.clone(), who).is_none(),
			Error::<T, I>::ContainsHolds
		);
		ensure!(T::Freezer::frozen_balance(id, who).is_none(), Error::<T, I>::ContainsFreezes);
		Ok(())
	}
```

**File:** substrate/frame/assets/src/functions.rs (L594-621)
```rust
			Account::<T, I>::try_mutate(&id, target, |maybe_account| -> DispatchResult {
				let mut account = maybe_account.take().ok_or(Error::<T, I>::NoAccount)?;
				debug_assert!(account.balance >= actual, "checked in prep; qed");

				// Make the debit.
				account.balance = account.balance.saturating_sub(actual);
				if account.balance < details.min_balance {
					debug_assert!(account.balance.is_zero(), "checked in prep; qed");
					Self::ensure_account_can_die(id.clone(), target)?;
					target_died = Some(Self::dead_account(target, details, &account.reason, false));
					if let Some(Remove) = target_died {
						return Ok(());
					}
				};
				*maybe_account = Some(account);
				Ok(())
			})?;

			Ok(())
		})?;

		// Execute hook outside of `mutate`.
		if let Some(Remove) = target_died {
			T::Freezer::died(id.clone(), target);
			T::Holder::died(id, target);
		}
		Ok(actual)
	}
```

**File:** substrate/frame/assets/src/tests.rs (L1448-1459)
```rust
fn calling_dead_account_fails_if_freezes_or_balances_on_hold_exist_1() {
	build_and_execute(|| {
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), 0, 1, true, 50));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 1, 100));

		set_frozen_balance(0, 1, 50);
		// Cannot transfer out less than max(freezes, ed). This happens in
		// `prep_debit` under `transfer_and_die`. Would not reach `dead_account`.
		assert_noop!(
			Assets::transfer(RuntimeOrigin::signed(1), 0, 2, 100),
			Error::<Test>::BalanceLow
		);
```
