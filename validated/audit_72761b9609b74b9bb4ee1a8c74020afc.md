I found a strong analog in `substrate/frame/psm/src/lib.rs`. The `remove_psm` extrinsic requires that outstanding debt for the PSM instance be exactly zero before removal is permitted, mirroring the reported `YRizStrategy` pattern where a pool with a non-zero balance cannot be removed.

### Title
Unprivileged users can grief `remove_psm` by front-running with a `mint` to keep PSM debt non-zero - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`remove_psm` requires `Self::total_psm_debt(&internal_asset).is_zero()` [1](#0-0)  similar to the `YRizStrategy._checkPoolsWithBalanceAreIncluded` pattern where removal reverts if balance is non-zero.

### Finding Description
`remove_psm` is only callable by the PSM's `full_admin` and enforces two preconditions: `external_count == 0` and `total_psm_debt(&internal_asset).is_zero()` [1](#0-0) . However, `mint` is a fully permissionless, `Signed`-origin extrinsic that increases `PsmDebt` for any approved external asset as long as `max_debt`/per-asset ceilings are not exceeded [2](#0-1) . Any unprivileged user can observe a pending/mempool `remove_psm` transaction (or simply monitor `total_psm_debt` dropping to zero after redemptions) and front-run/race it with a tiny `mint` call, re-establishing non-zero debt and causing `remove_psm` to revert with `Error::PsmHasDebt`. This is structurally identical to the reported bug: a state-changing removal operation is gated on a balance/debt value that any unprivileged party can manipulate to be non-zero.

### Impact Explanation
The impact is a griefing/DoS against a privileged administrative operation (PSM teardown), not fund loss. This differs materially from the original report where distribution changes affecting active yield/interest strategies could be indefinitely blocked; here, `remove_psm` is a maintenance/decommissioning action gated behind `full_admin`, and the only cost to the admin is having to first stop minting (e.g. by lowering `max_debt` to zero or setting circuit breakers via `set_asset_status`/`AssetStatus`) before removal, which is a normal, documented precondition rather than an unrecoverable trap. There is no analogous "keep interest rates artificially high/low forever" impact because `remove_psm` does not gate ordinary user-facing operations (mint/redeem continue to function normally regardless of whether removal succeeds).

### Likelihood Explanation
Likelihood is low-to-moderate: an attacker needs to notice a `remove_psm` call in the mempool or poll `total_psm_debt`, but this doesn't require any privileged role, and only a trivial `mint` (subject to `min_swap_amount` and available external asset) is needed to re-introduce debt. However, since `full_admin` typically also controls `set_asset_status` (can disable minting first) and `set_max_debt` (can zero the ceiling), a competent admin has a straightforward, low-friction workaround: disable minting/ceiling before attempting removal, which the front-running attacker cannot then defeat. This significantly reduces real-world exploitability compared to the original `YRizStrategy` report where the front-run also blocked all other pools' distributions with no bypass path.

### Recommendation
Document and/or enforce that admins should call `set_asset_status`/`set_max_debt` to fully disable minting before calling `remove_psm`, or have `remove_psm` atomically set the debt ceiling and status to disabled as part of the same call so an attacker cannot re-open minting mid-removal.

### Proof of Concept
1. Admin submits `remove_psm(internal_asset)` when `total_psm_debt == 0`.
2. Attacker observes the pending transaction and submits `mint(internal_asset, external_asset, external_amount, max_fee)` with higher priority/fee, which succeeds as long as debt ceilings allow it [3](#0-2) , incrementing `PsmDebt`.
3. Admin's `remove_psm` executes afterward, hits `ensure!(Self::total_psm_debt(&internal_asset).is_zero(), Error::<T>::PsmHasDebt)` and reverts [1](#0-0) .

**Note on scope**: Given the disqualification criteria (no reachable unprivileged-attacker path with meaningful protocol impact), this finding is of low severity — it is a griefing vector against a privileged maintenance call with a straightforward operational mitigation (disable minting first), not a fund-safety or protocol-availability issue affecting ordinary users. I was not able to find any other in-scope FRAME pallet (nomination-pools, assets, asset-rewards) where an *unprivileged* user's balance/debt manipulation blocks a security-critical, user-facing state transition analogous to the original `YRizStrategy` report — `pallet-nomination-pools`' `dissolve_pool`/`withdraw_unbonded` gating uses `defensive_assert!`s and cooperative unbonding flows rather than a hard revert exploitable by griefers [4](#0-3) , and `pallet-assets`' `do_refund`/`do_refund_other` require the caller (depositor/admin) to already control the zero-balance precondition rather than exposing it to arbitrary third parties [5](#0-4) .

### Citations

**File:** substrate/frame/psm/src/lib.rs (L700-756)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::mint(T::MaxExternals::get()))]
		pub fn mint(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			external_amount: BalanceOf<T>,
			max_fee: Permill,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let info = Psm::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;

			let external = ExternalAssets::<T>::get(&internal_asset, &external_asset)
				.ok_or(Error::<T>::UnsupportedAsset)?;
			ensure!(external.status.allows_minting(), Error::<T>::MintingStopped);

			let (ext_decimals, internal_decimals) =
				Self::ensure_decimals_match(&info, &internal_asset, &external_asset, &external)?;

			let internal_equivalent =
				Self::external_to_internal(external_amount, ext_decimals, internal_decimals)?;
			ensure!(!internal_equivalent.is_zero(), Error::<T>::AmountTooSmallAfterConversion);
			ensure!(internal_equivalent >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let effective_external =
				Self::internal_to_external(internal_equivalent, ext_decimals, internal_decimals)?;

			let fee_rate = MintingFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_equivalent);
			let internal_to_user = internal_equivalent.saturating_sub(fee);

			let current_total_psm_debt = Self::total_psm_debt(&internal_asset);
			ensure!(
				current_total_psm_debt.saturating_add(internal_equivalent) <= info.max_debt,
				Error::<T>::ExceedsMaxPsmDebt
			);

			let current_debt = PsmDebt::<T>::get(&internal_asset, &external_asset);
			let max_debt = Self::max_asset_debt(&internal_asset, &external_asset, &info);
			let new_debt = current_debt.saturating_add(internal_equivalent);
			ensure!(new_debt <= max_debt, Error::<T>::ExceedsMaxPsmDebt);

			let psm_account = Self::psm_account(&internal_asset);
			T::Fungibles::transfer(
				external_asset.clone(),
				&who,
				&psm_account,
				effective_external,
				Preservation::Expendable,
			)?;
			T::Fungibles::mint_into(internal_asset.clone(), &who, internal_to_user)?;
			if !fee.is_zero() {
				T::Fungibles::mint_into(internal_asset.clone(), &info.fee_destination, fee)?;
			}

			PsmDebt::<T>::insert(&internal_asset, &external_asset, new_debt);
```

**File:** substrate/frame/psm/src/lib.rs (L1030-1034)
```rust
		pub fn remove_psm(origin: OriginFor<T>, internal_asset: T::AssetId) -> DispatchResult {
			Self::ensure_psm_admin(origin, &internal_asset, |l| l.can_remove_psm())?;
			let info = Psm::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;
			ensure!(info.external_count == 0, Error::<T>::PsmHasApprovedExternals);
			ensure!(Self::total_psm_debt(&internal_asset).is_zero(), Error::<T>::PsmHasDebt);
```

**File:** substrate/frame/nomination-pools/src/lib.rs (L3358-3391)
```rust
	/// Remove everything related to the given bonded pool.
	///
	/// Metadata and all of the sub-pools are also deleted. All accounts are dusted and the leftover
	/// of the reward account is returned to the depositor.
	pub fn dissolve_pool(bonded_pool: BondedPool<T>) {
		let reward_account = bonded_pool.reward_account();
		let bonded_account = bonded_pool.bonded_account();

		ReversePoolIdLookup::<T>::remove(&bonded_account);
		RewardPools::<T>::remove(bonded_pool.id);
		SubPoolsStorage::<T>::remove(bonded_pool.id);

		// remove the ED restriction from the pool reward account.
		let _ = Self::unfreeze_pool_deposit(&bonded_pool.reward_account()).defensive();

		// Kill accounts from storage by making their balance go below ED. We assume that the
		// accounts have no references that would prevent destruction once we get to this point. We
		// don't work with the system pallet directly, but
		// 1. we drain the reward account and kill it. This account should never have any extra
		// consumers anyway.
		// 2. the bonded account should become a 'killed stash' in the staking system, and all of
		//    its consumers removed.
		defensive_assert!(
			frame_system::Pallet::<T>::consumers(&reward_account) == 0,
			"reward account of dissolving pool should have no consumers"
		);
		defensive_assert!(
			frame_system::Pallet::<T>::consumers(&bonded_account) == 0,
			"bonded account of dissolving pool should have no consumers"
		);
		defensive_assert!(
			T::StakeAdapter::total_stake(Pool::from(bonded_pool.bonded_account())) == Zero::zero(),
			"dissolving pool should not have any stake in the staking pallet"
		);
```

**File:** substrate/frame/assets/src/functions.rs (L369-412)
```rust
	/// Returns a deposit or a consumer reference, destroying an asset-account.
	/// Non-zero balance accounts refunded and destroyed only if `allow_burn` is true.
	pub(super) fn do_refund(id: T::AssetId, who: T::AccountId, allow_burn: bool) -> DispatchResult {
		use AssetStatus::*;
		use ExistenceReason::*;

		let mut account = Account::<T, I>::get(&id, &who).ok_or(Error::<T, I>::NoDeposit)?;
		ensure!(matches!(account.reason, Consumer | DepositHeld(..)), Error::<T, I>::NoDeposit);
		let mut details = Asset::<T, I>::get(&id).ok_or(Error::<T, I>::Unknown)?;
		ensure!(matches!(details.status, Live | Frozen), Error::<T, I>::IncorrectStatus);
		ensure!(account.balance.is_zero() || allow_burn, Error::<T, I>::WouldBurn);
		Self::ensure_account_can_die(id.clone(), &who)?;

		if let Some(deposit) = account.reason.take_deposit() {
			T::Currency::unreserve(&who, deposit);
		}

		if let Remove = Self::dead_account(&who, &mut details, &account.reason, false) {
			if !account.balance.is_zero() {
				debug_assert!(details.supply >= account.balance, "supply < balance; qed");
				details.supply = details.supply.saturating_sub(account.balance);
			}
			Account::<T, I>::remove(&id, &who);
		} else {
			debug_assert!(false, "refund did not result in dead account?!");
			// deposit may have been refunded, need to update `Account`
			Account::<T, I>::insert(id, &who, account);
			return Ok(());
		}

		if !account.balance.is_zero() {
			Self::deposit_event(Event::Burned {
				asset_id: id.clone(),
				owner: who.clone(),
				balance: account.balance,
			});
		}

		Asset::<T, I>::insert(&id, details);
		// Executing a hook here is safe, since it is not in a `mutate`.
		T::Freezer::died(id.clone(), &who);
		T::Holder::died(id, &who);
		Ok(())
	}
```
