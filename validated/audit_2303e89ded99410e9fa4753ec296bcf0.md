### Title
Stale item-level `approved` delegate is not revoked when a collection Admin is replaced via `set_team`, allowing continued unauthorized `transfer` calls - (File: `substrate/frame/uniques/src/lib.rs`)

### Summary
The reported DelegateToken bug is a two-tier approval model where a broad "operator" role can grant itself (or a colluding address) a narrow, per-token approval, and revoking the operator role does not revoke that narrow approval. `pallet-uniques` exhibits the same two-tier approval pattern: a collection `admin` (a broad, per-collection role) can grant itself a per-item `approved` delegate via `approve_transfer`, and later removing that account as `admin` via `set_team` does not clear the previously granted per-item `approved` entry.

### Finding Description
`approve_transfer` in `pallet-uniques` permits either the item `owner` **or the collection `admin`** to set `Item::approved` for an item: [1](#0-0) 

The collection `owner` can change who holds the `admin` role at any time via `set_team`, which only rewrites the `issuer`/`admin`/`freezer` fields on `Collection` storage and does not touch any `Item::approved` entries set while the old admin was in office: [2](#0-1) 

`transfer` allows the call to succeed if the caller is the item owner, the *current* collection admin, **or** matches the stale `details.approved` value: [3](#0-2) 

Attack scenario, directly analogous to the DelegateToken report:
1. Collection owner Alice sets Bob as `admin` via `set_team`.
2. Bob, while admin, calls `approve_transfer(collection, item, delegate = Bob)` (or any colluding address `X`), which succeeds because `check == collection_details.admin`.
3. Alice revokes Bob's admin role by calling `set_team` again with a different admin.
4. `Item::approved` for that item still equals Bob/`X` — nothing clears it on `set_team`.
5. Bob (or `X`) can still call `transfer(collection, item, dest)`. `details.owner != origin` and `collection_details.admin != origin` are both true, but `details.approved.take()==origin` matches, so the transfer succeeds.

The item owner never delegated anything to Bob directly — Bob delegated to himself while temporarily holding the broad `admin` role, and that specific/narrow permission survives the removal of the broad role, exactly mirroring the `setApprovalForAll` vs. `approve` disconnect in the original report.

### Impact Explanation
An item owner (or collection owner acting for the item owner) who removes a misbehaving/compromised admin has no built-in way to also purge approvals that admin self-granted; the stale delegate can still move the item out from under the (new) collection team's expectations. This is an access-control gap that can lead to unauthorized transfer of an NFT-like asset.

### Likelihood Explanation
Requires the specific sequence: owner grants admin → admin self-approves an item → owner revokes admin without separately calling `cancel_approval` for every item the admin touched. This is a realistic, permissionless-to-execute-by-the-admin scenario (the admin doesn't need any extra privilege beyond what was already granted), but it does depend on an owner action (granting/revoking admin) and does not affect `pallet-nfts` (the actively maintained successor), whose `do_approve_transfer` only allows the item **owner** (not a collection role) to approve: [4](#0-3) 

`pallet-uniques` is Substrate's legacy/simple NFT pallet, largely superseded by `pallet-nfts`; I could not verify from the available index whether `pallet-uniques` is still within the active bug-bounty scope (SECURITY.md contents were not available to me), which materially affects whether this qualifies as a submittable finding.

### Recommendation
When `set_team` changes the `admin` (or when `admin`/`issuer` roles are revoked), clear any `Item::approved` entries that were set by the outgoing admin, or restrict `approve_transfer` in `pallet-uniques` to the item owner only (mirroring `pallet-nfts`'s design) so that a transient collection role can never create a standing per-item approval that outlives the role itself.

### Proof of Concept
Using existing test scaffolding in `substrate/frame/uniques/src/tests.rs`, the following sequence demonstrates the issue conceptually (no such regression test currently exists in the repo):
```rust
// Alice owns collection 0, item 42 belongs to Alice.
assert_ok!(Uniques::set_team(RuntimeOrigin::signed(ALICE), 0, BOB, BOB, BOB)); // Bob becomes admin
assert_ok!(Uniques::approve_transfer(RuntimeOrigin::signed(BOB), 0, 42, BOB)); // Bob self-approves as admin
assert_ok!(Uniques::set_team(RuntimeOrigin::signed(ALICE), 0, CHARLIE, CHARLIE, CHARLIE)); // Bob removed as admin
// Item::approved is still Some(BOB) -- set_team never cleared it.
assert_ok!(Uniques::transfer(RuntimeOrigin::signed(BOB), 0, 42, EVE)); // succeeds despite Bob no longer being admin
``` [3](#0-2)

### Citations

**File:** substrate/frame/uniques/src/lib.rs (L658-665)
```rust
			Self::do_transfer(collection, item, dest, |collection_details, details| {
				if details.owner != origin && collection_details.admin != origin {
					let approved = details.approved.take().map_or(false, |i| i == origin);
					ensure!(approved, Error::<T, I>::NoPermission);
				}
				Ok(())
			})
		}
```

**File:** substrate/frame/uniques/src/lib.rs (L920-943)
```rust
		pub fn set_team(
			origin: OriginFor<T>,
			collection: T::CollectionId,
			issuer: AccountIdLookupOf<T>,
			admin: AccountIdLookupOf<T>,
			freezer: AccountIdLookupOf<T>,
		) -> DispatchResult {
			let origin = ensure_signed(origin)?;
			let issuer = T::Lookup::lookup(issuer)?;
			let admin = T::Lookup::lookup(admin)?;
			let freezer = T::Lookup::lookup(freezer)?;

			Collection::<T, I>::try_mutate(collection.clone(), |maybe_details| {
				let details = maybe_details.as_mut().ok_or(Error::<T, I>::UnknownCollection)?;
				ensure!(origin == details.owner, Error::<T, I>::NoPermission);

				details.issuer = issuer.clone();
				details.admin = admin.clone();
				details.freezer = freezer.clone();

				Self::deposit_event(Event::TeamChanged { collection, issuer, admin, freezer });
				Ok(())
			})
		}
```

**File:** substrate/frame/uniques/src/lib.rs (L967-995)
```rust
			let maybe_check: Option<T::AccountId> = T::ForceOrigin::try_origin(origin)
				.map(|_| None)
				.or_else(|origin| ensure_signed(origin).map(Some).map_err(DispatchError::from))?;

			let delegate = T::Lookup::lookup(delegate)?;

			let collection_details =
				Collection::<T, I>::get(&collection).ok_or(Error::<T, I>::UnknownCollection)?;
			let mut details =
				Item::<T, I>::get(&collection, &item).ok_or(Error::<T, I>::UnknownCollection)?;

			if let Some(check) = maybe_check {
				let permitted = check == collection_details.admin || check == details.owner;
				ensure!(permitted, Error::<T, I>::NoPermission);
			}

			details.approved = Some(delegate);
			Item::<T, I>::insert(&collection, &item, &details);

			let delegate = details.approved.expect("set as Some above; qed");
			Self::deposit_event(Event::ApprovedTransfer {
				collection,
				item,
				owner: details.owner,
				delegate,
			});

			Ok(())
		}
```

**File:** substrate/frame/nfts/src/features/approvals.rs (L64-66)
```rust
		if let Some(check_origin) = maybe_check_origin {
			ensure!(check_origin == details.owner, Error::<T, I>::NoPermission);
		}
```
