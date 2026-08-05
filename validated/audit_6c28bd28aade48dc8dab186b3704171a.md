Audit Report

## Title
`pallet-assets::do_transfer_approved` Does Not Check the Delegate's `AccountStatus`, Allowing a Blocked Spender to Still Move Approved Funds - (File: `substrate/frame/assets/src/functions.rs`)

## Summary
`do_transfer_approved` only validates the `owner` and `destination` accounts' `AccountStatus` (via `transfer_and_die`), but never checks the delegate's own status. A delegate blocked via the `block()` extrinsic can still execute `transfer_approved` (or the ERC-20 `transferFrom` precompile path) using pre-existing approvals, fully bypassing the block mechanism.

## Finding Description
`pallet-assets` implements an account-level blacklist through `AccountStatus::Blocked`, set via the `block()` extrinsic which is restricted to the asset's `Freezer` [1](#0-0) [2](#0-1) . Ordinary transfers correctly enforce this status for both sender and receiver, confirmed by the pallet's own test suite [3](#0-2) . However, `do_transfer_approved` — reached from the permissionless `transfer_approved` extrinsic and from the `fungibles::approvals::Mutate::transfer_from` trait implementation used by the ERC-20 precompile in `pallet-revive` — only deducts from the approval and calls `transfer_and_die(id, owner, destination, amount, ...)`, which enforces `owner`'s and `destination`'s status but never inspects the delegate's own `AccountStatus` at all [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) .

This is a genuine gap: the existing tests only cover blocking the owner or the receiving account of a direct `transfer`, never the delegate's status in an approval-based transfer, confirming the missing check is not otherwise mitigated elsewhere in the code.

## Impact Explanation
A compliance/security actor (the asset's Freezer) blocking a compromised or malicious address expects that address to be fully restricted from moving any assets it can access. Because the delegate's status is never checked in `do_transfer_approved`, a blocked delegate retains the ability to drain any outstanding approvals granted to it prior to being blocked — undermining the compliance guarantee the block mechanism is designed to provide. Since `pallet-assets` underlies asset issuance on Asset Hub and other parachains, and the ERC-20 precompile `transferFrom` path is also affected, the impact is a genuine breach of an intended access-control invariant, not merely a theoretical inconsistency.

## Likelihood Explanation
The exploit requires no privilege escalation: any account that already holds approvals (a common occurrence in DeFi/collateral usage of `pallet-assets`) can, once blocked, call the permissionless `transfer_approved` extrinsic (or the analogous precompile `transferFrom`) to move funds using pre-existing approvals. The only precondition — pre-existing approvals before the block — is realistic and commonly satisfied.

## Recommendation
In `do_transfer_approved` (`substrate/frame/assets/src/functions.rs`), before executing the transfer, fetch the delegate's own `Account` entry and reject the call with `Error::<T, I>::Frozen` (or a dedicated blocked-error) if the delegate's `AccountStatus::is_blocked()` (or `is_frozen()`) returns true, mirroring the checks already applied to `owner` and `destination` inside `transfer_and_die`.

## Proof of Concept
1. Admin creates asset `0`; account `1` mints balance and approves account `3` (delegate) to spend `50` via `approve_transfer`.
2. Asset's Freezer calls `Assets::block(freezer_origin, 0, 3)`, blocking delegate `3`.
3. Delegate `3` (signed, unprivileged) calls `Assets::transfer_approved(RuntimeOrigin::signed(3), 0, 1, 2, 50)`.
4. Because `do_transfer_approved` never checks `3`'s own `AccountStatus`, the call succeeds and funds move from `1` to `2` despite `3` being blocked, contradicting the intent of `block()` and the existing owner/destination-only test coverage.

### Citations

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

**File:** substrate/frame/assets/src/tests.rs (L851-880)
```rust
#[test]
fn transferring_from_blocked_account_should_not_work() {
	build_and_execute(|| {
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), 0, 1, true, 1));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 1, 100));
		assert_eq!(Assets::balance(0, 1), 100);
		assert_ok!(Assets::block(RuntimeOrigin::signed(1), 0, 1));
		// behaves as frozen when transferring from blocked
		assert_noop!(Assets::transfer(RuntimeOrigin::signed(1), 0, 2, 50), Error::<Test>::Frozen);
		assert_ok!(Assets::thaw(RuntimeOrigin::signed(1), 0, 1));
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(1), 0, 2, 50));
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(2), 0, 1, 50));
	});
}

#[test]
fn transferring_to_blocked_account_should_not_work() {
	build_and_execute(|| {
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), 0, 1, true, 1));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 1, 100));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 2, 100));
		assert_eq!(Assets::balance(0, 1), 100);
		assert_eq!(Assets::balance(0, 2), 100);
		assert_ok!(Assets::block(RuntimeOrigin::signed(1), 0, 1));
		assert_noop!(Assets::transfer(RuntimeOrigin::signed(2), 0, 1, 50), TokenError::Blocked);
		assert_ok!(Assets::thaw(RuntimeOrigin::signed(1), 0, 1));
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(2), 0, 1, 50));
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(1), 0, 2, 50));
	});
}
```

**File:** substrate/frame/assets/src/functions.rs (L1012-1056)
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

		// Execute hook outside of `mutate`.
		if let Some(Remove) = owner_died {
			T::Freezer::died(id.clone(), owner);
			T::Holder::died(id, owner);
		}
		Ok(())
	}
```

**File:** substrate/frame/assets/src/impl_fungibles.rs (L310-332)
```rust
impl<T: Config<I>, I: 'static> fungibles::approvals::Mutate<<T as SystemConfig>::AccountId>
	for Pallet<T, I>
{
	// Approve spending tokens from a given account
	fn approve(
		asset: T::AssetId,
		owner: &<T as SystemConfig>::AccountId,
		delegate: &<T as SystemConfig>::AccountId,
		amount: T::Balance,
	) -> DispatchResult {
		Self::do_approve_transfer(asset, owner, delegate, amount)
	}

	fn transfer_from(
		asset: T::AssetId,
		owner: &<T as SystemConfig>::AccountId,
		delegate: &<T as SystemConfig>::AccountId,
		dest: &<T as SystemConfig>::AccountId,
		amount: T::Balance,
	) -> DispatchResult {
		Self::do_transfer_approved(asset, owner, delegate, dest, amount)
	}
}
```

**File:** substrate/frame/assets/precompiles/src/lib.rs (L434-468)
```rust
	/// Execute the transfer_from call.
	fn transfer_from(
		asset_id: <Runtime as Config<Instance>>::AssetId,
		call: &IERC20::transferFromCall,
		env: &mut impl Ext<T = Runtime>,
	) -> Result<Vec<u8>, Error> {
		env.charge(<Runtime as Config<Instance>>::WeightInfo::transfer_approved())?;
		let spender = Self::caller(env)?;
		let spender = <Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&spender);

		let from = call.from.into_array().into();
		let from = <Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&from);

		let to = call.to.into_array().into();
		let to = <Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&to);

		let approval_amount = Self::to_balance(call.value)?;
		pallet_assets::Pallet::<Runtime, Instance>::do_transfer_approved(
			asset_id,
			&from,
			&spender,
			&to,
			approval_amount,
		)?;

		Self::deposit_event(
			env,
			IERC20Events::Transfer(IERC20::Transfer {
				from: call.from,
				to: call.to,
				value: call.value,
			}),
		)?;

		Ok(IERC20::transferFromCall::abi_encode_returns(&true))
```
