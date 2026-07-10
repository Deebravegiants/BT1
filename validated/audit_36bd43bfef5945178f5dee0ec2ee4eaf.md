### Title
Excess NEAR Deposit Not Refunded in `submit_participant_info` for Existing Participant Re-submissions — (File: `crates/contract/src/lib.rs`)

---

### Summary

`submit_participant_info` is marked `#[payable]` and correctly refunds excess deposits for new participants or non-participants. However, when an **existing participant re-submits** their attestation (e.g., for a TEE upgrade), the entire deposit refund block is skipped, causing any attached NEAR to be permanently absorbed by the contract.

---

### Finding Description

The function `submit_participant_info` computes a boolean gate:

```rust
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;
``` [1](#0-0) 

The entire deposit-check-and-refund block is wrapped inside `if attestation_storage_must_be_paid_by_caller { ... }`:

```rust
if attestation_storage_must_be_paid_by_caller {
    ...
    if let Some(diff) = attached.checked_sub(cost)
        && diff > NearToken::from_yoctonear(0)
    {
        Promise::new(account_id).transfer(diff).detach();
    }
}
``` [2](#0-1) 

When `attestation_storage_must_be_paid_by_caller` evaluates to `false` — i.e., when `is_new_attestation == false` AND `caller_is_not_participant == false` (an **existing participant re-submitting** their attestation) — the block is entirely skipped. No deposit check is performed and no refund is issued. Any NEAR attached to the call is silently retained by the contract.

The function is declared `#[payable]`, which signals to callers that a deposit is accepted. Since first-time submissions require a deposit for storage costs, a participant performing a re-submission (e.g., after a TEE image upgrade) will naturally attach NEAR, expecting either it to be used or refunded. Instead, it is lost. [3](#0-2) 

For contrast, the `require_deposit` helper used by `sign`, `request_app_private_key`, and `verify_foreign_transaction` always refunds excess unconditionally:

```rust
Some(diff) => {
    if diff > NearToken::from_yoctonear(0) {
        log!("refund excess deposit {diff} to {predecessor}");
        Promise::new(predecessor.clone()).transfer(diff).detach();
    }
}
``` [4](#0-3) 

`propose_update` also correctly refunds excess in all cases. [5](#0-4) 

`submit_participant_info` is the only `#[payable]` function that silently absorbs deposits under a reachable code path.

---

### Impact Explanation

Any NEAR tokens attached by an existing participant during a re-submission are permanently transferred to the contract with no mechanism for recovery. This breaks the accounting invariant that a `#[payable]` function must return funds it does not consume. The lost funds are controlled by the MPC contract and cannot be withdrawn by the participant. This matches the **Medium** allowed impact: *balance or contract execution-flow manipulation that breaks production safety/accounting invariants*.

---

### Likelihood Explanation

TEE image upgrades are a routine operational event. When a new MPC node image is whitelisted, all existing participants must re-submit their attestation via `submit_participant_info`. Because the function is `#[payable]` and first-time submissions require a deposit, participants (or their automation scripts) will naturally attach NEAR on re-submission. This is a predictable, recurring scenario — not a corner case.

---

### Recommendation

Add an unconditional refund of any excess deposit at the end of `submit_participant_info`, regardless of whether `attestation_storage_must_be_paid_by_caller` is true. The simplest fix mirrors the pattern already used in `require_deposit`:

```rust
// After all storage-cost logic:
let attached = env::attached_deposit();
// (compute cost as before, or 0 if storage_must_be_paid is false)
if let Some(diff) = attached.checked_sub(cost_charged)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(account_id).transfer(diff).detach();
}
```

Alternatively, factor the refund out of the `if attestation_storage_must_be_paid_by_caller` block so it always executes.

---

### Proof of Concept

1. Participant `alice.near` is an existing, attested participant (`caller_is_not_participant = false`).
2. A new TEE image is whitelisted; `alice.near` must re-submit her attestation.
3. `alice.near` calls `submit_participant_info(...)` with `1 NEAR` attached (a reasonable amount given the function is `#[payable]` and storage costs vary).
4. `tee_state.add_participant(...)` returns `ParticipantInsertion::UpdatedExistingParticipant` → `is_new_attestation = false`.
5. `attestation_storage_must_be_paid_by_caller = false || false = false`.
6. The `if attestation_storage_must_be_paid_by_caller { ... }` block is skipped entirely.
7. The function returns `Ok(())`. The `1 NEAR` is never refunded and is now held by the contract with no withdrawal path. [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L134-139)
```rust
        Some(diff) => {
            if diff > NearToken::from_yoctonear(0) {
                log!("refund excess deposit {diff} to {predecessor}");
                Promise::new(predecessor.clone()).transfer(diff).detach();
            }
        }
```

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

**File:** crates/contract/src/lib.rs (L1326-1331)
```rust
        // Refund the difference if the proposer attached more than required.
        if let Some(diff) = attached.checked_sub(required)
            && diff > NearToken::from_yoctonear(0)
        {
            Promise::new(proposer).transfer(diff).detach();
        }
```
