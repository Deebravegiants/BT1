### Title
Purchase pallet `payout` transfers locked funds as fully liquid balance when `VestingSchedule::add_vesting_schedule` fails, while still marking the account `Completed` - (File: polkadot/runtime/common/src/purchase/mod.rs)

### Finding Description
`Pallet::payout` is gated by `T::ValidityOrigin::ensure_origin(origin)`, so only a privileged validity-origin account can invoke it directly. However, the state it acts on can be manipulated beforehand by any unprivileged user through the public `pallet_vesting::vested_transfer` extrinsic, which lets anyone send a vesting schedule to an arbitrary destination account with no origin restriction on the receiver.

In `payout`, the total amount `free_balance + locked_balance` is transferred to `who` via `T::Currency::transfer` unconditionally, and only afterward does the code attempt `T::VestingSchedule::add_vesting_schedule(...)` for the locked portion, discarding the result with `let _ = ...`. The vesting pallet's `add_vesting_schedule` enforces a bounded number of concurrent schedules per account (`MaxVestingSchedules`), returning an error (in current substrate this is `Error::AtMaxVestingSchedules`, not literally `VestedBalanceExists` as worded in the question, but functionally equivalent — an existing/conflicting vesting state causes the call to fail) when the account already holds the maximum number of schedules. If an unprivileged third party front-runs the admin's `payout` call with a `vested_transfer` to `who` that fills up `who`'s available vesting-schedule slots, the subsequent `add_vesting_schedule` call inside `payout` fails silently. Because the error is swallowed, `payout` proceeds to set `status.validity = AccountValidity::Completed` and returns `Ok(())`, even though the locked portion of the purchase was never placed under a lock — it is already sitting as fully liquid, transferred balance in `who`'s account.

This is a real logic/accounting error: the pallet's core invariant (the locked portion of a DOT purchase must always end up under a vesting lock) is not enforced when `add_vesting_schedule` fails, and failure is deliberately ignored rather than causing `payout` to abort or retry.

### Impact Explanation
An account can end up receiving the full "locked" purchase amount as immediately spendable balance instead of vesting-locked balance, breaking the accounting invariant that purchase-locked DOT must remain locked until the vesting schedule unlocks. This is an unbacked/early release of value relative to the pallet's documented guarantee, even though total currency issuance is unaffected (it's a lock-bypass, not new-money-creation, bug).

### Likelihood Explanation
Exploitability depends on: (1) an unprivileged user being able to pre-fill the target's vesting schedule slots via `vested_transfer` before the privileged `payout` call executes, and (2) `payout` being called by the `ValidityOrigin` afterward, which the attacker does not control the timing of but can influence via mempool/extrinsic ordering within the same block, since `create_account`, `update_validity_status`, `update_balance`, and `payout` are separate, unbatched calls typically executed as separate extrinsics/blocks by the admin. Because the purchase process is a one-time, now-retired module used only for the original DOT token sale, real-world exploitability is essentially nil today, but the code path itself is logically unsound and would be exploitable in any redeployment of this pallet with an active `ValidityOrigin` workflow.

### Recommendation
- Do not silently ignore the result of `add_vesting_schedule`. If it fails, either abort the whole `payout` (return an error, not transferring anything) or only transfer `free_balance` and keep `locked_balance` in the purchase pallet's account until a vesting schedule can be successfully applied.
- Alternatively, transfer the free balance first, and only transfer the locked balance if `add_vesting_schedule` succeeds; if it fails, do not mark the account `Completed`, and expose a separate retry mechanism.

### Proof of Concept
Extend the existing `payout_works` test in `polkadot/runtime/common/src/purchase/tests.rs`:
1. Set up `Purchase::create_account`, `update_validity_status(ValidHigh)`, `update_balance(free, locked)` for account `who`, as in the existing test.
2. Before calling `Purchase::payout`, have a colluding unprivileged account call `Vesting::vested_transfer` (or repeatedly, to hit `MaxVestingSchedules`) targeting `who`, filling its vesting schedule slots with an unrelated dummy schedule.
3. Call `Purchase::payout(validity_origin, who)`.
4. Assert:
   - `Balances::free_balance(who)` increased by `free_balance + locked_balance` (full amount, matching current buggy behavior).
   - `Vesting::vesting_balance(&who)` does NOT reflect the purchase's `locked_balance` (only the pre-existing dummy schedule, or `None`), proving the lock was never applied.
   - `Purchase::accounts(who).validity == AccountValidity::Completed` despite the lock failure — confirming the invariant break (locked funds ended up fully liquid while the pallet believes payout succeeded normally).