### Title
Attached NEAR Deposit Permanently Locked in `MpcContract` When Existing Participant Re-submits Attestation — (`File: crates/contract/src/lib.rs`)

---

### Summary

`submit_participant_info` is marked `#[payable]` and accepts an attached NEAR deposit. The refund path is only entered when `attestation_storage_must_be_paid_by_caller` is `true`. When an **existing participant** re-submits or updates their attestation, both conditions that set that flag are `false`, so the entire refund block is skipped. Any NEAR tokens attached to such a call are permanently locked in the contract with no recovery path.

---

### Finding Description

In `crates/contract/src/lib.rs`, the `submit_participant_info` function computes whether the caller must pay for storage:

```rust
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);

let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... refund excess deposit here ...
}
``` [1](#0-0) 

When an **already-registered participant** re-submits their attestation (e.g., to refresh an expiring TEE quote), `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant`, making `is_new_attestation = false`. Since the caller is already a participant, `caller_is_not_participant = false` as well. The combined flag is `false`, so the `if` block — which contains the only refund logic — is never entered. [2](#0-1) 

The function is still declared `#[payable]`, so the NEAR runtime accepts any attached deposit without complaint. The deposit is credited to the contract account and there is no withdrawal or sweep mechanism. [3](#0-2) 

---

### Impact Explanation

Any NEAR tokens attached to a re-submission call by an existing participant are permanently frozen inside the `MpcContract`. There is no admin withdrawal function, no sweep, and no later refund path. This matches the **Medium** allowed impact: *balance/accounting invariant broken without relying on network-level DoS or operator misconfiguration*.

---

### Likelihood Explanation

Existing MPC participants must periodically re-submit attestations when their TEE quote expires or when they upgrade their node image. This is a routine, expected operation. A participant who attaches even 1 yoctoNEAR (e.g., by habit, scripting error, or wallet default) will silently lose those funds. The scenario requires no adversary — it is triggered by normal participant maintenance.

---

### Recommendation

Add an unconditional refund of any excess deposit at the end of `submit_participant_info`, regardless of whether storage was charged:

```rust
// After the storage-payment block, always refund any unspent deposit
let attached = env::attached_deposit();
let cost_charged = if attestation_storage_must_be_paid_by_caller { cost } else { NearToken::from_yoctonear(0) };
if let Some(diff) = attached.checked_sub(cost_charged) {
    if diff > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(diff).detach();
    }
}
```

Alternatively, assert `env::attached_deposit() == NearToken::from_yoctonear(0)` when `attestation_storage_must_be_paid_by_caller` is `false`, so the call reverts rather than silently absorbing funds.

---

### Proof of Concept

1. Participant `alice.near` is already registered in the contract (returned `NewlyInsertedParticipant` on first call).
2. Alice's TEE quote expires; she calls `submit_participant_info` again with a fresh attestation, accidentally attaching `1 NEAR` (e.g., her wallet's default minimum).
3. `add_participant` returns `UpdatedExistingParticipant` → `is_new_attestation = false`.
4. `self.voter_account()` succeeds for Alice → `caller_is_not_participant = false`.
5. `attestation_storage_must_be_paid_by_caller = false` → the `if` block is skipped entirely.
6. The call succeeds, Alice's attestation is updated, and `1 NEAR` is permanently locked in the contract. [4](#0-3)

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

**File:** crates/contract/src/tee/tee_state.rs (L46-50)
```rust
#[derive(Debug)]
pub(crate) enum ParticipantInsertion {
    NewlyInsertedParticipant,
    UpdatedExistingParticipant,
}
```
