### Title
Excess Deposit Silently Consumed by Contract on Attestation Re-submission — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `submit_participant_info` function in `mpc-contract` is `#[payable]` and contains a conditional refund path. When an existing participant re-submits their attestation (not a new insertion), the function skips the deposit-check-and-refund block entirely. Any NEAR tokens attached to such a call are permanently locked in the contract with no refund issued to the caller.

---

### Finding Description

`submit_participant_info` computes a boolean gate to decide whether to enforce a deposit: [1](#0-0) 

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;
```

When `attestation_storage_must_be_paid_by_caller` is `false` — i.e., the caller **is** an existing participant **and** the submission is an update (not a new entry) — the entire deposit-handling block is skipped: [2](#0-1) 

```rust
if attestation_storage_must_be_paid_by_caller {
    // ...
    if let Some(diff) = attached.checked_sub(cost)
        && diff > NearToken::from_yoctonear(0)
    {
        Promise::new(account_id).transfer(diff).detach();  // refund only here
    }
}
```

Because the function is declared `#[payable]`, the NEAR runtime accepts any attached deposit unconditionally. When the `if` block is not entered, there is no code path that returns the attached tokens to the caller. The deposit is absorbed into the contract's balance permanently.

By contrast, the analogous deposit-handling helper `require_deposit` used by `sign`, `request_app_private_key`, and `verify_foreign_transaction` always refunds excess to `predecessor_account_id`: [3](#0-2) 

```rust
Some(diff) => {
    if diff > NearToken::from_yoctonear(0) {
        log!("refund excess deposit {diff} to {predecessor}");
        Promise::new(predecessor.clone()).transfer(diff).detach();
    }
}
```

The `submit_participant_info` re-submission path has no equivalent refund.

---

### Impact Explanation

Any NEAR tokens attached to a re-submission call by an existing participant are permanently locked in the contract. The contract's balance grows by the deposited amount with no corresponding state benefit, breaking the accounting invariant that excess deposits must be returned to callers. This constitutes a permanent, irreversible loss of the caller's funds — matching the **Medium** allowed impact: *"Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants."*

---

### Likelihood Explanation

The design document confirms that `mpc-node`'s `periodic_attestation_submission` task re-submits on a **1-hour cadence** and on attestation-removal events: [4](#0-3) 

Each periodic re-submission by an already-registered participant hits the `attestation_storage_must_be_paid_by_caller = false` branch. If the node attaches any deposit (e.g., a conservative buffer to cover potential storage growth), that deposit is silently consumed. Because the function is `#[payable]` with no documented "attach zero" requirement for re-submissions, node operators following the new-submission pattern will inadvertently lose funds on every update cycle.

---

### Recommendation

Add an unconditional refund of any excess deposit at the end of `submit_participant_info`, mirroring the pattern in `require_deposit`. The simplest fix is to move the refund outside the conditional block:

```rust
// After the conditional storage-payment block:
let attached = env::attached_deposit();
let cost = if attestation_storage_must_be_paid_by_caller { computed_cost } else { NearToken::from_yoctonear(0) };
if let Some(diff) = attached.checked_sub(cost)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(account_id).transfer(diff).detach();
}
```

Alternatively, reject any non-zero deposit when `attestation_storage_must_be_paid_by_caller` is `false`, so callers receive an explicit error rather than silently losing funds.

---

### Proof of Concept

1. Participant `alice.near` calls `submit_participant_info` for the first time, paying the required storage deposit. The entry is inserted; `is_new_attestation = true`; deposit is checked and excess refunded correctly.
2. One hour later, `alice.near`'s node re-submits (periodic cadence). The entry already exists; `is_new_attestation = false` and `caller_is_not_participant = false`, so `attestation_storage_must_be_paid_by_caller = false`.
3. The node attaches 1 mNEAR as a conservative buffer. The `if attestation_storage_must_be_paid_by_caller` block is skipped entirely.
4. The call succeeds. `alice.near`'s 1 mNEAR is now in the contract's balance with no refund scheduled.
5. This repeats every hour. Over time, the participant's funds are drained into the contract with no recovery path. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L134-138)
```rust
        Some(diff) => {
            if diff > NearToken::from_yoctonear(0) {
                log!("refund excess deposit {diff} to {predecessor}");
                Promise::new(predecessor.clone()).transfer(diff).detach();
            }
```

**File:** crates/contract/src/lib.rs (L817-849)
```rust
        let caller_is_not_participant = self.voter_account().is_err();
        let is_new_attestation = matches!(
            attestation_insertion_result,
            ParticipantInsertion::NewlyInsertedParticipant
        );

        let attestation_storage_must_be_paid_by_caller =
            is_new_attestation || caller_is_not_participant;

        if attestation_storage_must_be_paid_by_caller {
            // `saturating_sub`: if a re-submission shrinks the entry, charge nothing
            // rather than underflow. Intentional asymmetry: we do not refund freed bytes
            // either — the caller already paid for the larger entry, and we'd rather
            // accept that asymmetry than open a refund path for payload-shrinking games.
            let storage_used = env::storage_usage().saturating_sub(initial_storage);
            let cost = env::storage_byte_cost().saturating_mul(storage_used as u128);
            let attached = env::attached_deposit();

            if attached < cost {
                return Err(InvalidParameters::InsufficientDeposit {
                    attached: attached.as_yoctonear(),
                    required: cost.as_yoctonear(),
                }
                .into());
            }

            // Refund the difference if the proposer attached more than required
            if let Some(diff) = attached.checked_sub(cost)
                && diff > NearToken::from_yoctonear(0)
            {
                Promise::new(account_id).transfer(diff).detach();
            }
        }
```

**File:** docs/design/attestation-verifier-contract.md (L104-104)
```markdown
The only caller of `submit_participant_info` in production is `mpc-node`'s `periodic_attestation_submission` task, which resubmits on a 1-hour cadence and on attestation-removal events. It already polls contract state to confirm the attestation is actually stored, with exponential backoff (100 ms → 60 s, capped at 12 h). That polling-based success criterion is what makes the sync→async change transparent. Under yield-resume the returned `Promise` also resolves with the actual outcome — success, a verifier-rejection error, or a post-DCAP-failure error (each as soon as the verifier answers), or a timeout error after ~200 blocks if it never does — so any future caller that wants to await the result synchronously can, without changing the contract.
```
