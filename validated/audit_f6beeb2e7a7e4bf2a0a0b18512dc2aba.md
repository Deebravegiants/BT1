### Title
Silent Deposit Consumption in `submit_participant_info` Update Path — (File: `crates/contract/src/lib.rs`)

### Summary
`submit_participant_info` is marked `#[payable]` and contains a deposit-refund block, but that block is gated behind a condition that evaluates to `false` for the most common production call path — an existing participant refreshing their attestation. Any NEAR attached in that path is silently absorbed by the contract with no refund and no error.

### Finding Description
The function computes a boolean guard before entering the deposit-handling block:

```rust
// crates/contract/src/lib.rs ~L817-L848
let caller_is_not_participant = self.voter_account().is_err();
let is_new_attestation = matches!(
    attestation_insertion_result,
    ParticipantInsertion::NewlyInsertedParticipant
);

let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;

if attestation_storage_must_be_paid_by_caller {
    // ... storage cost check ...
    // ... refund of excess deposit ...
}
``` [1](#0-0) 

When the caller is an **already-registered participant** (`voter_account()` succeeds → `caller_is_not_participant = false`) **and** the submission updates an existing entry rather than inserting a new one (`is_new_attestation = false`), the guard is `false`. The entire block — including the refund — is skipped. `env::attached_deposit()` is never read, never compared, and never returned. Any NEAR attached to the call is permanently locked in the contract.

The function is unconditionally `#[payable]`:

```rust
#[payable]
#[handle_result]
pub fn submit_participant_info(...)
``` [2](#0-1) 

The node's periodic attestation-resubmission task (`periodic_attestation_submission`, called on a 1-hour cadence) is the primary caller of this method in production. Unit tests consistently attach `NearToken::from_near(1)` when calling `submit_participant_info`: [3](#0-2) 

If the node or any tooling attaches even 1 yoctoNEAR on a re-submission, that amount is irrecoverably transferred to the contract.

### Impact Explanation
Every successful re-submission by an existing participant silently drains NEAR from the participant's account into the contract with no mechanism for recovery. Because `submit_participant_info` is `#[payable]` and the README documents that "any excess deposit is automatically refunded" for other payable methods, callers have a reasonable expectation of refund. The contract's own accounting invariant — excess deposits are returned — is violated on this code path. This maps to the **Medium** allowed impact: *balance or contract execution-flow manipulation that breaks production safety/accounting invariants*.

### Likelihood Explanation
MPC nodes call `submit_participant_info` on a fixed hourly cadence and on attestation-removal events. Any tooling, operator script, or test harness that attaches a deposit (as the unit tests do with 1 NEAR) on a re-submission will silently lose that deposit. The code path is exercised continuously in production. Likelihood is **Medium**.

### Recommendation
Remove the `if attestation_storage_must_be_paid_by_caller` gate around the refund logic, or add an unconditional refund of any excess deposit at the end of the function regardless of which branch was taken:

```rust
// After the conditional storage-charge block:
let attached = env::attached_deposit();
let charged = if attestation_storage_must_be_paid_by_caller { cost } else { NearToken::from_yoctonear(0) };
if let Some(diff) = attached.checked_sub(charged)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(account_id).transfer(diff).detach();
}
```

Alternatively, if no deposit is ever required on the update path, add `#[deposit(0)]` or assert `env::attached_deposit() == 0` on that branch to prevent accidental overpayment at the call site.

### Proof of Concept
1. Deploy the contract with two participants (threshold = 2).
2. Both participants call `submit_participant_info` with a valid attestation — this is the initial insertion (`is_new_attestation = true`), so the deposit-handling block runs and any excess is refunded.
3. One participant calls `submit_participant_info` again (simulating the hourly re-submission) while attaching `NearToken::from_near(1)`.
   - `voter_account()` succeeds → `caller_is_not_participant = false`
   - The insertion result is `UpdatedParticipant` (not `NewlyInsertedParticipant`) → `is_new_attestation = false`
   - `attestation_storage_must_be_paid_by_caller = false`
   - The deposit-handling block is skipped entirely.
4. Observe that the participant's balance decreased by 1 NEAR and the contract balance increased by 1 NEAR, with no refund receipt emitted. [4](#0-3)

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

**File:** crates/contract/src/lib.rs (L3993-3997)
```rust
        let participant_context = VMContextBuilder::new()
            .signer_account_id(account_id.clone())
            .predecessor_account_id(account_id.clone())
            .attached_deposit(NearToken::from_near(1))
            .build();
```
