Audit Report

## Title
Unchecked `Currency::transfer` result in bounty payout silently swallowed by `debug_assert!`, causing permanent loss of bounty/child-bounty funds - (File: `substrate/frame/bounties/src/lib.rs`, `substrate/frame/child-bounties/src/lib.rs`)

## Summary
In `pallet-bounties::claim_bounty` and `pallet-child-bounties::claim_child_bounty`, the `T::Currency::transfer(...)` calls that pay out the curator fee and beneficiary payout have their `Result` checked only via `debug_assert!(res.is_ok())`, which compiles to a no-op in release builds. Immediately afterward the bounty/child-bounty storage record is unconditionally deleted, so a failed transfer under this pattern would be masked and the funds would become unrecoverable with no retry path.

## Finding Description
`claim_bounty` performs `T::Currency::transfer(&bounty_account, &curator, final_fee, AllowDeath)` and `T::Currency::transfer(&bounty_account, &beneficiary, payout, AllowDeath)`, storing each result in `res` and checking it only with `debug_assert!(res.is_ok())`. [1](#0-0) 
Regardless of the transfer outcome, the code then unconditionally clears bounty state via `*maybe_bounty = None`, removes `BountyDescriptions`, and emits `BountyClaimed`. [2](#0-1) 

The identical pattern exists in `claim_child_bounty`, where `fee_transfer_result` and `payout_transfer_result` are only checked with `debug_assert!`, followed by unconditional removal of the child-bounty record and description, and a `Claimed` event. [3](#0-2) [4](#0-3) 

Both dispatchables are permissionless (`ensure_signed(origin)?; // anyone can trigger claim`), reachable by any account once the bounty is `PendingPayout` and the unlock delay elapses. [5](#0-4) 

`debug_assert!` is compiled out in standard release builds (no `debug-assertions` flag), so if `Currency::transfer` returns `Err` for any reason (e.g., `pallet_balances`' existential-deposit rule that a transfer creating a new destination account below `ExistentialDeposit` fails regardless of the `ExistenceRequirement` passed, which only governs the sender side), the error is discarded and execution proceeds to delete the bounty/child-bounty record with no remaining code path to retry payment.

## Impact Explanation
If a payout transfer legitimately fails, the affected bounty or child-bounty record is deleted while the funds remain in the bounty sub-account with no dispatchable path to recover or retry the payment, and a misleading `BountyClaimed`/`Claimed` success event is emitted. This is a genuine loss-of-funds pattern class (same as the described MerkleVesting-style bug: state finalized as "success" without verifying the underlying transfer).

## Likelihood Explanation
The failure precondition is narrow and not fully attacker-controlled by an arbitrary unprivileged caller: `claim_bounty`/`claim_child_bounty` are callable by anyone, but the amounts and beneficiary that could trigger an ExistentialDeposit failure (a `payout` or `final_fee` below ED, paid to a brand-new zero-balance account) are determined earlier in the bounty lifecycle by the curator (via `propose_curator`'s fee) and by the bounty value approved through governance (`approve_bounty`), not by the account calling `claim_bounty` itself. This requires a specific and somewhat contrived configuration (a bounty/child-bounty whose net payout after fees is below the chain's `ExistentialDeposit`, paid to an account that has never held a balance) rather than being trivially triggerable by any user at will. It is a real, non-hypothetical edge case, but the "attacker" capability needed (choosing a very small residual payout and a fresh destination account) sits with the already-trusted curator/beneficiary-selection process, not a fully external/unprivileged party exploiting an otherwise-secure flow.

## Recommendation
Replace `debug_assert!(res.is_ok())` / `debug_assert!(fee_transfer_result.is_ok())` / `debug_assert!(payout_transfer_result.is_ok())` with proper error propagation (`?` or `ensure!`) so a failed transfer aborts the dispatchable via storage-transaction rollback instead of deleting bounty state unconditionally. Apply the same treatment to the `unreserve` result checks (`debug_assert!(err_amount.is_zero())`) for consistency, and consider guarding against ED-violating payouts explicitly (e.g., topping up to ED or rejecting the award) rather than relying on `transfer` to fail-safe.

## Proof of Concept
1. Governance proposes and approves a bounty (`propose_bounty` → `approve_bounty`) with a value only slightly above the fee that will be assigned.
2. Assign and accept a curator (`propose_curator`/`accept_curator`) with a fee such that `bounty.value - fee` (the `payout` to beneficiary) is below the chain's `ExistentialDeposit`.
3. Curator calls `award_bounty(bounty_id, beneficiary)` where `beneficiary` is a brand-new account with zero balance, moving status to `PendingPayout`.
4. Wait until `treasury_block_number() >= unlock_at`.
5. Any account calls `claim_bounty(bounty_id)` in a release build (no `debug-assertions`): `T::Currency::transfer(&bounty_account, &beneficiary, payout, AllowDeath)` returns `Err(Error::ExistentialDeposit)` because the destination account doesn't exist and the transferred amount is below ED; `debug_assert!` no-ops; `*maybe_bounty = None` deletes the bounty; `BountyClaimed` fires despite the beneficiary never receiving funds, with the residual balance stranded in the bounty sub-account and no further dispatchable referencing it.
6. Equivalent steps apply to `propose_curator`/`award_child_bounty`/`claim_child_bounty` in `pallet-child-bounties` for the analogous `Claimed` event and unconditional `*maybe_child_bounty = None`.

### Citations

**File:** substrate/frame/bounties/src/lib.rs (L796-807)
```rust
		pub fn claim_bounty(
			origin: OriginFor<T>,
			#[pallet::compact] bounty_id: BountyIndex,
		) -> DispatchResult {
			ensure_signed(origin)?; // anyone can trigger claim

			Bounties::<T, I>::try_mutate_exists(bounty_id, |maybe_bounty| -> DispatchResult {
				let bounty = maybe_bounty.take().ok_or(Error::<T, I>::InvalidIndex)?;
				if let BountyStatus::PendingPayout { curator, beneficiary, unlock_at } =
					bounty.status
				{
					ensure!(Self::treasury_block_number() >= unlock_at, Error::<T, I>::Premature);
```

**File:** substrate/frame/bounties/src/lib.rs (L820-826)
```rust
					let final_fee = fee.saturating_sub(children_fee);
					let res =
						T::Currency::transfer(&bounty_account, &curator, final_fee, AllowDeath); // should not fail
					debug_assert!(res.is_ok());
					let res =
						T::Currency::transfer(&bounty_account, &beneficiary, payout, AllowDeath); // should not fail
					debug_assert!(res.is_ok());
```

**File:** substrate/frame/bounties/src/lib.rs (L828-837)
```rust
					*maybe_bounty = None;

					BountyDescriptions::<T, I>::remove(bounty_id);
					T::ChildBountyManager::bounty_removed(bounty_id);

					Self::deposit_event(Event::<T, I>::BountyClaimed {
						index: bounty_id,
						payout,
						beneficiary,
					});
```

**File:** substrate/frame/child-bounties/src/lib.rs (L726-744)
```rust
						// Make payout to child-bounty curator.
						// Should not fail because curator fee is always less than bounty value.
						let fee_transfer_result = T::Currency::transfer(
							&child_bounty_account,
							curator,
							curator_fee,
							AllowDeath,
						);
						debug_assert!(fee_transfer_result.is_ok());

						// Make payout to beneficiary.
						// Should not fail.
						let payout_transfer_result = T::Currency::transfer(
							&child_bounty_account,
							beneficiary,
							payout,
							AllowDeath,
						);
						debug_assert!(payout_transfer_result.is_ok());
```

**File:** substrate/frame/child-bounties/src/lib.rs (L746-763)
```rust
						// Trigger the Claimed event.
						Self::deposit_event(Event::<T>::Claimed {
							index: parent_bounty_id,
							child_index: child_bounty_id,
							payout,
							beneficiary: beneficiary.clone(),
						});

						// Update the active child-bounty tracking count.
						ParentChildBounties::<T>::mutate(parent_bounty_id, |count| {
							count.saturating_dec()
						});

						// Remove the child-bounty description.
						ChildBountyDescriptionsV1::<T>::remove(parent_bounty_id, child_bounty_id);

						// Remove the child-bounty instance from the state.
						*maybe_child_bounty = None;
```
