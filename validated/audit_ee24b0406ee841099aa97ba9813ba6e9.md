### Title
Claims pallet skips vesting-capacity pre-check when destination already has active (non-fully-vested) schedules, allowing silent `add_vesting_schedule` failure to leave claimed funds fully liquid - (File: polkadot/runtime/common/src/claims/mod.rs)

### Summary
`Claims::process_claim` only runs the `T::VestingSchedule::can_add_vesting_schedule` pre-check when `T::VestingSchedule::vesting_balance(&dest)` returns `None`. If the destination account already has active, non-fully-vested schedules (exactly the state produced by filling `MaxVestingSchedules` via `pallet_vesting::vested_transfer`), this pre-check is skipped, and the actual `add_vesting_schedule` call later in the function is only checked with a `debug_assert!`, which is compiled out in release/production builds. This lets a claim's balance be deposited and the claim consumed while the intended vesting lock silently fails to attach.

### Finding Description
`process_claim` in `polkadot/runtime/common/src/claims/mod.rs` implements the flow: read `Vesting::<T>::get(&signer)`, conditionally pre-validate via `T::VestingSchedule::can_add_vesting_schedule`, then perform `Total::<T>::put`, `Claims::<T>::remove`, `Vesting::<T>::remove`, `CurrencyOf::<T>::deposit_creating(&dest, balance_due)`, and finally call `T::VestingSchedule::add_vesting_schedule(&dest, vs.0, vs.1, vs.2)`. [1](#0-0) 

The pre-check is gated by `if T::VestingSchedule::vesting_balance(&dest).is_none()`. This condition is true only when the destination currently has no *active/locked* vesting balance (e.g., a brand-new account, or one whose prior schedules already fully matured but haven't been cleaned up). It is false — and the pre-check is skipped — when the destination already has an active, non-fully-vested schedule, which is exactly the state an attacker reaches by exhausting `MaxVestingSchedules` slots through `pallet_vesting::vested_transfer` calls (a normal signed-user extrinsic path, `substrate/frame/vesting/src/lib.rs`). [2](#0-1) 

When the pre-check is skipped, execution proceeds unconditionally through `Claims::<T>::remove`/`Vesting::<T>::remove` and `CurrencyOf::<T>::deposit_creating`, crediting the claimed balance as fully liquid before the vesting schedule is applied. The subsequent `add_vesting_schedule` call internally does `schedules.try_push(...).map_err(...)?` and will return `Error::AtMaxVestingSchedules` if the account is already at `MaxVestingSchedules`. In `process_claim` this result is only checked via `debug_assert!(res.is_ok(), ...)`, which has no effect in a non-debug (production) runtime build — the `Err` is discarded and `process_claim` still returns `Ok(())`.

Because the currency deposit and storage removal (`Claims`, `Vesting`) already committed before the failed `add_vesting_schedule` call, and there is no rollback of the whole extrinsic on that failure, the attacker ends up with the full claimed balance credited and liquid, with no vesting lock ever attached.

### Impact Explanation
An unprivileged attacker permanently bypasses the intended vesting lock on a claims-based token grant, retaining the entire claimed balance as immediately transferable/liquid funds instead of a locked, linearly-vesting balance. This breaks the core invariant that a claim with `vesting_schedule = Some(..)` must always result in a correspondingly locked balance.

### Likelihood Explanation
Fully feasible with only unprivileged, real extrinsic calls:
1. Attacker calls `pallet_vesting::vested_transfer` (to self, from another account they control) `MaxVestingSchedules` times to fill their vesting schedule slots with active (non-fully-vested) schedules.
2. Attacker (or anyone) triggers `claims::claim`/`claims::claim_attest` for a claim tied to that account, where the claim has `vesting_schedule = Some(..)`.
3. `process_claim` sees `vesting_balance(&dest)` as `Some(nonzero)` (active schedules), skips `can_add_vesting_schedule`, deposits/removes claim state, then `add_vesting_schedule` fails internally with `AtMaxVestingSchedules`, silently discarded by `debug_assert!` in a release build.

This is fully repeatable and requires no privileged origin, no governance action, and no race condition — only ordinary account setup via public extrinsics.

### Recommendation
Remove the `vesting_balance(&dest).is_none()` gating condition and always run `can_add_vesting_schedule` (or an equivalent capacity check) before any state mutation whenever `vesting.is_some()`. Additionally, replace the `debug_assert!` on the final `add_vesting_schedule` call with a real error propagation guarded behind a `TransactionOutcome`/storage-transactional wrapper (or perform the currency deposit and storage removal only after `add_vesting_schedule` has already succeeded), so that any failure to attach the vesting schedule reverts the entire claim rather than leaving funds credited unlocked.

### Proof of Concept
Rust integration test in `polkadot/runtime/common/src/claims/tests.rs` (or an equivalent mock-runtime test):
1. For the attacker's account, call `Vesting::vested_transfer` `MaxVestingSchedules` times with small locked amounts and non-trivial `per_block` so schedules remain active (not fully vested) at the time of claim.
2. Set up a `Claims::Vesting` entry and `Claims::Claims` entry for the same account's Ethereum-linked signer, with `vesting_schedule = Some((locked, per_block, starting_block))` and a nonzero `balance_due`.
3. Call `Claims::claim` (or `claim_attest`) for that signer/account.
4. Assert either:
   - The whole call returns an `Err` and neither `Claims::Claims`/`Claims::Vesting` are mutated nor is the currency balance increased (expected safe behavior), **or**
   - If the call returns `Ok(())`, assert that `Balances::locks(&dest)` contains a vesting lock covering `balance_due` (i.e., vesting was actually applied).
5. In the current (vulnerable) code compiled in `release` profile (where `debug_assert!` is a no-op), the test will show: call returns `Ok(())`, `Balances::free_balance(&dest)` increased by `balance_due`, but `Balances::locks(&dest)` shows no corresponding vesting lock for the claimed amount — demonstrating the funds are fully liquid despite `vesting_schedule` being set, proving the bug.

### Citations

**File:** polkadot/runtime/common/src/claims/mod.rs (L1-1)
```rust
// Copyright (C) Parity Technologies (UK) Ltd.
```

**File:** substrate/frame/vesting/src/lib.rs (L1-1)
```rust
// This file is part of Substrate.
```
