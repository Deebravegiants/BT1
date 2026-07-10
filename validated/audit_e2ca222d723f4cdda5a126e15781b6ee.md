### Title
Excess Attached Deposit Permanently Stuck in Contract on Existing-Participant Attestation Re-submission — (`File: crates/contract/src/lib.rs`)

---

### Summary

`submit_participant_info` is `#[payable]` but only performs a deposit check and refund when `attestation_storage_must_be_paid_by_caller` is `true`. When an **existing participant** re-submits or updates their attestation (the common operational case), that flag is `false`, the entire deposit-handling block is skipped, and any NEAR tokens attached to the call are silently absorbed by the contract with no refund path.

---

### Finding Description

In `crates/contract/src/lib.rs`, the `submit_participant_info` function computes a boolean guard:

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);

let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;
``` [1](#0-0) 

The deposit check and refund logic is gated entirely behind this flag:

```rust
if attestation_storage_must_be_paid_by_caller {
    // ... cost check ...
    // Refund the difference if the proposer attached more than required
    if let Some(diff) = attached.checked_sub(cost)
        && diff > NearToken::from_yoctonear(0)
    {
        Promise::new(account_id).transfer(diff).detach();
    }
}
``` [2](#0-1) 

When both conditions are `false` — i.e., the caller **is** an existing participant **and** the submission is an **update** (not a brand-new entry) — the flag is `false`, the `if` block is never entered, and any `attached_deposit()` is never returned. Because the function is `#[payable]`, NEAR allows any deposit to be attached; the runtime does not automatically refund it. [3](#0-2) 

The analogous pattern in the external report is the EVM `swap()` forwarding `msg.value` to the executor even when the input token is not native — here the contract accepts a deposit but provides no refund path for the common re-submission case.

---

### Impact Explanation

Any NEAR tokens attached by an existing participant when re-submitting their attestation (e.g., to rotate their TLS key or refresh an expiring quote) are permanently locked inside the MPC contract. There is no withdrawal function, no sweep mechanism, and no subsequent code path that returns the deposit. The funds are irretrievably lost to the caller.

This breaks the production accounting invariant that a `#[payable]` function must either consume exactly the required deposit or refund the surplus. It falls under:

> **Medium. Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants.**

---

### Likelihood Explanation

`submit_participant_info` is called by every MPC node on every TEE attestation refresh cycle (attestations expire and must be periodically renewed). All active participants are therefore existing participants re-submitting, making the vulnerable branch the **normal operational path**, not an edge case. Any caller who attaches even 1 yoctoNEAR (a common practice to satisfy full-access-key requirements or scripting defaults) loses that deposit permanently.

---

### Recommendation

Apply the same pattern used in `require_deposit` and `propose_update`: always refund any excess deposit, unconditionally, regardless of whether storage costs are charged to the caller.

```diff
-if attestation_storage_must_be_paid_by_caller {
     let storage_used = env::storage_usage().saturating_sub(initial_storage);
     let cost = env::storage_byte_cost().saturating_mul(storage_used as u128);
     let attached = env::attached_deposit();

+    if attestation_storage_must_be_paid_by_caller {
         if attached < cost {
             return Err(InvalidParameters::InsufficientDeposit {
                 attached: attached.as_yoctonear(),
                 required: cost.as_yoctonear(),
             }.into());
         }
+    }

     if let Some(diff) = attached.checked_sub(cost)
         && diff > NearToken::from_yoctonear(0)
     {
         Promise::new(account_id).transfer(diff).detach();
     }
-}
```

Alternatively, mirror the external report's fix and explicitly require zero deposit when no storage cost is owed:

```rust
if !attestation_storage_must_be_paid_by_caller {
    let attached = env::attached_deposit();
    if attached > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(attached).detach();
    }
}
```

---

### Proof of Concept

1. Node A is already a registered participant (`voter_account()` returns `Ok`).
2. Node A's TEE attestation is approaching expiry; it calls `submit_participant_info` with a fresh quote and attaches `1 yoctoNEAR` (standard practice).
3. `add_participant` returns `ParticipantInsertion::UpdatedParticipant` (not `NewlyInsertedParticipant`), so `is_new_attestation = false`.
4. `caller_is_not_participant = false` because Node A is a participant.
5. `attestation_storage_must_be_paid_by_caller = false || false = false`.
6. The `if attestation_storage_must_be_paid_by_caller` block is skipped entirely.
7. The 1 yoctoNEAR is never refunded; it remains in the contract balance with no recovery path. [4](#0-3) [2](#0-1)

### Citations

**File:** crates/contract/src/lib.rs (L758-760)
```rust
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
```

**File:** crates/contract/src/lib.rs (L817-824)
```rust
        let caller_is_not_participant = self.voter_account().is_err();
        let is_new_attestation = matches!(
            attestation_insertion_result,
            ParticipantInsertion::NewlyInsertedParticipant
        );

        let attestation_storage_must_be_paid_by_caller =
            is_new_attestation || caller_is_not_participant;
```

**File:** crates/contract/src/lib.rs (L826-849)
```rust
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
