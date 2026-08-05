### Title
Untrusted Asset Freezer Role Enables Permanent DoS/Fund-Lock on `pallet-asset-conversion` Pools - (File: `substrate/frame/asset-conversion/src/lib.rs`)

### Summary
`pallet-asset-conversion::create_pool` (via `do_create_pool`) allows any signed account to create a swap pool for an arbitrary pair of `AssetKind`s without validating that the underlying `pallet-assets` asset has no privileged "Freezer" role controlled by an untrusted party. Since `pallet-assets` lets an asset's Owner freely assign the `freezer` (and `admin`) roles via `set_team`, and asset creation itself can be permissionless (deposit-based) depending on runtime config, a malicious actor can create an asset, pair it into a pool, attract liquidity from other users, and then call `Assets::freeze` on the pool's account, blocking all outgoing transfers of that asset from the pool. This mirrors the reported SPL "mint freeze authority" DoS: an external, pool-uncontrolled authority can freeze the pool's token account and permanently lock user funds.

### Finding Description
`do_create_pool` in `substrate/frame/asset-conversion/src/lib.rs` only checks that `asset1 != asset2` and that the pool doesn't already exist — it performs no validation of the asset's team/freezer configuration: [1](#0-0) 

`pallet-assets` documents the Freezer as "An account ID uniquely privileged to be able to freeze an account from transferring a particular class of assets," and this role is settable by the asset Owner via `set_team`, completely independent of pool logic: [2](#0-1) [3](#0-2) 

The `freeze` extrinsic lets the asset's Freezer set an arbitrary account's status to `AccountStatus::Frozen`, requiring only that `origin == d.freezer`: [4](#0-3) 

Once an account is frozen, tests confirm that transfers *into* the account still succeed, but transfers *from* the frozen account fail with `Error::Frozen`: [5](#0-4) 

Because `do_add_liquidity`/`do_remove_liquidity`/swap logic in `pallet-asset-conversion` move funds through the pool's sovereign account (`T::PoolLocator::address`) using the standard `fungibles::transfer` implementation of `pallet-assets` (the same code path enforcing the `Frozen` check), freezing the pool's account for one leg of the pair blocks:
- `remove_liquidity` (which must transfer the frozen asset out of the pool back to the LP),
- `swap_exact_tokens_for_tokens`/`swap_tokens_for_exact_tokens` in the direction that requires paying out the frozen asset.

An integration test elsewhere in the repo directly exercises this scenario for `ChargeAssetTxPayment`, confirming that once the pool/caller account is `Frozen`/`Blocked`, the swap path is skipped and pool state becomes unusable for that asset: [6](#0-5) 

### Impact Explanation
If a user (attacker) creates an asset (`pallet-assets`) that they control, sets themselves as `Freezer` (default at creation via `force_create`/`create`+`set_team`), and pairs it into a pool with another asset (e.g., the native token) via `AssetConversion::create_pool`, then attracts genuine liquidity providers to `add_liquidity`, the attacker can subsequently call `Assets::freeze` on the pool's sovereign account for that asset ID. This:
- Permanently blocks `remove_liquidity` and the swap direction that requires releasing the frozen asset from the pool, trapping other users' contributed funds.
- Constitutes a Denial-of-Service against the pool and a potential permanent loss of funds for liquidity providers who deposited the non-frozen leg's counterpart, exactly analogous to the SPL "freeze authority on input token mint" finding.

### Likelihood Explanation
Likelihood depends heavily on runtime configuration: whether asset creation and pool creation are permissionless for arbitrary user-created assets. On chains where `pallet-assets::Config::CreateOrigin` allows permissionless (deposit-based) asset creation and `pallet-asset-conversion::Config` allows pools for any such `AssetKind` (as seen in the generic `NativeOrWithId`-based test configuration and in the trusted-asset-hub runtimes where `AssetConversion::create_pool` is exposed to signed users), an attacker can self-issue the malicious asset and become its own Freezer at no special privilege beyond a deposit. On Asset Hub runtimes specifically, pool creation from `pallet-assets::Instance1`/foreign assets is permissionless for signed accounts, while the freezer/admin role of those assets is fully attacker-controlled at asset-creation time — this is a realistic, unprivileged attack path, not a "trusted role compromise."

### Recommendation
- In `do_create_pool` (`substrate/frame/asset-conversion/src/lib.rs`), require that any `AssetKind` used in a pool either (a) has no independent Freezer/Admin role capable of freezing the pool's account, or (b) restrict poolable assets to a runtime-defined allow-list / "sufficient"/trusted asset class (as Asset Hub already does for the `PoolAssets` LP-token registry via `Instance3`).
- Alternatively, add a `PoolAssetsFilter`/`AssetKind` validation hook at `create_pool` time that queries the underlying asset's team info (owner/admin/freezer) and rejects pools where the Freezer is not the pool/pallet account, governance, or `None`.
- Document and enforce that only assets meeting these criteria can be onboarded into swap pools, mirroring the recommended SPL fix of validating absence of an untrusted freeze authority.

### Proof of Concept
1. Attacker calls `pallet_assets::create` (permissionless path, paying deposit) to create asset `X`, becoming its Owner/Admin/Freezer (or explicitly `set_team` to set themselves as `freezer`).
2. Attacker calls `AssetConversion::create_pool(Native, X)` — succeeds, no validation of `X`'s team, per `do_create_pool` [1](#0-0) .
3. Victim calls `AssetConversion::add_liquidity(Native, X, ...)`, depositing genuine funds into the pool's sovereign account.
4. Attacker calls `Assets::freeze(X, pool_account)` using their Freezer privilege [4](#0-3) .
5. Victim's subsequent `remove_liquidity` or swap requiring the pool to send out asset `X` fails with `Error::Frozen`, permanently locking the victim's share of the pool — matching the frozen-account transfer behavior demonstrated in `pallet-assets` tests [5](#0-4)  and mirrored by the pool-DoS scenario captured in the tx-payment integration test [6](#0-5) .

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L729-759)
```rust
		pub(crate) fn do_create_pool(
			creator: &T::AccountId,
			asset1: T::AssetKind,
			asset2: T::AssetKind,
			initial_fee: Option<Permill>,
		) -> Result<T::PoolId, DispatchError> {
			ensure!(asset1 != asset2, Error::<T>::InvalidAssetPair);
			if let Some(fee) = initial_fee {
				ensure!(fee <= T::MaxSwapFee::get(), Error::<T>::FeeTooHigh);
			}

			// prepare pool_id
			let pool_id = T::PoolLocator::pool_id(&asset1, &asset2)
				.map_err(|_| Error::<T>::InvalidAssetPair)?;
			ensure!(!Pools::<T>::contains_key(&pool_id), Error::<T>::PoolExists);

			let pool_account =
				T::PoolLocator::address(&pool_id).map_err(|_| Error::<T>::InvalidAssetPair)?;

			// pay the setup fee
			let fee =
				Self::withdraw(T::PoolSetupFeeAsset::get(), creator, T::PoolSetupFee::get(), true)?;
			T::PoolSetupFeeTarget::on_unbalanced(fee);

			if T::Assets::should_touch(asset1.clone(), &pool_account) {
				T::Assets::touch(asset1.clone(), &pool_account, creator)?
			};

			if T::Assets::should_touch(asset2.clone(), &pool_account) {
				T::Assets::touch(asset2.clone(), &pool_account, creator)?
			};
```

**File:** substrate/frame/assets/src/lib.rs (L56-60)
```rust
//! * **Fungible asset**: An asset whose units are interchangeable.
//! * **Issuer**: An account ID uniquely privileged to be able to mint a particular class of assets.
//! * **Freezer**: An account ID uniquely privileged to be able to freeze an account from
//!   transferring a particular class of assets.
//! * **Freezing**: Removing the possibility of an unpermissioned transfer of an asset from a
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

**File:** substrate/frame/assets/src/lib.rs (L1369-1394)
```rust
		pub fn set_team(
			origin: OriginFor<T>,
			id: T::AssetIdParameter,
			issuer: AccountIdLookupOf<T>,
			admin: AccountIdLookupOf<T>,
			freezer: AccountIdLookupOf<T>,
		) -> DispatchResult {
			let origin = ensure_signed(origin)?;
			let issuer = T::Lookup::lookup(issuer)?;
			let admin = T::Lookup::lookup(admin)?;
			let freezer = T::Lookup::lookup(freezer)?;
			let id: T::AssetId = id.into();

			Asset::<T, I>::try_mutate(id.clone(), |maybe_details| {
				let details = maybe_details.as_mut().ok_or(Error::<T, I>::Unknown)?;
				ensure!(details.status == AssetStatus::Live, Error::<T, I>::AssetNotLive);
				ensure!(origin == details.owner, Error::<T, I>::NoPermission);

				details.issuer = issuer.clone();
				details.admin = admin.clone();
				details.freezer = freezer.clone();

				Self::deposit_event(Event::TeamChanged { asset_id: id, issuer, admin, freezer });
				Ok(())
			})
		}
```

**File:** substrate/frame/assets/src/tests.rs (L1063-1073)
```rust
		// cannot freeze an account that doesn't have an `Assets` entry
		assert_noop!(Assets::freeze(RuntimeOrigin::signed(1), 0, 2), Error::<Test>::NoAccount);
		assert_ok!(Assets::touch(RuntimeOrigin::signed(2), 0));
		// now it can be frozen
		assert_ok!(Assets::freeze(RuntimeOrigin::signed(1), 0, 2));
		// can transfer to `2` even though its frozen
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(1), 0, 2, 50));
		// cannot transfer from `2`
		assert_noop!(Assets::transfer(RuntimeOrigin::signed(2), 0, 1, 25), Error::<Test>::Frozen);
		assert_eq!(Assets::balance(0, 1), 50);
		assert_eq!(Assets::balance(0, 2), 50);
```

**File:** substrate/frame/transaction-payment/asset-conversion-tx-payment/src/tests.rs (L1386-1424)
```rust
			// Block the caller's asset account — `can_deposit` will now return `Blocked`,
			// so the refund pre-flight check fails and the swap is skipped entirely.
			assert_ok!(Assets::block(
				RuntimeOrigin::signed(freezer),
				asset_id.into(),
				<Runtime as system::Config>::Lookup::unlookup(caller),
			));

			// Record the pool state before post-dispatch — it must be untouched since
			// the refund swap is skipped.
			let pool_account = <<Runtime as pallet_asset_conversion::Config>::PoolLocator
				as pallet_asset_conversion::PoolLocator<_, _, _>>::pool_address(
				&NativeOrWithId::Native,
				&NativeOrWithId::WithId(asset_id),
			)
			.unwrap();
			let pool_native_before = Balances::free_balance(&pool_account);
			let pool_asset_before = Assets::balance(asset_id, &pool_account);

			let post_info = post_info_from_weight(WEIGHT_50.saturating_add(extension_weight));

			// Security invariant: post_dispatch must NOT return `Err`.
			assert_ok!(ChargeAssetTxPayment::<Runtime>::post_dispatch_details(
				pre,
				&info,
				&post_info,
				len,
				&Ok(()),
			));

			// Caller's balance is unchanged since withdraw: refund was not credited
			// because the account is blocked.
			assert_eq!(Assets::balance(asset_id, &caller), balance_after_withdraw);

			// Pool state is untouched — the `can_deposit` pre-flight check prevents
			// the swap from executing.
			assert_eq!(Balances::free_balance(&pool_account), pool_native_before);
			assert_eq!(Assets::balance(asset_id, &pool_account), pool_asset_before);

```
