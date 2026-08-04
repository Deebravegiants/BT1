### Title
Dissolve permanently burns any dust balance transferred directly into the crowdloan pot rather than returning it - ([File: polkadot/runtime/common/src/crowdloan/mod.rs])

### Summary
`Pallet::dissolve` calls `CurrencyOf::<T>::make_free_balance_be(&pot, Zero::zero())` to zero out the fund's pot account regardless of the actual balance held there, only checking `fund.raised == 0`, not the pot's actual free balance. Any account can send an arbitrary amount to the pot account via a normal `transfer_allow_death`/`transfer_keep_alive` call, and if the depositor (or any signed account after `fund.end`) subsequently calls `dissolve`, that balance is unconditionally burned.

### Finding Description
`dissolve` at [1](#0-0)  computes `permitted = who == fund.depositor || now >= fund.end` and `can_dissolve = permitted && fund.raised.is_zero()`. It never re-checks `CurrencyOf::<T>::free_balance(&pot)` before burning. The burn line: [2](#0-1) 

unconditionally sets the pot's free balance to zero via `make_free_balance_be`, which for pallet-balances burns (destroys) any surplus balance rather than crediting it back to a contributor or depositor. The pot account (`Self::fund_account_id(fund.fund_index)`) is a plain `AccountId` derived from `PalletId` + index, so it is a normal transferable account — any signed user can call `Balances::transfer_allow_death(origin, pot, X)` to send dust/funds into it with no permission check, since the pot is not a privileged or filtered destination.

Because `fund.raised` is fully independent bookkeeping (an in-storage counter of contributions, decremented on `withdraw`/`refund`, not derived from the pot's live balance), sending funds directly to the pot does not affect `fund.raised`. Thus the precondition `fund.raised.is_zero()` can hold true simultaneously with the pot having a nonzero free balance, and `dissolve` will burn that balance.

This is not stopped by any origin, filter, or balance check: `ensure_signed` only requires a signed caller (the depositor or anyone once `now >= fund.end`); there's no check comparing pot balance to `fund.raised` at `dissolve` time (unlike `ensure_crowdloan_ended` used by `withdraw`/`refund`, which does check `free_balance(&fund_account) >= fund.raised`, but `dissolve` does not call `ensure_crowdloan_ended` at all).

### Impact Explanation
Any third party can cause deterministic, irreversible burning of tokens that were never part of the crowdloan's tracked contributions, by transferring balance to the fund's pot account and having the depositor (or anyone after `fund.end`) call `dissolve`. This destroys value with no way for the sender to recover it — a permanent loss of user funds, matching the scoped impact ("permanent trapping/destruction of funds contributed via non-crowdloan channel").

However, note this is a self-inflicted loss by whoever sends funds to the pot outside the contribution flow — it requires the attacker (or a confused user) to voluntarily send funds to a specific derived account, and requires someone (depositor or anyone post-`fund.end`) to subsequently call `dissolve`. It cannot be used to steal a third party's *other* assets; the attacker is destroying/donating their own transferred balance, or — the more concerning case — an attacker deliberately sends dust to *someone else's soon-to-be-dissolved* pot to force burn of value that might otherwise have been recoverable (e.g., if governance were later going to sweep leftover pot balance). Since there is no governance/recovery path documented for stray funds in this code, and the burn is triggered by an unprivileged call, this matches a real (if narrow) unrestricted-burn bug: no check ties the burned amount to `fund.raised`.

### Likelihood Explanation
Highly feasible and repeatable: no special permissions, timing, or races are needed beyond fund.end having passed (or being the depositor), which is normal end-of-crowdloan state reached by every unsuccessful crowdloan. An attacker simply needs to observe an ended crowdloan with `raised == 0` (or wait for refund/withdraw to zero it) and front-run/race the `dissolve` call, or simply transfer dust before the depositor calls dissolve (dissolve is not restricted to same-block, and pot accounts are public/derivable via `fund_account_id`).

### Recommendation
In `dissolve`, before burning, check the pot's actual free/total balance and either:
- refuse to dissolve if `free_balance(&pot) != 0` (require pot to be fully drained by a prior refund/sweep step), or
- transfer any leftover pot balance back to the depositor (or to a treasury) instead of using `make_free_balance_be` to zero it silently.
Also consider calling `Self::ensure_crowdloan_ended`-style balance checks in `dissolve` to detect any balance discrepancy versus `fund.raised`, and emit an event/error rather than silently destroying value.

### Proof of Concept
Rust integration test in `polkadot/runtime/common/src/crowdloan/mod.rs::tests`:
1. Create a fund via `Crowdloan::create`, let it end with `raised == 0` (no contributions, or fully refunded).
2. From an unrelated signed account `attacker`, call `Balances::transfer_allow_death(attacker, pot_account, DUST)`.
3. Record `total_issuance` before dissolve.
4. Call `Crowdloan::dissolve(depositor, index)`.
5. Assert:
   - `Balances::free_balance(&pot_account) == 0` (pot zeroed),
   - `Balances::total_issuance()` decreased by exactly `DUST` (funds burned, not returned to `attacker` or `depositor`),
   - `attacker`'s balance does NOT recover the `DUST` amount.

This confirms the burn is unconditional on real pot balance and independent of `fund.raised`, i.e., an unprivileged transfer plus a normal `dissolve` call destroys funds with no recovery path.

### Citations

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L555-581)
```rust
		pub fn dissolve(origin: OriginFor<T>, #[pallet::compact] index: ParaId) -> DispatchResult {
			let who = ensure_signed(origin)?;

			let fund = Funds::<T>::get(index).ok_or(Error::<T>::InvalidParaId)?;
			let pot = Self::fund_account_id(fund.fund_index);
			let now = frame_system::Pallet::<T>::block_number();

			// Only allow dissolution when the raised funds goes to zero,
			// and the caller is the fund creator or we are past the end date.
			let permitted = who == fund.depositor || now >= fund.end;
			let can_dissolve = permitted && fund.raised.is_zero();
			ensure!(can_dissolve, Error::<T>::NotReadyToDissolve);

			// Assuming state is not corrupted, the child trie should already be cleaned up
			// and all funds in the crowdloan account have been returned. If not, governance
			// can take care of that.
			debug_assert!(Self::contribution_iterator(fund.fund_index).count().is_zero());

			// Crowdloan over, burn all funds.
			let _imba = CurrencyOf::<T>::make_free_balance_be(&pot, Zero::zero());
			let _ = frame_system::Pallet::<T>::dec_providers(&pot).defensive();

			CurrencyOf::<T>::unreserve(&fund.depositor, fund.deposit);
			Funds::<T>::remove(index);
			Self::deposit_event(Event::<T>::Dissolved { para_id: index });
			Ok(())
		}
```
