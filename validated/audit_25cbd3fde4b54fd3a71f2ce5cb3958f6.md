### Title
Attached Deposit Not Refunded to Participant on Attestation Re-Submission - (`File: crates/contract/src/lib.rs`)

### Summary

`submit_participant_info` is a `#[payable]` function. When a **current participant** re-submits their attestation (an update, not a new entry), the entire deposit-handling block is skipped. Any NEAR tokens attached by the caller are silently retained by the contract with no refund path.

### Finding Description

`submit_participant_info` computes a boolean gate to decide whether to enforce and refund a storage deposit:

```rust
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... check deposit >= cost, refund excess ...
}
``` [1](#0-0) 

When `attestation_storage_must_be_paid_by_caller` evaluates to `false` — i.e., when the caller **is** a current participant (`caller_is_not_participant == false`) **and** the submission is an update (`is_new_attestation == false`) — the entire block is bypassed. No deposit is required (correct), but crucially, **no refund is issued either** (incorrect). Any NEAR tokens the caller attached are permanently absorbed by the contract. [2](#0-1) 

The function is declared `#[payable]`, so the NEAR runtime will accept any attached deposit without complaint. [3](#0-2) 

The comment inside the block explains an intentional asymmetry for *freed storage bytes*, but says nothing about the case where the entire deposit-handling block is skipped: [4](#0-3) 

### Impact Explanation

Every other payable entry point in the contract (`sign`, `request_app_private_key`, `propose_update`, and the new-participant branch of `submit_participant_info`) explicitly refunds excess deposits. The participant re-submission branch is the only path that silently consumes any attached value. This breaks the production accounting invariant that callers receive back any NEAR they did not owe.

The `mpc-node` calls `submit_participant_info` on a **1-hour cadence** for periodic attestation renewal. Test helpers attach `NearToken::from_near(1)` per call: [5](#0-4) 

If the production node attaches any non-zero deposit on re-submissions (even 1 yoctoNEAR), those funds are permanently lost to the contract on every renewal cycle. At 1 NEAR per hour per node, the loss compounds continuously.

**Allowed impact match:** Medium — balance/accounting invariant broken, direct loss of participant funds, no operator misconfiguration required.

### Likelihood Explanation

- `submit_participant_info` is called automatically by every MPC node on a 1-hour cadence.
- The function is `#[payable]`, so any deposit attached (intentionally or by convention) is silently consumed.
- The trigger condition (participant re-submission) is the **normal steady-state operation** of the network, not an edge case.
- No privileged access, collusion, or external dependency failure is required.

### Recommendation

Add an unconditional refund of any excess deposit at the end of `submit_participant_info`, mirroring the pattern used in `require_deposit` and `propose_update`:

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

Alternatively, restructure the deposit logic so that `env::attached_deposit()` is always read and any amount above the computed cost (zero for participant re-submissions) is always returned to the caller.

### Proof of Concept

1. A current participant calls `submit_participant_info` with `attached_deposit = 1 NEAR` to renew their attestation.
2. `add_participant` returns `ParticipantInsertion::UpdatedParticipant` → `is_new_attestation = false`.
3. `self.voter_account().is_ok()` → `caller_is_not_participant = false`.
4. `attestation_storage_must_be_paid_by_caller = false || false = false`.
5. The `if` block is skipped entirely — no refund is scheduled.
6. The call returns `Ok(())`. The 1 NEAR is permanently held by the contract.
7. This repeats every hour for every node in the network. [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L758-760)
```rust
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
```

**File:** crates/contract/src/lib.rs (L817-852)
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
    }
```

**File:** crates/contract/src/lib.rs (L3993-3997)
```rust
        let participant_context = VMContextBuilder::new()
            .signer_account_id(account_id.clone())
            .predecessor_account_id(account_id.clone())
            .attached_deposit(NearToken::from_near(1))
            .build();
```
