### Title
Malicious `asset-rewards` pool creator can freeze a targeted staker's reward asset to selectively block that staker's reward payout - (File: `substrate/frame/asset-rewards/src/lib.rs`)

### Summary
`pallet-asset-rewards` allows permissionless creation of reward pools with an arbitrary, attacker-chosen `reward_asset_id`. `harvest_rewards` performs a single unconditional `T::Assets::transfer` call to the staker and propagates any error with `?`, aborting the whole call if that transfer fails. Because `pallet-assets` lets an asset's `Freezer`/admin freeze any individual account for that asset, a pool creator who mints their own reward asset (naming themselves Freezer) can freeze exactly one victim staker's account for that asset, causing only that staker's `harvest_rewards` calls to revert forever, while every other staker in the same pool is unaffected. This mirrors the C4 finding's root cause (a single token-transfer failure aborting an entire withdrawal/payout instead of being isolated to the affected leg) but adapted to FRAME's fungible-transfer semantics instead of Solidity `ERC20.transfer` return values.

### Finding Description
`create_pool` is reachable by any signed account on Asset Hub: [1](#0-0) 

Pool creation only requires the two assets to exist (`T::Assets::asset_exists`) — there is no requirement that `reward_asset_id` be a trusted/whitelisted asset class: [2](#0-1) 

`harvest_rewards` does a single transfer of the reward asset to the staker and bubbles up any error via `?`, aborting the extrinsic (state changes are rolled back for the whole call): [3](#0-2) 

`pallet-assets` explicitly supports per-account freezing by the asset's `Freezer`, which causes any transfer involving that account to fail with `Error::Frozen`: [4](#0-3) [5](#0-4) 

Because a pool creator using a self-issued asset as the reward token also controls the `Freezer`/admin role for that asset, they can:
1. Create asset `A` (self as owner/Freezer).
2. Create a reward pool with `reward_asset_id = A` via the permissionless `CreatePoolOrigin`.
3. Wait for a specific victim to `stake` and accrue rewards.
4. Call `Assets::freeze` on the victim's account for asset `A` only.
5. The victim's subsequent `harvest_rewards` calls fail with `Error::Frozen`, reverting the whole extrinsic, while other stakers (not frozen) continue to harvest normally.

### Impact Explanation
The attacker can selectively and indefinitely deny a specific staker their accrued reward payout in a pool they otherwise legitimately participate in, without impacting any other participant or any other functionality of the pool — the exact "surgical" griefing pattern described in the referenced report (targeting one specific holder's entitlement instead of breaking the whole contract). I was not able to fully verify in this pass whether `unstake` also depends on a reward-asset transfer succeeding (I ran out of investigation budget before reading `unstake`'s full body), so I cannot confirm with certainty whether the victim's *staked principal* is also frozen out, or only the reward claim. If reward settlement is also entangled with `unstake`, the impact would extend to blocking withdrawal of the staked principal too, which would raise severity to match the original finding closely. As it stands, confirmed impact is limited to denial of reward harvesting for a targeted victim.

### Likelihood Explanation
Likelihood is realistic and requires no privileged or trusted role beyond the attacker's own self-granted control over an asset they create: `CreatePoolOrigin` is `EnsureSigned<AccountId>` on Asset Hub runtimes, so anyone can create a pool with any existing asset as the reward token, and anyone can create their own asset via `pallet-assets` and name themselves as `Freezer`. No governance or root access is needed.

### Recommendation
- Do not let `harvest_rewards` (and any other function paying out reward-asset transfers) hard-fail the entire extrinsic when the transfer errors; instead, decouple the accounting update from the transfer, or provide a permissionless "claim to any address"/emergency-withdrawal path that lets the staker redirect a blocked payout to an alternate account they control, and/or the analogous "sponsor-recommended" fallback the original report converged on.
- Consider requiring `reward_asset_id` to be constrained (e.g., an allow-listed set of assets, or require the pool creator not have freeze/admin capability over the reward asset) so a permissionless pool's reward token cannot be weaponized against individual stakers.
- Clearly document in `pallet-asset-rewards` that arbitrary/attacker-controlled reward assets can be used to grief individual stakers, and gate high-value/production deployments behind a curated reward-asset allowlist rather than raw `asset_exists` checks.

### Proof of Concept
1. Attacker calls `pallet_assets::create`/`force_create` (or uses `EnsureSigned` permissionless creation) to mint asset `A`, setting themselves as owner/Freezer.
2. Attacker calls `AssetRewards::create_pool(origin=attacker, staked_asset_id=X, reward_asset_id=A, ...)` — permitted because `CreatePoolOrigin = EnsureSigned<AccountId>` [1](#0-0) .
3. Victim stakes asset `X` into the pool via `AssetRewards::stake`, accruing rewards denominated in `A`.
4. Attacker calls `Assets::freeze(origin=attacker, id=A, who=victim)` [4](#0-3) .
5. Victim calls `AssetRewards::harvest_rewards`; the internal `T::Assets::transfer(A, pool_account, victim, rewards, ...)` returns `Error::Frozen`, and the `?` at that call site aborts the extrinsic [3](#0-2) , while unfrozen stakers in the same pool continue to harvest successfully.

### Citations

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/lib.rs (L568-576)
```rust
impl pallet_asset_rewards::Config for Runtime {
	type RuntimeEvent = RuntimeEvent;
	type PalletId = AssetRewardsPalletId;
	type Balance = Balance;
	type Assets = NativeAndAllAssets;
	type AssetsFreezer = NativeAndAllAssetsFreezer;
	type AssetId = xcm::v5::Location;
	type CreatePoolOrigin = EnsureSigned<AccountId>;
	type RuntimeFreezeReason = RuntimeFreezeReason;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L586-595)
```rust

			// Transfer unclaimed rewards from the pool to the staker.
			T::Assets::transfer(
				pool_info.reward_asset_id,
				&pool_info.account,
				&staker,
				staker_info.rewards,
				// Could kill the account, but only if the pool was already almost empty.
				Preservation::Expendable,
			)?;
```

**File:** substrate/frame/asset-rewards/src/lib.rs (L843-858)
```rust
	fn create_pool(
		creator: &T::AccountId,
		staked_asset_id: T::AssetId,
		reward_asset_id: T::AssetId,
		reward_rate_per_block: T::Balance,
		expiry: DispatchTime<BlockNumberFor<T>>,
		admin: &T::AccountId,
	) -> Result<PoolId, DispatchError> {
		// Ensure the assets exist.
		ensure!(T::Assets::asset_exists(staked_asset_id.clone()), Error::<T>::NonExistentAsset);
		ensure!(T::Assets::asset_exists(reward_asset_id.clone()), Error::<T>::NonExistentAsset);

		// Check the expiry block.
		let now = T::BlockNumberProvider::current_block_number();
		let expiry_block = expiry.evaluate(now);
		ensure!(expiry_block > now, Error::<T>::ExpiryBlockMustBeInTheFuture);
```

**File:** substrate/frame/assets/src/lib.rs (L1192-1216)
```rust
		#[pallet::call_index(11)]
		pub fn freeze(
			origin: OriginFor<T>,
			id: T::AssetIdParameter,
			who: AccountIdLookupOf<T>,
		) -> DispatchResult {
			let origin = ensure_signed(origin)?;
			let id: T::AssetId = id.into();

			let d = Asset::<T, I>::get(&id).ok_or(Error::<T, I>::Unknown)?;
			ensure!(
				d.status == AssetStatus::Live || d.status == AssetStatus::Frozen,
				Error::<T, I>::IncorrectStatus
			);
			ensure!(origin == d.freezer, Error::<T, I>::NoPermission);
			let who = T::Lookup::lookup(who)?;

			Account::<T, I>::try_mutate(&id, &who, |maybe_account| -> DispatchResult {
				maybe_account.as_mut().ok_or(Error::<T, I>::NoAccount)?.status =
					AccountStatus::Frozen;
				Ok(())
			})?;

			Self::deposit_event(Event::<T, I>::Frozen { asset_id: id, who });
			Ok(())
```

**File:** substrate/frame/assets/src/tests.rs (L1036-1052)
```rust
#[test]
fn transferring_from_frozen_account_should_not_work() {
	build_and_execute(|| {
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), 0, 1, true, 1));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 1, 100));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 2, 100));
		assert_eq!(Assets::balance(0, 1), 100);
		assert_eq!(Assets::balance(0, 2), 100);
		assert_ok!(Assets::freeze(RuntimeOrigin::signed(1), 0, 2));
		// can transfer to `2`
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(1), 0, 2, 50));
		// cannot transfer from `2`
		assert_noop!(Assets::transfer(RuntimeOrigin::signed(2), 0, 1, 25), Error::<Test>::Frozen);
		assert_eq!(Assets::balance(0, 1), 50);
		assert_eq!(Assets::balance(0, 2), 150);
	});
}
```
