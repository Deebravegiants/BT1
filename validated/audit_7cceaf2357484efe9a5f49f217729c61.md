### Title
Vesting-claim ED check in `process_claim` uses `saturating_add` over pre-existing free balance, allowing the pre-existing (unlocked) balance to be withdrawn afterwards and dust the account below ED, destroying the vesting-locked funds - ([File: polkadot/runtime/common/src/claims/mod.rs])

### Summary
`Pallet::process_claim` only guarantees that `free_balance(dest) + balance_due >= ExistentialDeposit` **at the moment of the claim**, by summing any pre-existing (unlocked) balance of `dest` with the newly claimed amount [1](#0-0) . If the pre-existing balance was what pushed the sum over ED while the newly deposited/vested amount alone is below ED, the account holder can legitimately withdraw that unlocked pre-existing balance afterwards (it is not covered by the `VestingSchedule` lock), collapsing the account's free balance under ED and triggering `pallet-balances` dust removal, which zeroes the account's free balance irrespective of any outstanding `Locks`. The "front-run mid-extrinsic" framing in the prompt is not itself valid (Substrate extrinsics execute atomically, so nothing can interleave between `deposit_creating` and `Total::<T>::put` inside `process_claim`), but the underlying ED-accounting flaw is real and reachable purely through normal, unprivileged extrinsics.

### Finding Description
`process_claim` performs the ED-safety check for vesting claims as:
```rust
let free_after = CurrencyOf::<T>::free_balance(&dest).saturating_add(balance_due);
ensure!(
    free_after >= CurrencyOf::<T>::minimum_balance(),
    Error::<T>::ClaimBelowExistentialDeposit,
);
``` [2](#0-1) 

This check adds `dest`'s *current, unlocked* free balance to the incoming `balance_due` and only requires the **sum** to clear ED. It then deposits the funds and installs the vesting lock via `T::VestingSchedule::add_vesting_schedule` [3](#0-2) . The lock applies only to the vested amount (`vs.0`/`vs.1`/`vs.2`), not to whatever pre-existing balance `dest` already held before the claim.

Exploit flow (fully reachable via ordinary signed extrinsics, no privileged calls required after the out-of-scope `mint_claim`):
1. `dest` (an account the claimant/attacker controls) holds a small pre-existing free balance `P` that is below ED on its own, but `P + balance_due >= ED` while `balance_due` itself (or the vested lock amount `vs.0`) is below ED.
2. Claimant calls `claim`/`claim_attest`/`attest`, which dispatches to `Self::process_claim(signer, dest)` [4](#0-3) [5](#0-4) [6](#0-5) . The ED check passes because it evaluates `P + balance_due`, not `balance_due` alone. `deposit_creating` mints `balance_due` into `dest`, and `add_vesting_schedule` installs a lock over the newly minted (or intended) vested amount.
3. `dest` then submits an ordinary `pallet_balances::transfer_allow_death` sending away `P` (the still-unlocked portion). This withdrawal is permitted by `ensure_can_withdraw` because the resulting balance (`vs.0`, the locked amount) is `>= frozen_balance` — the lock is not breached by this specific transfer.
4. Because the resulting free balance (`vs.0`) is `< ExistentialDeposit`, `pallet-balances`' post-mutation dust-removal logic zeroes the account's *entire* remaining free balance and reaps the account — this sweep does not consult `Locks`, since dust removal is unconditional once free balance drops under ED. The vesting-locked tokens are destroyed/swept even though a `VestingSchedule` lock nominally protected them.
5. `Vesting`/underlying vesting-pallet schedule entries referencing the now-dead account become orphaned, and the funds are permanently lost to the claimant (dust is typically burned or redirected, not returned).

The pallet's own comment acknowledges the ED-liveness requirement for vesting locks (`"A vesting schedule installs a balance lock, which requires the account to stay alive, otherwise it is dusted..."`) but the implemented check only enforces this transiently at claim time by mixing in unlocked pre-existing funds, not durably for the locked amount itself.

### Impact Explanation
This matches the scoped impact: permanent loss/freeze of the claimed vesting funds. The vesting-locked tokens, which the check is explicitly meant to protect from being dusted on a non-existent account, can still be destroyed by a completely ordinary follow-up `transfer_allow_death` from the account owner, because the guarantee in `process_claim` is computed over a sum that includes fungible, freely-movable pre-existing balance rather than the durable locked amount alone.

### Likelihood Explanation
Requires: (a) a vesting claim (`mint_claim` with `vesting_schedule = Some(...)`, root-privileged and out of scope, but a normal part of the claims pallet's intended usage on-chain), where the vested amount is small (below ED) or `balance_due` is small; and (b) `dest` already holding a small unlocked balance that only barely tops the combined amount over ED. Given claims can legitimately be small (SAFT/partial claims, or a claim reduced via `move_claim` splitting), and `dest` accounts commonly hold small residual balances, this is a plausible, repeatable, purely user-triggered sequence (`claim`/`claim_attest`/`attest` followed by a normal `transfer_allow_death`) requiring no forged signatures or origin bypass.

### Recommendation
Change the ED check in `process_claim` to validate the vested/locked amount's durability independent of any pre-existing unlocked balance — e.g., require that the amount being locked by the vesting schedule (`vs.0`, or `balance_due` if the whole claim is vested) alone is `>= ExistentialDeposit`, or alternatively require that `free_balance(dest)` after subtracting anything that remains freely transferable (i.e., the locked amount alone) stays `>= ExistentialDeposit`, so that the guarantee holds even after the pre-existing free portion is later moved out.

### Proof of Concept
Rust integration test (in `polkadot/runtime/common/src/claims/tests.rs` or a new test module):
```rust
#[test]
fn vesting_claim_can_be_dusted_by_prior_balance_withdrawal() {
    new_test_ext().execute_with(|| {
        // Preconditions: `mint_claim` with a vesting schedule whose vested amount (vs.0)
        // is below ExistentialDeposit, and `dest` (AccountId `42`) already holds a small
        // unlocked balance P such that P + balance_due >= ED but balance_due < ED.
        let ed = <Test as pallet_balances::Config>::ExistentialDeposit::get();
        let balance_due = ed / 2; // vested amount below ED
        let p = ed - balance_due + 1; // pre-existing unlocked balance
        Balances::make_free_balance_be(&42, p);

        assert_ok!(Claims::mint_claim(
            RawOrigin::Root.into(),
            eth(&alice()),
            balance_due,
            Some((balance_due, balance_due, 0)), // fully vested lock == balance_due
            None,
        ));

        // Claim succeeds because P + balance_due >= ED.
        assert_ok!(Claims::claim(RawOrigin::None.into(), 42, sig::<Test>(&alice(), &42u64.encode(), &[][..])));
        assert!(Balances::free_balance(&42) >= ed);

        // Attacker-controlled dest withdraws the pre-existing unlocked portion `p`.
        assert_ok!(Balances::transfer_allow_death(RawOrigin::Signed(42).into(), 43, p));

        // BUG: account is dusted/reaped even though a VestingSchedule lock still nominally
        // exists over `balance_due`, violating the invariant that a VestingSchedule lock
        // must not be dusted below ED by the depositing flow.
        assert_eq!(Balances::free_balance(&42), 0);
        assert!(!frame_system::Pallet::<Test>::account_exists(&42));
    });
}
```
Expected (buggy) result: the assertions at the end pass, proving the account holding an active `VestingSchedule` lock was reaped/dusted to zero, i.e. `process_claim`'s ED check did not provide a durable guarantee for the vesting-locked funds.

### Citations

**File:** polkadot/runtime/common/src/claims/mod.rs (L342-356)
```rust
		pub fn claim(
			origin: OriginFor<T>,
			dest: T::AccountId,
			ethereum_signature: EcdsaSignature,
		) -> DispatchResult {
			ensure_none(origin)?;

			let data = dest.using_encoded(to_ascii_hex);
			let signer = Self::eth_recover(&ethereum_signature, &data, &[][..])
				.ok_or(Error::<T>::InvalidEthereumSignature)?;
			ensure!(Signing::<T>::get(&signer).is_none(), Error::<T>::InvalidStatement);

			Self::process_claim(signer, dest)?;
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/claims/mod.rs (L423-439)
```rust
		pub fn claim_attest(
			origin: OriginFor<T>,
			dest: T::AccountId,
			ethereum_signature: EcdsaSignature,
			statement: Vec<u8>,
		) -> DispatchResult {
			ensure_none(origin)?;

			let data = dest.using_encoded(to_ascii_hex);
			let signer = Self::eth_recover(&ethereum_signature, &data, &statement)
				.ok_or(Error::<T>::InvalidEthereumSignature)?;
			if let Some(s) = Signing::<T>::get(signer) {
				ensure!(s.to_text() == &statement[..], Error::<T>::InvalidStatement);
			}
			Self::process_claim(signer, dest)?;
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/claims/mod.rs (L466-475)
```rust
		pub fn attest(origin: OriginFor<T>, statement: Vec<u8>) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let signer = Preclaims::<T>::get(&who).ok_or(Error::<T>::SenderHasNoClaim)?;
			if let Some(s) = Signing::<T>::get(signer) {
				ensure!(s.to_text() == &statement[..], Error::<T>::InvalidStatement);
			}
			Self::process_claim(signer, who.clone())?;
			Preclaims::<T>::remove(&who);
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/claims/mod.rs (L605-613)
```rust
			// A vesting schedule installs a balance lock, which requires the account to stay alive,
			// otherwise it is dusted and the lock placed on a non-existent account. The `dest` may
			// already hold funds, so a small claim that tops an existing account over the ED is
			// valid.
			let free_after = CurrencyOf::<T>::free_balance(&dest).saturating_add(balance_due);
			ensure!(
				free_after >= CurrencyOf::<T>::minimum_balance(),
				Error::<T>::ClaimBelowExistentialDeposit,
			);
```

**File:** polkadot/runtime/common/src/claims/mod.rs (L616-625)
```rust
		// We first need to deposit the balance to ensure that the account exists.
		let _ = CurrencyOf::<T>::deposit_creating(&dest, balance_due);

		// Check if this claim should have a vesting schedule.
		if let Some(vs) = vesting {
			// This can only fail if the account already has a vesting schedule or its balance is
			// below the existential deposit, both of which are checked above.
			T::VestingSchedule::add_vesting_schedule(&dest, vs.0, vs.1, vs.2)
				.map_err(|_| Error::<T>::VestedBalanceExists)?;
		}
```
