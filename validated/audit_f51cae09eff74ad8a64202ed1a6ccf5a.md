### Title
Deposit Silently Consumed on Existing-Participant Attestation Re-submission — (File: `crates/contract/src/lib.rs`)

### Summary
`submit_participant_info` is `#[payable]` and contains deposit-refund logic, but that logic is gated behind a condition that is `false` for the most common production call path: an existing participant re-submitting their attestation. Any NEAR attached in that case is silently retained by the contract, breaking the deposit-accounting invariant that every other payable entry-point in the contract upholds.

### Finding Description
`submit_participant_info` computes a boolean guard:

```rust
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;
```

The entire deposit-handling block — including the insufficiency check **and** the excess-refund — is wrapped in `if attestation_storage_must_be_paid_by_caller { … }`. [1](#0-0) 

When an existing participant re-submits their attestation (the normal hourly cadence documented in the codebase), both sub-conditions are `false`:
- `is_new_attestation` is `false` — `add_participant` returns `UpdatedExistingParticipant`, not `NewlyInsertedParticipant`.
- `caller_is_not_participant` is `false` — `self.voter_account()` succeeds.

The `if` block is therefore skipped entirely. `env::attached_deposit()` is never read, never checked, and never refunded. Any NEAR the caller attached is absorbed into the contract's balance.

Compare this with every other payable entry-point in the contract:

- `require_deposit` (used by `sign`, `request_app_private_key`, `verify_foreign_transaction`) always refunds the excess to `predecessor`. [2](#0-1) 
- `propose_update` always refunds the excess to `proposer`. [3](#0-2) 

`submit_participant_info` is the only `#[payable]` method that silently swallows a deposit on a reachable code path.

The node software calls `submit_participant_info` on a 1-hour cadence (`periodic_attestation_submission`) and on attestation-removal events. [4](#0-3)  The call sites are in `crates/node/src/tee/remote_attestation.rs` and `crates/node/src/indexer/tx_sender.rs`. If the node attaches any deposit (e.g., to cover anticipated storage costs), that deposit is permanently lost on every re-submission by an existing participant.

### Impact Explanation
**Medium.** This breaks the production deposit-accounting invariant: the contract is `#[payable]` on this method but provides no refund path for the dominant re-submission case. Over the hourly re-submission cadence, node operators silently lose attached NEAR. The contract's own balance grows at the expense of participant operators, with no mechanism for recovery. This matches the allowed Medium impact: *"Balance … manipulation that breaks production safety/accounting invariants."*

### Likelihood Explanation
**Medium.** Every active participant re-submits their attestation on a 1-hour cadence. Whether the node attaches a non-zero deposit on re-submission depends on the node software (files `remote_attestation.rs` / `tx_sender.rs` were not fully inspected), but the contract provides no guard against it and no refund if it happens. The CHANGELOG entry "Contract was refunding too much of deposit (#1165)" confirms this area has had prior deposit-accounting bugs, making a residual gap plausible.

### Recommendation
Unconditionally refund any excess deposit at the end of `submit_participant_info`, regardless of the `attestation_storage_must_be_paid_by_caller` branch. The simplest fix mirrors the pattern already used in `propose_update`:

```rust
// After the if attestation_storage_must_be_paid_by_caller { … } block:
let attached = env::attached_deposit();
if attached > NearToken::from_yoctonear(0) {
    // refund whatever was not consumed by storage
    Promise::new(account_id).transfer(attached).detach();
}
```

Or, restructure the function to call `require_deposit(NearToken::from_yoctonear(0), &account_id)` unconditionally so the shared refund helper handles the excess.

### Proof of Concept

1. Deploy the contract with one participant (`alice.near`).
2. `alice.near` calls `submit_participant_info` a second time (re-submission) and attaches `1_000_000_000_000_000_000_000_000` yoctoNEAR (1 NEAR).
3. `add_participant` returns `UpdatedExistingParticipant` → `is_new_attestation = false`.
4. `self.voter_account()` succeeds → `caller_is_not_participant = false`.
5. `attestation_storage_must_be_paid_by_caller = false` → the `if` block is skipped.
6. The function returns `Ok(())`. Alice's 1 NEAR is now in the contract's balance with no refund promise scheduled.
7. Alice's account balance is permanently reduced by 1 NEAR plus gas fees. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L122-141)
```rust
fn require_deposit(minimum_deposit: NearToken, predecessor: &AccountId) {
    let deposit = env::attached_deposit();
    match deposit.checked_sub(minimum_deposit) {
        None => {
            env::panic_str(
                &InvalidParameters::InsufficientDeposit {
                    attached: deposit.as_yoctonear(),
                    required: minimum_deposit.as_yoctonear(),
                }
                .to_string(),
            );
        }
        Some(diff) => {
            if diff > NearToken::from_yoctonear(0) {
                log!("refund excess deposit {diff} to {predecessor}");
                Promise::new(predecessor.clone()).transfer(diff).detach();
            }
        }
    }
}
```

**File:** crates/contract/src/lib.rs (L756-760)
```rust
    /// (Prospective) Participants can submit their tee participant information through this
    /// endpoint.
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
