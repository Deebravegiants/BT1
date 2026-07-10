### Title
Unrefunded Deposit in `submit_participant_info` When Caller Is an Existing Participant — (File: `crates/contract/src/lib.rs`)

### Summary
`submit_participant_info` is marked `#[payable]`, allowing any caller to attach an arbitrary NEAR deposit. However, when the caller is an existing participant re-submitting their attestation (not a new insertion), the deposit-handling block is skipped entirely. Any attached deposit is silently consumed by the contract with no refund and no withdrawal mechanism, permanently locking those funds.

### Finding Description
`submit_participant_info` is declared `#[payable]` at line 758: [1](#0-0) 

After `add_participant` returns, the function computes a boolean gate: [2](#0-1) 

The deposit check and refund logic is only entered when `attestation_storage_must_be_paid_by_caller` is `true`: [3](#0-2) 

When the condition is `false` — i.e., the caller **is** a current participant **and** the insertion result is `UpdatedExistingParticipant` (a re-submission) — the entire block is byp

### Title
Deposit Silently Consumed Without Refund in `submit_participant_info` Re-submission Path - (File: `crates/contract/src/lib.rs`)

### Summary

`submit_participant_info` is marked `#[payable]` and accepts arbitrary NEAR deposits, but when an existing participant re-submits their attestation (the normal hourly cadence), the deposit-handling block is entirely skipped. Any NEAR attached to that call is silently consumed by the contract with no refund and no withdrawal mechanism.

### Finding Description

`submit_participant_info` is declared `#[payable]`, meaning callers may attach any amount of NEAR. [1](#0-0) 

After the attestation is inserted, the function computes a boolean guard: [2](#0-1) 

The deposit check and excess-refund logic executes **only** when `attestation_storage_must_be_paid_by_caller` is `true`: [3](#0-2) 

When the condition is `false` — i.e., the caller is already a current participant **and** the attestation is not brand-new — the function returns `Ok(())` immediately without reading `env::attached_deposit()` or issuing any refund. Any NEAR attached to the call is absorbed into the contract balance permanently.

There is no `withdraw`, `drain`, or admin-sweep function anywhere in the contract that could recover these funds.

### Impact Explanation

Every NEAR token attached to a re-submission call by an existing participant is permanently locked in the MPC contract. The contract's own documentation states that nodes re-submit attestations on a **1-hour cadence** and on attestation-removal events:

> "The only caller of `submit_participant_info` in production is `mpc-node`'s `periodic_attestation_submission` task, which resubmits on a 1-hour cadence."

The node software currently sends `0` deposit by default for re-submissions, so routine automated calls are unaffected. However, the function is `#[payable]` and the contract's own troubleshooting guide explicitly instructs operators to call `submit_participant_info` **manually with `--deposit`** for first-time joins:

> "Attached deposit is lower than required. Attached: X, required: Y — first-time joiners must attach enough yoctoNEAR for storage; the node attaches 0, so call `submit_participant_info` manually with `--deposit` once." [4](#0-3) 

An operator who follows this guidance and then re-submits (e.g., after a TEE upgrade) while still a participant will have their deposit silently consumed. The `#[payable]` attribute provides no warning that the deposit will not be refunded in this path. The funds are permanently frozen in the contract with no recovery path.

This matches: **Medium — Balance/accounting invariant violation that breaks production safety/accounting invariants.**

### Likelihood Explanation

- The re-submission path (`is_new_attestation = false`, `caller_is_not_participant = false`) is the **normal steady-state** for every existing participant after their first join.
- The troubleshooting documentation actively guides operators to attach deposits manually, making accidental deposit attachment during re-submission a realistic operator error.
- The `#[payable]` attribute gives no indication that the deposit will be silently discarded in this branch.

### Recommendation

Add an unconditional excess-deposit refund at the end of `submit_participant_info`, mirroring the pattern already used in `require_deposit` and `propose_update`:

```rust
// After the conditional storage-charge block, always refund any
// deposit that was not consumed by storage costs.
let attached = env::attached_deposit();
let consumed = if attestation_storage_must_be_paid_by_caller { cost } else { NearToken::from_yoctonear(0) };
if let Some(excess) = attached.checked_sub(consumed) {
    if excess > NearToken::from_yoctonear(0) {
        Promise::new(account_id).transfer(excess).detach();
    }
}
```

Alternatively, remove `#[payable]` from `submit_participant_info` entirely and handle the storage-staking deposit as a separate, explicit call, so the NEAR runtime rejects any accidental deposit at the protocol level.

### Proof of Concept

1. Deploy the MPC contract and initialize it with participant `alice.near`.
2. `alice.near` calls `submit_participant_info` with a valid attestation and `--deposit 1 NEAR` (first join). Deposit is correctly charged for storage; excess is refunded.
3. `alice.near` is now a current participant (`voter_account()` returns `Ok`).
4. `alice.near` calls `submit_participant_info` again (re-submission, e.g., after a TEE upgrade) with `--deposit 0.5 NEAR`.
5. `add_participant` returns `ParticipantInsertion::UpdatedExistingParticipant` (not `NewlyInsertedParticipant`).
6. `is_new_attestation = false`, `caller_is_not_participant = false` → `attestation_storage_must_be_paid_by_caller = false`.
7. The deposit-handling block is skipped entirely. The function returns `Ok(())`.
8. The 0.5 NEAR is now in the contract balance with no refund issued and no mechanism to recover it. [5](#0-4) [6](#0-5)

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

**File:** docs/running-an-mpc-node-in-tdx-external-guide.md (L2039-2039)
```markdown
- **`Attached deposit is lower than required. Attached: X, required: Y`** — first-time joiners must attach enough yoctoNEAR for storage; the node attaches `0`, so call `submit_participant_info` manually with `--deposit` once. Exact amount tracked in [#903](https://github.com/near/mpc/issues/903).
```
