## Analog Vulnerability Found

### Title
Stale Collection Role Permissions (Issuer/Admin/Freezer) Persist After `transfer_ownership` in `pallet-nfts` and `pallet-uniques` - (File: `substrate/frame/nfts/src/features/transfer.rs`, `substrate/frame/uniques/src/lib.rs`)

### Summary
The LUKSO finding describes an LSP6 `UP` where permissions set by a prior owner remain valid after ownership transfer because the smart contract has no mechanism to invalidate stale permission keys tied to old owners. The same pattern exists in Substrate's `pallet-nfts` (and its predecessor `pallet-uniques`): a collection's `owner` field can be transferred via `transfer_ownership`, but the collection's `Issuer`, `Admin`, and `Freezer` roles (stored in `CollectionRoleOf`, or `issuer`/`admin`/`freezer` fields in `uniques`) are never reset or invalidated during that transfer.

### Finding Description
`do_transfer_ownership` in `substrate/frame/nfts/src/features/transfer.rs` only mutates `details.owner`, moves the deposit, and updates `CollectionAccount`/`OwnershipAcceptance` bookkeeping: [1](#0-0) 

It never touches `CollectionRoleOf`, which stores the `Issuer`/`Admin`/`Freezer` roles set via `do_set_team`: [2](#0-1) 

Those roles carry significant capabilities that are independent of the `owner`:
- `Admin`: "can thaw items, force transfers and burn items from any account"
- `Issuer`: "can mint items"
- `Freezer`: "can freeze items" [3](#0-2) 

The same design exists in `pallet-uniques`: `transfer_ownership` moves only `owner`, leaving `issuer`, `admin`, and `freezer` fields on `CollectionDetails` unchanged: [4](#0-3) [5](#0-4) 

Just as in the LSP6 case where "universal" permission data keys are independent of the current owner and are never revoked on ownership change, `CollectionRoleOf`/`issuer`/`admin`/`freezer` are keyed by `collection`, not by `owner`, so a role assignment made under a previous owner remains fully valid under any subsequent owner.

### Impact Explanation
A malicious current owner (or the original creator) can call `set_team` (`pallet-nfts`) / `set_team` (`pallet-uniques`) to grant themselves (or a colluding account) the `Admin` role before transferring ownership via `transfer_ownership`/`set_accept_ownership`. After the transfer completes, the new owner believes they have full control of the collection, but the old owner retains `Admin` powers — force-transferring items out of any account in the collection, burning items, freezing items, or (as `Issuer`) minting new items diluting the collection — without the new owner's consent. This mirrors the LSP6 residual-permission "rug pull" pattern and was assessed as Medium severity there because it requires the new owner to trust that all prior permissions were cleared, which is not enforced at the protocol level.

### Likelihood Explanation
This is reachable by any unprivileged, signed account that creates or owns an NFT collection — no special privilege is required. The scenario requires an owner to transfer a valuable/established collection to a new party (e.g. via a marketplace-like flow using `set_accept_ownership`/`transfer_ownership`), which is an intended, exposed extrinsic path, not a mocked or admin-only flow. As with the original LUKSO finding, the exploit is conditional on the new owner not independently verifying (e.g. via `CollectionRoleOf` in an indexer) that no stale Issuer/Admin/Freezer roles remain, which is consistent with why the original bug was rated Medium rather than High.

### Recommendation
On `transfer_ownership` (and `force_collection_owner`), clear existing `CollectionRoleOf` entries (`Self::clear_roles(&collection)`) for `pallet-nfts`, and reset `issuer`/`admin`/`freezer` to the new owner (or to `None`/default) for `pallet-uniques`, unless the new owner explicitly re-authorizes the existing team via a fresh `set_team` call. Alternatively, expose a boolean flag on `transfer_ownership` (default `true`) to reset the team, mirroring the deposit/`OwnershipAcceptance` bookkeeping already performed in `do_transfer_ownership`.

### Proof of Concept
1. Account `A` calls `Nfts::create` and becomes `owner` of `collection = 0`.
2. `A` calls `Nfts::set_team(collection, issuer=Some(A), admin=Some(A), freezer=Some(A))`, giving itself all three roles (see `do_set_team`, [6](#0-5) ).
3. Account `B` calls `Nfts::set_accept_ownership(Some(0))`.
4. `A` calls `Nfts::transfer_ownership(0, B)` — `do_transfer_ownership` updates only `details.owner = B` ( [7](#0-6) ); `CollectionRoleOf` for `A` is untouched.
5. `B` believes it now fully controls collection `0`. However, `A` still holds `Admin`/`Issuer`/`Freezer` and can call `Nfts::mint`, `Nfts::force_mint`, `Nfts::burn` (via Admin's force-burn), or `Nfts::lock_item_properties`/freeze on items owned by `B` or third parties within the collection, without `B`'s authorization.

### Citations

**File:** substrate/frame/nfts/src/features/transfer.rs (L124-161)
```rust
	pub(crate) fn do_transfer_ownership(
		origin: T::AccountId,
		collection: T::CollectionId,
		new_owner: T::AccountId,
	) -> DispatchResult {
		// Check if the new owner is acceptable based on the collection's acceptance settings.
		let acceptable_collection = OwnershipAcceptance::<T, I>::get(&new_owner);
		ensure!(acceptable_collection.as_ref() == Some(&collection), Error::<T, I>::Unaccepted);

		// Try to retrieve and mutate the collection details.
		Collection::<T, I>::try_mutate(collection, |maybe_details| {
			let details = maybe_details.as_mut().ok_or(Error::<T, I>::UnknownCollection)?;
			// Check if the `origin` is the current owner of the collection.
			ensure!(origin == details.owner, Error::<T, I>::NoPermission);
			if details.owner == new_owner {
				return Ok(());
			}

			// Move the deposit to the new owner.
			T::Currency::repatriate_reserved(
				&details.owner,
				&new_owner,
				details.owner_deposit,
				Reserved,
			)?;

			// Update account ownership information.
			CollectionAccount::<T, I>::remove(&details.owner, &collection);
			CollectionAccount::<T, I>::insert(&new_owner, &collection, ());

			details.owner = new_owner.clone();
			OwnershipAcceptance::<T, I>::remove(&new_owner);
			frame_system::Pallet::<T>::dec_consumers(&new_owner);

			// Emit `OwnerChanged` event.
			Self::deposit_event(Event::OwnerChanged { collection, new_owner });
			Ok(())
		})
```

**File:** substrate/frame/nfts/src/features/roles.rs (L38-88)
```rust
	pub(crate) fn do_set_team(
		maybe_check_owner: Option<T::AccountId>,
		collection: T::CollectionId,
		issuer: Option<T::AccountId>,
		admin: Option<T::AccountId>,
		freezer: Option<T::AccountId>,
	) -> DispatchResult {
		Collection::<T, I>::try_mutate(collection, |maybe_details| {
			let details = maybe_details.as_mut().ok_or(Error::<T, I>::UnknownCollection)?;
			let is_root = maybe_check_owner.is_none();
			if let Some(check_origin) = maybe_check_owner {
				ensure!(check_origin == details.owner, Error::<T, I>::NoPermission);
			}

			let roles_map = [
				(issuer.clone(), CollectionRole::Issuer),
				(admin.clone(), CollectionRole::Admin),
				(freezer.clone(), CollectionRole::Freezer),
			];

			// only root can change the role from `None` to `Some(account)`
			if !is_root {
				for (account, role) in roles_map.iter() {
					if account.is_some() {
						ensure!(
							Self::find_account_by_role(&collection, *role).is_some(),
							Error::<T, I>::NoPermission
						);
					}
				}
			}

			let roles = roles_map
				.into_iter()
				.filter_map(|(account, role)| account.map(|account| (account, role)))
				.collect();

			let account_to_role = Self::group_roles_by_account(roles);

			// Delete the previous records.
			Self::clear_roles(&collection)?;

			// Insert new records.
			for (account, roles) in account_to_role {
				CollectionRoleOf::<T, I>::insert(&collection, &account, roles);
			}

			Self::deposit_event(Event::TeamChanged { collection, issuer, admin, freezer });
			Ok(())
		})
	}
```

**File:** substrate/frame/nfts/src/types.rs (L558-569)
```rust
/// Support for up to 8 different roles for collections.
#[bitflags]
#[repr(u8)]
#[derive(Copy, Clone, Debug, PartialEq, Eq, Encode, Decode, MaxEncodedLen, TypeInfo)]
pub enum CollectionRole {
	/// Can mint items.
	Issuer,
	/// Can freeze items.
	Freezer,
	/// Can thaw items, force transfers and burn items from any account.
	Admin,
}
```

**File:** substrate/frame/uniques/src/lib.rs (L866-904)
```rust
		#[pallet::call_index(11)]
		#[pallet::weight(T::WeightInfo::transfer_ownership())]
		pub fn transfer_ownership(
			origin: OriginFor<T>,
			collection: T::CollectionId,
			new_owner: AccountIdLookupOf<T>,
		) -> DispatchResult {
			let origin = ensure_signed(origin)?;
			let new_owner = T::Lookup::lookup(new_owner)?;

			let acceptable_collection = OwnershipAcceptance::<T, I>::get(&new_owner);
			ensure!(acceptable_collection.as_ref() == Some(&collection), Error::<T, I>::Unaccepted);

			Collection::<T, I>::try_mutate(collection.clone(), |maybe_details| {
				let details = maybe_details.as_mut().ok_or(Error::<T, I>::UnknownCollection)?;
				ensure!(origin == details.owner, Error::<T, I>::NoPermission);
				if details.owner == new_owner {
					return Ok(());
				}

				// Move the deposit to the new owner.
				T::Currency::repatriate_reserved(
					&details.owner,
					&new_owner,
					details.total_deposit,
					Reserved,
				)?;

				CollectionAccount::<T, I>::remove(&details.owner, &collection);
				CollectionAccount::<T, I>::insert(&new_owner, &collection, ());

				details.owner = new_owner.clone();
				OwnershipAcceptance::<T, I>::remove(&new_owner);
				frame_system::Pallet::<T>::dec_consumers(&new_owner);

				Self::deposit_event(Event::OwnerChanged { collection, new_owner });
				Ok(())
			})
		}
```

**File:** substrate/frame/uniques/src/types.rs (L39-62)
```rust
#[derive(Clone, Encode, Decode, Eq, PartialEq, Debug, TypeInfo, MaxEncodedLen)]
pub struct CollectionDetails<AccountId, DepositBalance> {
	/// Can change `owner`, `issuer`, `freezer` and `admin` accounts.
	pub owner: AccountId,
	/// Can mint tokens.
	pub issuer: AccountId,
	/// Can thaw tokens, force transfers and burn tokens from any account.
	pub admin: AccountId,
	/// Can freeze tokens.
	pub freezer: AccountId,
	/// The total balance deposited for the all storage associated with this collection.
	/// Used by `destroy`.
	pub total_deposit: DepositBalance,
	/// If `true`, then no deposit is needed to hold items of this collection.
	pub free_holding: bool,
	/// The total number of outstanding items of this collection.
	pub items: u32,
	/// The total number of outstanding item metadata of this collection.
	pub item_metadatas: u32,
	/// The total number of attributes for this collection.
	pub attributes: u32,
	/// Whether the collection is frozen for non-admin transfers.
	pub is_frozen: bool,
}
```
