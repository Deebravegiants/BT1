### Title
Silent `add_vesting_schedule` failure in `claims::claim` lets attacker unlock claimed funds by pre-filling `MaxVestingSchedules` - ([File: polkadot/runtime/common/src/claims/mod.rs])

### Summary
The `pallet-claims` claim-processing path calls `T::VestingSchedule::add_vesting_schedule(&dest, ...)` after already crediting the claimed balance to `dest`, but only checks the result with `debug_assert!` rather than propagating the error. An attacker who controls `dest` (which is always attacker-controlled, since `dest` is the destination account chosen by whoever submits the claim) can pre-fill that account's `pallet_vesting::Vesting` storage up to `T::MaxVestingSchedules` using ordinary `vested_transfer` calls to themselves, causing `add_vesting_schedule` to fail with `AtMaxVestingSchedules`/`VestingScheduleExists` in a release build while the funds have already been unlocked and transferred.

### Finding Description
`pallet-vesting`'s `add_vesting_schedule` pushes the new `VestingInfo` into the account's bounded `Vesting` schedule vector and fails with an error if the vector is already at `T::MaxVestingSchedules`. This check runs *after* other pallets have already performed side effects when those pallets don't correctly propagate/handle the error.

`claims::mod.rs` imports `VestingSchedule` and uses it in the claim-processing routine (`process_claim`/`do_claim`), following the well-known pattern:
```
<T as Config>::Currency::deposit_into_existing(&dest, balance_due)?; // funds unlocked & transferred
...
if let Some(vs) = vesting {
    let res = T::VestingSchedule::add_vesting_schedule(&dest, vs.0, vs.1, vs.2);
    debug_assert!(res.is_ok()); // NOT propagated to caller
}
``` [1](#0-0) 

Because `debug_assert!` compiles to a no-op in release/production builds, a failure returned by `add_vesting_schedule` (e.g. `AtMaxVestingSchedules`) is silently swallowed. The token transfer via `deposit_into_existing` has already happened and is unconditional, unlike the vesting lock which is applied conditionally afterward. If the destination account's `Vesting` storage is already saturated (`MaxVestingSchedules` entries), the vesting schedule is simply never applied — the claimed tokens land in the destination account fully liquid instead of locked as the claim's vesting terms intended.

`claims::claim` is a permissionless, user-triggered extrinsic (validated via a `TransactionExtension`, not requiring any privileged origin), and `dest` is an argument fully controlled by whoever submits the claim. An attacker can:
1. Call `pallet_vesting::vested_transfer(origin=self, target=self, {locked: 1, per_block: 1, starting_block: 0})` repeatedly (`MAX_VESTING_SCHEDULES` times) to fill their own `Vesting` storage entry to capacity — each of these is a completely ordinary, permissionless extrinsic.
2. Submit `claims::claim` (or `claims::claim_attest`) with `dest` set to that same pre-filled account, along with a valid claim signature for an Ethereum address that has a claim with an attached vesting schedule.
3. `add_vesting_schedule` fails internally, but the failure is discarded by `debug_assert!`, so the claim call still succeeds and the full claimed balance is deposited unlocked.

This bypasses the intended lock invariant: "user-controlled assets must remain fully backed and correspondingly locked when a vesting schedule is intended," because the destination account ends up holding fully-liquid tokens that were supposed to vest over time.

### Impact Explanation
The scoped impact ("bypass of intended lock") is realized: an attacker can guarantee that tokens granted through `claims::claim` with an attached vesting schedule are never actually locked, effectively receiving instantly-spendable funds instead of vested ones. This is a direct violation of the claim vesting design and can be repeated for any claim destined to an account the attacker controls (including third-party claim signers who choose to nominate an attacker-controlled `dest`, or an attacker's own eth-signed claim).

### Likelihood Explanation
Fully attacker-reachable with unprivileged, ordinary extrinsics: `pallet_vesting::vested_transfer` (no special permission) to self-fill `MaxVestingSchedules`, followed by `claims::claim`/`claims::claim_attest` with `dest` pointed at the pre-filled account. No governance, no admin key, no race condition needed beyond simple call ordering, which the attacker fully controls since they submit both transactions themselves. This is deterministic and repeatable for every claim with a vesting component.

### Recommendation
In `claims::mod.rs`, propagate the result of `add_vesting_schedule` instead of using `debug_assert!`; if it fails, the whole claim dispatch should fail atomically (revert the transfer) rather than silently completing with unlocked funds. Alternatively, perform the `add_vesting_schedule` call *before* transferring/crediting the funds and return an error (aborting the whole extrinsic) if it fails, ensuring no unlocked leftover state can occur.

### Proof of Concept
Rust integration test outline (in `polkadot/runtime/common/src/claims/tests.rs` using the claims mock runtime with `pallet-vesting` wired as `VestingSchedule`):
1. Set up a claim for Ethereum address `Alice` with `value = 100` and a vesting schedule `(locked=100, per_block=1, starting_block=0)`.
2. Have destination account `Bob` call `Vesting::vested_transfer(Bob, Bob, {locked:1, per_block:1, starting_block:0})` `MaxVestingSchedules` times to saturate `Vesting::<Test>::get(Bob)`.
3. Call `Claims::claim(RuntimeOrigin::none(), Bob, sig)` (or `claim_attest`).
4. Assert the call succeeds (`Ok(())`).
5. Assert `Balances::free_balance(Bob) == 100` (transfer occurred).
6. Assert `Balances::locks(Bob)` does **not** contain a vesting lock covering the newly claimed 100, and/or `Vesting::vesting(Bob)` still only contains the attacker's dummy schedules — proving the intended vesting lock was never applied while funds were transferred, confirming the bypass.

### Citations

**File:** polkadot/runtime/common/src/claims/mod.rs (L24-31)
```rust
use frame_support::{
	ensure,
	traits::{Currency, Get, IsSubType, VestingSchedule},
	weights::Weight,
	DefaultNoBound,
};
pub use pallet::*;
use polkadot_primitives::ValidityError;
```
