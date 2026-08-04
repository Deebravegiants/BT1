Based on my investigation, I could not find a valid analog of this vulnerability class in the polkadot-sdk codebase.

The Rubicon bug's root cause is a **check-then-act** pattern where a security invariant (reserve ratio) is validated once before an action, but the action itself is allowed to consume unbounded funds, with no corresponding post-condition check — allowing the strategist to blow past the invariant in a single call.

I looked for structurally similar patterns in FRAME pallets that manage pooled liquidity or spending limits with a "reserve" style invariant:

- `pallet-asset-conversion`'s `do_remove_liquidity` computes the exact withdrawal amounts first, then explicitly validates the **resulting** reserves (`reserve1_left`/`reserve2_left`) against `T::Assets::minimum_balance` *before* performing the transfer/burn — i.e., it checks the post-condition prior to committing state, which is exactly the fix pattern recommended in the Rubicon report, not the vulnerable pattern. [1](#0-0) 

- Swaps in the same pallet transfer using `Preserve`/`Expendable` preservation semantics enforced by `pallet-assets`' `can_decrease`/`prep_debit`, which compute the exact reducible balance and reject any withdrawal that would breach `min_balance`, again as part of the same atomic operation rather than a separate up-front check. [2](#0-1) [3](#0-2) 

- `pallet-treasury`'s `spend`/`spend_local` calls track cumulative spend against `max_amount` via `with_context::<SpendContext<...>>`, which accumulates spend across multiple calls dispatched in the same extrinsic (e.g. via `batch_all`) so an origin cannot bypass its spending limit by splitting the withdrawal — this is the multi-call accumulation analog and it is enforced, not bypassable.
<invoke name="codebase_search">
<parameter name="query">placeholder</parameter>
</invoke>

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L919-939)
```rust
			let amount1 = Self::mul_div(&lp_redeem_amount, &reserve1, &total_supply)?;
			let amount2 = Self::mul_div(&lp_redeem_amount, &reserve2, &total_supply)?;

			ensure!(
				!amount1.is_zero() && amount1 >= amount1_min_receive,
				Error::<T>::AssetOneWithdrawalDidNotMeetMinimum
			);
			ensure!(
				!amount2.is_zero() && amount2 >= amount2_min_receive,
				Error::<T>::AssetTwoWithdrawalDidNotMeetMinimum
			);
			let reserve1_left = reserve1.saturating_sub(amount1);
			let reserve2_left = reserve2.saturating_sub(amount2);
			ensure!(
				reserve1_left >= T::Assets::minimum_balance(asset1.clone()),
				Error::<T>::ReserveLeftLessThanMinimal
			);
			ensure!(
				reserve2_left >= T::Assets::minimum_balance(asset2.clone()),
				Error::<T>::ReserveLeftLessThanMinimal
			);
```

**File:** substrate/frame/assets/src/functions.rs (L176-243)
```rust
	pub(super) fn can_decrease(
		id: T::AssetId,
		who: &T::AccountId,
		amount: T::Balance,
		keep_alive: bool,
	) -> WithdrawConsequence<T::Balance> {
		use WithdrawConsequence::*;
		let details = match Asset::<T, I>::get(&id) {
			Some(details) => details,
			None => return UnknownAsset,
		};
		if details.supply.checked_sub(&amount).is_none() {
			return Underflow;
		}
		if details.status == AssetStatus::Frozen {
			return Frozen;
		}
		if details.status == AssetStatus::Destroying {
			return UnknownAsset;
		}
		if amount.is_zero() {
			return Success;
		}
		let account = match Account::<T, I>::get(&id, who) {
			Some(a) => a,
			None => return BalanceLow,
		};
		if account.status.is_frozen() {
			return Frozen;
		}
		if let Some(rest) = account.balance.checked_sub(&amount) {
			match (
				T::Holder::balance_on_hold(id.clone(), who),
				T::Freezer::frozen_balance(id.clone(), who),
			) {
				(None, None) => {
					if rest < details.min_balance {
						if keep_alive {
							WouldDie
						} else {
							ReducedToZero(rest)
						}
					} else {
						Success
					}
				},
				(maybe_held, maybe_frozen) => {
					let frozen = maybe_frozen.unwrap_or_default();
					let held = maybe_held.unwrap_or_default();

					// The `untouchable` balance of the asset account of `who`. This is described
					// here: https://paritytech.github.io/polkadot-sdk/master/frame_support/traits/tokens/fungible/index.html#visualising-balance-components-together-
					let untouchable = frozen.saturating_sub(held).max(details.min_balance);
					if rest < untouchable {
						if !frozen.is_zero() {
							Frozen
						} else {
							WouldDie
						}
					} else {
						Success
					}
				},
			}
		} else {
			BalanceLow
		}
	}
```

**File:** substrate/frame/assets/src/functions.rs (L291-309)
```rust
	pub(super) fn prep_debit(
		id: T::AssetId,
		target: &T::AccountId,
		amount: T::Balance,
		f: DebitFlags,
	) -> Result<T::Balance, DispatchError> {
		let actual = Self::reducible_balance(id.clone(), target, f.keep_alive)?.min(amount);
		ensure!(f.best_effort || actual >= amount, Error::<T, I>::BalanceLow);

		let conseq = Self::can_decrease(id, target, actual, f.keep_alive);
		let actual = match conseq.into_result(f.keep_alive) {
			Ok(dust) => actual.saturating_add(dust), //< guaranteed by reducible_balance
			Err(e) => {
				debug_assert!(false, "passed from reducible_balance; qed");
				return Err(e);
			},
		};

		Ok(actual)
```
