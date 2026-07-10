### Title
`submit_participant_info()` Silently Absorbs Excess Deposit When Existing Participant Re-Submits Attestation - (File: `crates/contract/src/lib.rs`)

---

### Summary

`submit_participant_info` is marked `#[payable]` and contains a deposit-check-and-refund block, but that block is gated behind a boolean flag. When an existing participant re-submits their attestation (an update, not a new insertion), the flag evaluates to `false`, the entire block is skipped, and any attached deposit is permanently absorbed by the contract with no refund.

---

### Finding Description

`submit_participant_info` computes whether the caller must pay for storage:

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);

let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;
``` [1](#0-0) 

The deposit check and refund logic only execute inside the `if attestation_storage_must_be_paid_by_caller` block:

```rust
if attestation_storage_must_be_paid_by_caller {
    // ...
    // Refund the difference if the proposer attached more than required
    if let Some(diff) = attached.checked_sub(cost)
        && diff > NearToken::from_yoctonear(0)
    {
        Promise::new(account_id).transfer(diff).detach();
    }
}
``` [2](#0-1) 

When `attestation_storage_must_be_paid_by_caller` is `false` — i.e., the caller **is** an existing participant **and** the insertion result is `UpdatedExistingParticipant` — the block is entirely skipped. The function returns `Ok(())` successfully, and `env::attached_deposit()` is never read, checked, or refunded. Any NEAR tokens attached to the call are permanently locked in the contract.

The function is unconditionally `#[payable]`, so the NEAR runtime accepts any deposit without restriction: [3](#0-2) 

By contrast, every other payable entry point (`sign`, `request_app_private_key`, `verify_foreign_transaction`, `propose_update`) either calls `require_deposit` (which always refunds excess) or has its own explicit refund path. `submit_participant_info` is the only function where a successful call can silently absorb an arbitrary deposit.

---

### Impact Explanation

**Medium.** This breaks the balance/accounting invariant of the contract. Any NEAR tokens attached to a re-submission call by an existing participant are permanently locked — there is no withdrawal function, no sweep mechanism, and no administrative recovery path. The contract's NEAR balance grows by the excess, and the caller's balance shrinks by the same amount, with no protocol benefit. This matches the allowed medium impact: *"Balance … manipulation that breaks production safety/accounting invariants."*

---

### Likelihood Explanation

**Low-Medium.** The vulnerable path requires the caller to be an already-registered participant **and** to attach a non-zero deposit during a re-submission. Participants re-submit attestations periodically (e.g., after TEE upgrades). A participant who mistakenly attaches a deposit — or who is scripted to always attach 1 yoctoNEAR as a "safety deposit" following the pattern documented for `sign` — will silently lose those funds on every re-submission. Because the README documents that "any excess deposit is automatically refunded" for user-facing calls, a participant may reasonably expect the same behaviour here.

---

### Recommendation

Add an unconditional refund for any excess deposit at the end of `submit_participant_info`, mirroring the pattern used in `require_deposit` and `propose_update`:

```rust
// After the attestation_storage_must_be_paid_by_caller block:
let attached = env::attached_deposit();
let cost = if attestation_storage_must_be_paid_by_caller { cost } else { NearToken::from_yoctonear(0) };
if let Some(diff) = attached.checked_sub(cost)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(account_id).transfer(diff).detach();
}
```

Alternatively, restructure the function so that `env::attached_deposit()` is always read and any amount above the computed `cost` (which is zero when `attestation_storage_must_be_paid_by_caller` is false) is always refunded, regardless of the flag.

---

### Proof of Concept

1. Participant `alice.near` is already registered in the contract (`voter_account()` returns `Ok`).
2. `alice.near` calls `submit_participant_info` with a fresh attestation and attaches `1_000_000_000_000_000_000_000_000` yoctoNEAR (1 NEAR).
3. `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant` (re-submission).
4. `caller_is_not_participant = false`, `is_new_attestation = false` → `attestation_storage_must_be_paid_by_caller = false`.
5. The deposit block is skipped entirely; the function returns `Ok(())`.
6. The 1 NEAR is now held by the contract with no mechanism to recover it.
7. `alice.near`'s balance is permanently reduced by 1 NEAR. [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L758-760)
```rust
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
```

**File:** crates/contract/src/lib.rs (L817-851)
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

        Ok(())
```
