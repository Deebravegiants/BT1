This confirms the code as described in the claim. `do_transfer_approved` calls `transfer_and_die` with `owner` and `destination` only, and never inspects the `delegate`'s own `Account`/`AccountStatus` entry.Audit Report

## Title
`pallet-assets::do_transfer_approved` Does Not Check the Delegate's `AccountStatus`, Allowing a Blocked Spender to Still Move Approved Funds - (File: `substrate/frame/assets/src/functions.rs`)

## Summary
`do_transfer_approved` only checks the asset's overall status and consumes the `owner`→`delegate` approval, delegating balance-movement checks to `transfer_and_die`, which validates only the `owner` (source) and `destination` accounts. The `delegate`'s own `Account` entry and `AccountStatus` (in particular `Blocked`) is never consulted, so a delegate blocked by the asset's Freezer can still execute `transfer_approved` (or the `fungibles::approvals::Mutate::transfer_from`/ERC-20 `transferFrom` precompile path) using pre-existing approvals.

## Finding Description
`do_transfer_approved` reads the asset details, checks `AssetStatus::Live`, then mutates the `Approvals` map and calls `Self::transfer_and_die(id, owner, destination, amount, None, f)` [1](#0-0) . This function only takes `owner` and `destination` as the accounts whose balances/status are checked; the `delegate` parameter is used purely as a key into `Approvals` and never passed into any balance-mutation or status-check routine [2](#0-1) . `AccountStatus::Blocked` and `is_blocked()`/`is_frozen()` exist specifically to gate an account's ability to move assets [3](#0-2) , and `block()` is documented as disallowing "further unprivileged transfers of an asset id to and from an account" [4](#0-3) . This is reachable via the permissionless `transfer_approved` extrinsic [5](#0-4)  and via `fungibles::approvals::Mutate::transfer_from`, used e.g. by the ERC-20 `transferFrom` precompile [6](#0-5) .

I confirmed the current code in the repository matches these citations exactly — `do_transfer_approved` at lines 1012–1056 of `substrate/frame/assets/src/functions.rs` never reads `Account::<T,I>::get(id, delegate)` or checks the delegate's status before or during the transfer.

## Impact Explanation
An account blocked via the Freezer's `block()` extrinsic is expected to be fully cut off from moving any assets it can access, mirroring the checks the existing test suite validates only for `owner`/`destination` blocking (`transferring_from_blocked_account_should_not_work`, `transferring_to_blocked_account_should_not_work`) — neither test covers delegate blocking, confirming the gap is untested and unguarded. A delegate that is blocked after receiving approvals retains the ability to drain those approvals, moving funds from any consenting `owner` to any `destination`, which defeats the purpose of the blocking/compliance mechanism. This is a real, concrete authorization-bypass bug in an in-scope pallet (`pallet-assets`), not a theoretical one.

## Likelihood Explanation
Exploitation requires only: (1) an approval already exists from some `owner` to the `delegate` (a common DeFi/collateral pattern), and (2) the Freezer subsequently blocks the delegate. The delegate then simply calls the standard, permissionless `transfer_approved` extrinsic (or the ERC-20 `transferFrom` precompile) with no elevated privilege needed. This is straightforward and repeatable for any delegate address with standing approvals.

## Recommendation
In `do_transfer_approved`, before/within the transfer, load `Account::<T, I>::get(&id, delegate)` and reject with `Error::<T, I>::Frozen` (or a dedicated blocked-error) if `status.is_blocked()` (or `is_frozen()`), mirroring the checks already performed on `owner` and `destination` inside `transfer_and_die`/`can_decrease`.

## Proof of Concept
1. Create asset `0`; account `1` mints balance and calls `approve_transfer` to approve account `3` (delegate) to spend `50`.
2. The asset's Freezer calls `Assets::block(freezer_origin, 0, 3)`, setting delegate `3`'s `AccountStatus` to `Blocked`.
3. Delegate `3`, still able to sign transactions, calls `Assets::transfer_approved(RuntimeOrigin::signed(3), 0, 1, 2, 50)`.
4. Because `do_transfer_approved` never inspects `Account::<T, I>::get(&id, &3)`, the call succeeds and funds move from `1` to `2`, despite `3` being blocked — a unit test extending `transferring_from_blocked_account_should_not_work` to block the delegate rather than the owner would demonstrate the bypass.

### Citations

**File:** substrate/frame/assets/src/functions.rs (L1012-1048)
```rust
	pub fn do_transfer_approved(
		id: T::AssetId,
		owner: &T::AccountId,
		delegate: &T::AccountId,
		destination: &T::AccountId,
		amount: T::Balance,
	) -> DispatchResult {
		let mut owner_died: Option<DeadConsequence> = None;

		let d = Asset::<T, I>::get(&id).ok_or(Error::<T, I>::Unknown)?;
		ensure!(d.status == AssetStatus::Live, Error::<T, I>::AssetNotLive);

		Approvals::<T, I>::try_mutate_exists(
			(id.clone(), &owner, delegate),
			|maybe_approved| -> DispatchResult {
				let mut approved = maybe_approved.take().ok_or(Error::<T, I>::Unapproved)?;
				let remaining =
					approved.amount.checked_sub(&amount).ok_or(Error::<T, I>::Unapproved)?;

				let f = TransferFlags { keep_alive: false, best_effort: false, burn_dust: false };
				owner_died =
					Self::transfer_and_die(id.clone(), owner, destination, amount, None, f)?.1;

				if remaining.is_zero() {
					T::Currency::unreserve(owner, approved.deposit);
					Asset::<T, I>::mutate(id.clone(), |maybe_details| {
						if let Some(details) = maybe_details {
							details.approvals.saturating_dec();
						}
					});
				} else {
					approved.amount = remaining;
					*maybe_approved = Some(approved);
				}
				Ok(())
			},
		)?;
```

**File:** substrate/frame/assets/src/types.rs (L154-173)
```rust
/// The status of an asset account.
#[derive(Clone, Encode, Decode, Eq, PartialEq, Debug, MaxEncodedLen, TypeInfo)]
pub enum AccountStatus {
	/// Asset account can receive and transfer the assets.
	Liquid,
	/// Asset account cannot transfer the assets.
	Frozen,
	/// Asset account cannot receive and transfer the assets.
	Blocked,
}
impl AccountStatus {
	/// Returns `true` if frozen or blocked.
	pub fn is_frozen(&self) -> bool {
		matches!(self, AccountStatus::Frozen | AccountStatus::Blocked)
	}
	/// Returns `true` if blocked.
	pub fn is_blocked(&self) -> bool {
		matches!(self, AccountStatus::Blocked)
	}
}
```

**File:** substrate/frame/assets/src/lib.rs (L1706-1719)
```rust
		#[pallet::call_index(25)]
		pub fn transfer_approved(
			origin: OriginFor<T>,
			id: T::AssetIdParameter,
			owner: AccountIdLookupOf<T>,
			destination: AccountIdLookupOf<T>,
			#[pallet::compact] amount: T::Balance,
		) -> DispatchResult {
			let delegate = ensure_signed(origin)?;
			let owner = T::Lookup::lookup(owner)?;
			let destination = T::Lookup::lookup(destination)?;
			let id: T::AssetId = id.into();
			Self::do_transfer_approved(id, &owner, &delegate, &destination, amount)
		}
```

**File:** substrate/frame/assets/src/lib.rs (L1858-1893)
```rust
		/// Disallow further unprivileged transfers of an asset `id` to and from an account `who`.
		///
		/// Origin must be Signed and the sender should be the Freezer of the asset `id`.
		///
		/// - `id`: The identifier of the account's asset.
		/// - `who`: The account to be unblocked.
		///
		/// Emits `Blocked`.
		///
		/// Weight: `O(1)`
		#[pallet::call_index(31)]
		pub fn block(
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
					AccountStatus::Blocked;
				Ok(())
			})?;

			Self::deposit_event(Event::<T, I>::Blocked { asset_id: id, who });
			Ok(())
		}
```

**File:** substrate/frame/assets/src/impl_fungibles.rs (L322-331)
```rust

	fn transfer_from(
		asset: T::AssetId,
		owner: &<T as SystemConfig>::AccountId,
		delegate: &<T as SystemConfig>::AccountId,
		dest: &<T as SystemConfig>::AccountId,
		amount: T::Balance,
	) -> DispatchResult {
		Self::do_transfer_approved(asset, owner, delegate, dest, amount)
	}
```
