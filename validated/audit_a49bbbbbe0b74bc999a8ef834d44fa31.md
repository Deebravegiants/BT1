### Title
Attached Deposit Permanently Locked in `submit_participant_info` When Called by Existing Participant - (File: `crates/contract/src/lib.rs`)

---

### Summary

`submit_participant_info` is marked `#[payable]` and accepts NEAR deposits, but when an existing participant re-submits their attestation (an update rather than a new insertion), the deposit-handling branch is entirely skipped. Any NEAR tokens attached to the call are silently absorbed by the contract with no refund path and no accounting entry, permanently locking the caller's funds.

---

### Finding Description

`submit_participant_info` computes a boolean gate `attestation_storage_must_be_paid_by_caller`:

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);

let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... deposit check and excess refund
}
``` [1](#0-0) 

When the caller is an **existing participant** (`caller_is_not_participant == false`) and the attestation is an **update** (`is_new_attestation == false`), the entire `if` block is skipped. Because the function is `#[payable]`, the NEAR runtime does not reject an attached deposit; it is simply credited to the contract balance. No `pendingBalances`-style map, no refund promise, and no withdrawal function exist to recover it. [2](#0-1) 

The contract has no general-purpose withdrawal method. Once the deposit is absorbed, it is irrecoverable.

---

### Impact Explanation

Any NEAR tokens attached by an existing participant during an attestation update are permanently frozen inside the MPC contract. This directly matches the **Medium** allowed impact: *"Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants."* The contract's own balance is inflated by untracked deposits, and the caller's funds are unrecoverable without a contract upgrade.

---

### Likelihood Explanation

Existing participants are expected to call `submit_participant_info` periodically (e.g., after a TEE firmware upgrade or TLS key rotation). Because the function is `#[payable]`, tooling, scripts, or cautious operators may attach a small deposit to cover potential storage costs — a reasonable defensive practice. The NEAR SDK does not warn callers that their deposit will be silently discarded in the update path. The trigger condition (existing participant + re-submission) is the **normal operational path**, not an edge case.

---

### Recommendation

Add an unconditional refund of any attached deposit when `attestation_storage_must_be_paid_by_caller` is `false`:

```rust
} else {
    let attached = env::attached_deposit();
    if attached > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(attached).detach();
    }
}
```

Alternatively, remove `#[payable]` from `submit_participant_info` entirely and split it into two separate entry points — one for new participants (payable) and one for updates (non-payable). In NEAR, a non-payable function panics if any deposit is attached, which is the safest guard.

---

### Proof of Concept

1. Participant `alice.near` is already registered in the contract (`voter_account()` returns `Ok`).
2. Alice's TEE firmware is upgraded; she calls `submit_participant_info` with a new attestation quote and attaches `1 NEAR` to cover any storage delta.
3. Inside the function, `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant` (not `NewlyInsertedParticipant`).
4. `is_new_attestation = false`, `caller_is_not_participant = false` → `attestation_storage_must_be_paid_by_caller = false`.
5. The `if` block at line 826 is skipped; `env::attached_deposit()` is never read, no refund promise is created.
6. The function returns `Ok(())`. Alice's `1 NEAR` is now part of the contract's balance with no accounting entry and no way to retrieve it. [3](#0-2)

### Citations

**File:** crates/contract/src/lib.rs (L758-760)
```rust
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
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
