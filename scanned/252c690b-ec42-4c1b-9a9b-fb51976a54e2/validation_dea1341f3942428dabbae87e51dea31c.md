### Title
Colliding `RemoteLockedFungibles` keys after XCM-version migration strand a locked-fungible record forever, making its remote-lock bookkeeping unreachable via `request_unlock` - ([File: polkadot/xcm/pallet-xcm/src/migration.rs])

### Summary
`migrate_data_to_xcm_version`'s second step (key-swap) for `RemoteLockedFungibles` computes a migrated key `(to_xcm_version, account, asset_id)` from an old key and, if that migrated key already has an entry, simply logs an error and `continue`s, leaving the old key's record permanently un-migrated. Because ordinary (unprivileged) usage of `pallet_xcm::lock_asset`/remote `NoteUnlockable` inserts entries keyed by the *current* `XCM_VERSION` at call time, an account that legitimately locks the same underlying remote asset in two different XCM-version epochs can end up with two records whose keys normalize to the identical target key after a later version bump, causing one record to be permanently orphaned at its old key.

### Finding Description
`RemoteLockedFungibles` entries are created only through `Pallet::<T>::note_unlockable` [1](#0-0) , which builds the key as `(XCM_VERSION, account, id)` using the crate's *current* compiled `XCM_VERSION` constant, not an attacker-chosen value. A signed user can trigger this path unprivileged via the `LockAsset` XCM instruction (executed from a signed extrinsic through `pallet_xcm::execute`/`send`), which is handled in the executor and calls `AssetLocker::prepare_lock`/`enact` on the sending side and `note_unlockable` on the remote/unlocker side [2](#0-1) .

If the same account locks the same real remote asset in two different XCM-version epochs of the chain's life (i.e., before and after a runtime upgrade that bumps `XCM_VERSION`), it produces two separate `RemoteLockedFungibles` entries with different key-version components, because the merge/clobber protection in `note_unlockable` only checks for an *exact* key match, not for other version-tagged keys representing the same logical asset [3](#0-2) .

When a later runtime upgrade runs `MigrateToLatestXcmVersion`, the key-migration loop in `migration.rs` iterates all keys, migrates each old key via `try_migrate`, and before performing the storage `swap`, checks whether the computed `new_key` already exists: [4](#0-3) 
If it does (because the two independently created entries now normalize to the same target key), the code only logs an error and `continue`s, permanently leaving the older key's `RemoteLockedFungibleRecord` un-migrated. This is by design a "skip", with no reconciliation, merging, or retry-with-different-outcome logic — it simply repeats on every subsequent migration and, if the competing key is always resolved first, the stale record never migrates.

The stranded record becomes practically unreachable by the standard "unlock the remote lock" flow: `Pallet::<T>::prepare_reduce_unlockable` (invoked by the user-triggered `RequestUnlock` XCM instruction, reachable from a signed extrinsic) always computes its lookup key using the *current* `XCM_VERSION`, not the old stranded key [5](#0-4) . Consequently, the legitimate owner of the stranded record can never again target it through `RequestUnlock`/`prepare_reduce_unlockable`, permanently losing on-chain bookkeeping proof needed to unlock the corresponding remote-chain lock.

### Impact Explanation
The affected `RemoteLockedFungibleRecord.amount`/`consumers` bookkeeping — which represents (and is required to authorize unlocking of) real funds locked on a remote chain — becomes permanently orphaned at an old, no-longer-addressable storage key. Since `prepare_reduce_unlockable` can only compute and look up the *current*-version key, the owner loses the ability to issue a valid `RequestUnlock` for that stranded portion, effectively permanently freezing the corresponding remotely-locked funds from this chain's perspective — matching the scoped "lock funds unlockable" impact.

### Likelihood Explanation
This does not require a single malicious extrinsic; it requires an account to hold remote locks for the same asset created in two different XCM-version epochs (i.e., across at least one runtime upgrade that changes `XCM_VERSION`), such that both entries' asset-ids normalize identically after `into_version`. This is a legitimate, unprivileged sequence of actions (signed `lock_asset` calls across chain-upgrade boundaries) and does not rely on any privileged origin, mocked state, or direct storage writes. However, it requires precise coincidence of two independently-created keys collapsing to the same normalized key, and requires an intervening runtime XCM-version upgrade (a governance-controlled event) as the trigger for the migration to run — the trigger is privileged/infrequent, but the vulnerable path itself (creating colliding entries, and losing access to the older one) is fully reachable by an ordinary signed user across normal chain lifecycle events.

### Recommendation
On collision, do not silently skip: merge the old record into the existing new-key record (validating `locker`/`owner` match and summing/max-ing `amount` and `consumers`, mirroring the merge logic already present in `note_unlockable`), or reject/defensively fail the runtime upgrade migration and require manual remediation before completing, rather than leaving unreachable stale storage indefinitely.

### Proof of Concept
Extend the existing `migrate_data_to_xcm_version_works` test in `polkadot/xcm/pallet-xcm/src/tests/mod.rs` [6](#0-5) :
1. Insert a `key_old` = `(previous_version, account, asset_id_v_previous)` record with a nonzero `amount` and some `consumers`.
2. Insert a `key_new` = `(latest_version, account, asset_id_v_latest)` record for the same account (same normalized asset id) with a different `amount`/`consumers`, simulating a second lock created after a version bump.
3. Call `Pallet::<Test>::migrate_data_to_xcm_version(&mut Weight::zero(), latest_version)`.
4. Assert that `RemoteLockedFungibles::<Test>::get(&key_old)` still returns `Some(..)` (the old entry persists, un-migrated) and `RemoteLockedFungibles::<Test>::get(&key_new)` is unchanged.
5. Simulate the user calling `Pallet::<Test>::prepare_reduce_unlockable(locker, asset, owner)` (as invoked from a `RequestUnlock` XCM) and assert it can only ever resolve `key_new`, never `key_old`, proving the old record's locked amount/consumers are permanently unreachable through the standard unlock path.

### Citations

**File:** polkadot/xcm/pallet-xcm/src/lib.rs (L3768-3795)
```rust
	fn note_unlockable(
		locker: Location,
		asset: Asset,
		mut owner: Location,
	) -> Result<(), xcm_executor::traits::LockError> {
		use xcm_executor::traits::LockError::*;
		ensure!(T::TrustedLockers::contains(&locker, &asset), NotTrusted);
		let amount = match asset.fun {
			Fungible(a) => a,
			NonFungible(_) => return Err(Unimplemented),
		};
		owner.remove_network_id();
		let account = T::SovereignAccountOf::convert_location(&owner).ok_or(BadOwner)?;
		let locker = locker.into();
		let owner = owner.into();
		let id: VersionedAssetId = asset.id.into();
		let key = (XCM_VERSION, account, id);
		let mut record =
			RemoteLockedFungibleRecord { amount, owner, locker, consumers: BoundedVec::default() };
		if let Some(old) = RemoteLockedFungibles::<T>::get(&key) {
			// Make sure that the new record wouldn't clobber any old data.
			ensure!(old.locker == record.locker && old.owner == record.owner, WouldClobber);
			record.consumers = old.consumers;
			record.amount = record.amount.max(old.amount);
		}
		RemoteLockedFungibles::<T>::insert(&key, record);
		Ok(())
	}
```

**File:** polkadot/xcm/pallet-xcm/src/lib.rs (L3797-3823)
```rust
	fn prepare_reduce_unlockable(
		locker: Location,
		asset: Asset,
		mut owner: Location,
	) -> Result<Self::ReduceTicket, xcm_executor::traits::LockError> {
		use xcm_executor::traits::LockError::*;
		let amount = match asset.fun {
			Fungible(a) => a,
			NonFungible(_) => return Err(Unimplemented),
		};
		owner.remove_network_id();
		let sovereign_account = T::SovereignAccountOf::convert_location(&owner).ok_or(BadOwner)?;
		let locker = locker.into();
		let owner = owner.into();
		let id: VersionedAssetId = asset.id.into();
		let key = (XCM_VERSION, sovereign_account, id);

		let record = RemoteLockedFungibles::<T>::get(&key).ok_or(NotLocked)?;
		// Make sure that the record contains what we expect and there's enough to unlock.
		ensure!(locker == record.locker && owner == record.owner, WouldClobber);
		ensure!(record.amount >= amount, NotEnoughLocked);
		ensure!(
			record.amount_held().map_or(true, |h| record.amount.saturating_sub(amount) >= h),
			InUse
		);
		Ok(ReduceTicket { key, amount, locker, owner })
	}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1713-1740)
```rust
			LockAsset { asset, unlocker } => {
				self.transactional_process(|self_ref| {
					let origin = self_ref.cloned_origin().ok_or(XcmError::BadOrigin)?;
					let (remote_asset, context) = Self::try_reanchor(asset.clone(), &unlocker)?;
					let lock_ticket =
						Config::AssetLocker::prepare_lock(unlocker.clone(), asset, origin.clone())?;
					let owner = origin.reanchored(&unlocker, &context).map_err(|e| {
						tracing::error!(target: "xcm::xcm_executor::process_instruction", ?e, ?unlocker, ?context, "Failed to re-anchor origin");
						XcmError::ReanchorFailed
					})?;
					let msg = Xcm::<()>(vec![NoteUnlockable { asset: remote_asset, owner }]);
					let (ticket, price) = validate_send::<Config::XcmSender>(unlocker, msg)?;
					self_ref.take_fee(price, FeeReason::LockAsset)?;
					lock_ticket.enact()?;
					Config::XcmSender::deliver(ticket)?;
					Ok(())
				})
			},
			UnlockAsset { asset, target } => {
				let origin = self.cloned_origin().ok_or(XcmError::BadOrigin)?;
				Config::AssetLocker::prepare_unlock(origin, asset, target)?.enact()?;
				Ok(())
			},
			NoteUnlockable { asset, owner } => {
				let origin = self.cloned_origin().ok_or(XcmError::BadOrigin)?;
				Config::AssetLocker::note_unlockable(origin, asset, owner)?;
				Ok(())
			},
```

**File:** polkadot/xcm/pallet-xcm/src/migration.rs (L337-350)
```rust
			for (old_key, new_key) in remote_locked_fungibles_keys_to_migrate {
				weight.saturating_accrue(T::DbWeight::get().reads(1));
				// make sure, that we don't override accidentally other data
				if RemoteLockedFungibles::<T>::get(&new_key).is_some() {
					tracing::error!(
						target: LOG_TARGET,
						?old_key,
						?new_key,
						"`RemoteLockedFungibles` already contains data for a `new_key`!"
					);
					// let's just skip for now, could be potentially caused with missing this
					// migration before (manual clean-up?).
					continue;
				}
```

**File:** polkadot/xcm/pallet-xcm/src/tests/mod.rs (L1606-1693)
```rust
		// `RemoteLockedFungibles` migration
		{
			let account1 = AccountId::new([13u8; 32]);
			let account2 = AccountId::new([58u8; 32]);
			let account3 = AccountId::new([97u8; 32]);
			let asset_id = VersionedAssetId::from(AssetId(Location::parent()));
			let owner = VersionedLocation::from(Location::parent());
			let locker = VersionedLocation::from(Location::parent());
			let key1_as_latest = (latest_version, account1, asset_id.clone());
			let key2_as_latest = (latest_version, account2, asset_id.clone());
			let key3_as_previous = (
				previous_version,
				account3.clone(),
				asset_id.clone().into_version(previous_version).unwrap(),
			);
			let expected_key3_as_latest = (latest_version, account3, asset_id);
			let data_as_latest = RemoteLockedFungibleRecord {
				amount: Default::default(),
				owner: owner.clone(),
				locker: locker.clone(),
				consumers: Default::default(),
			};
			let data_as_previous = RemoteLockedFungibleRecord {
				amount: Default::default(),
				owner: owner.into_version(previous_version).unwrap(),
				locker: locker.into_version(previous_version).unwrap(),
				consumers: Default::default(),
			};
			assert_ne!(data_as_latest.owner, data_as_previous.owner);
			assert_ne!(data_as_latest.locker, data_as_previous.locker);
			assert!(!key1_as_latest.needs_migration(latest_version));
			assert!(!key1_as_latest.needs_migration(previous_version));
			assert!(!key2_as_latest.needs_migration(latest_version));
			assert!(!key2_as_latest.needs_migration(previous_version));
			assert!(key3_as_previous.needs_migration(latest_version));
			assert!(!key3_as_previous.needs_migration(previous_version));
			assert!(!expected_key3_as_latest.needs_migration(latest_version));
			assert!(!expected_key3_as_latest.needs_migration(previous_version));
			assert!(!data_as_latest.needs_migration(latest_version));
			assert!(!data_as_latest.needs_migration(previous_version));
			assert!(data_as_previous.needs_migration(latest_version));
			assert!(!data_as_previous.needs_migration(previous_version));

			// store three lockeds:
			// fully migrated
			RemoteLockedFungibles::<Test>::insert(&key1_as_latest, data_as_latest.clone());
			// only key migrated
			RemoteLockedFungibles::<Test>::insert(&key2_as_latest, data_as_previous.clone());
			// neither key nor data migrated
			RemoteLockedFungibles::<Test>::insert(&key3_as_previous, data_as_previous);
			assert!(Pallet::<Test>::do_try_state().is_ok());

			// trigger migration
			Pallet::<Test>::migrate_data_to_xcm_version(&mut Weight::zero(), latest_version);

			let assert_locked_eq =
				|left: Option<RemoteLockedFungibleRecord<_, _>>,
				 right: Option<RemoteLockedFungibleRecord<_, _>>| {
					match (left, right) {
						(None, Some(_)) | (Some(_), None) => {
							assert!(false, "Received unexpected message")
						},
						(None, None) => (),
						(Some(l), Some(r)) => {
							assert_eq!(l.owner, r.owner);
							assert_eq!(l.locker, r.locker);
						},
					}
				};

			// no change
			assert_locked_eq(
				RemoteLockedFungibles::<Test>::get(&key1_as_latest),
				Some(data_as_latest.clone()),
			);
			// change - data migrated
			assert_locked_eq(
				RemoteLockedFungibles::<Test>::get(&key2_as_latest),
				Some(data_as_latest.clone()),
			);
			// fully migrated
			assert_locked_eq(RemoteLockedFungibles::<Test>::get(&key3_as_previous), None);
			assert_locked_eq(
				RemoteLockedFungibles::<Test>::get(&expected_key3_as_latest),
				Some(data_as_latest.clone()),
			);
			assert!(Pallet::<Test>::do_try_state().is_ok());
		}
```
