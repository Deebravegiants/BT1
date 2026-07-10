### Title
Excess Deposit Silently Retained in `submit_participant_info` When Caller Is an Existing Participant - (File: crates/contract/src/lib.rs)

---

### Summary

`submit_participant_info` is marked `#[payable]` and accepts NEAR token deposits from any caller. However, the deposit-refund logic is gated behind a conditional branch that is only entered when `attestation_storage_must_be_paid_by_caller` is `true`. When an **existing participant** re-submits their attestation (the common hourly re-attestation path), this condition is `false` and the entire deposit-handling block is skipped. Any NEAR tokens attached to the call are silently absorbed by the contract with no refund and no error.

---

### Finding Description

In `crates/contract/src/lib.rs`, `submit_participant_info` is declared `#[payable]`: [1](#0-0) 

After the attestation is inserted, the contract computes whether the caller must pay for storage: [2](#0-1) 

`attestation_storage_must_be_paid_by_caller` is `false` when the caller is already a participant **and** the submission is not a new attestation entry (i.e., a re-submission). In that case the entire deposit block — which includes both the sufficiency check and the refund — is skipped: [3](#0-2) 

Because the function is `#[payable]`, the NEAR runtime accepts any attached deposit without complaint. When the branch is not entered, `env::attached_deposit()` is never read, and no `Promise::transfer` is scheduled. The tokens remain in the contract balance permanently.

Compare this to the consistent pattern used everywhere else in the contract — `require_deposit` in `check_request_preconditions`, and the explicit refund in `propose_update` — both of which unconditionally refund any excess: [4](#0-3) [5](#0-4) 

---

### Impact Explanation

**Medium.** Any NEAR tokens attached to a re-submission call by an existing participant are permanently locked in the contract. The contract's own documentation and operator guide explicitly instruct first-time joiners to call `submit_participant_info` manually with `--deposit`; an operator who follows the same procedure on a subsequent re-submission (e.g., after a TEE upgrade or attestation expiry) will silently lose their deposit. This breaks the production accounting invariant that `#[payable]` functions must refund excess deposits, and causes a direct, irreversible loss of the caller's funds with no error signal.

---

### Likelihood Explanation

**Medium.** The `mpc-node` daemon submits with zero deposit by default, but the operator guide explicitly documents the manual `--deposit` path for first-time joiners and for cases where the node fails to submit automatically. An operator who has already joined and re-runs the same manual command (e.g., after a TEE image upgrade forces re-attestation) will hit this path. The function being `#[payable]` provides no hint that a deposit is unnecessary on re-submission, making the mistake natural. The periodic re-attestation cadence (hourly) means the window of exposure is continuous. [6](#0-5) 

---

### Recommendation

Add an unconditional refund of any excess deposit at the end of `submit_participant_info`, mirroring the pattern already used in `require_deposit` and `propose_update`:

```rust
// After the attestation_storage_must_be_paid_by_caller block:
let attached = env::attached_deposit();
if attached > NearToken::from_yoctonear(0) {
    // Refund any deposit not consumed by storage staking.
    // (When attestation_storage_must_be_paid_by_caller is true, the
    // inner block already refunds the diff; this handles the false branch.)
    Promise::new(account_id).transfer(attached).detach();
}
```

Alternatively, restructure the deposit handling so that `env::attached_deposit()` is always read and any amount above the actual storage cost (zero in the re-submission case) is always returned to the caller.

---

### Proof of Concept

1. Deploy the contract with two participants and have both submit valid attestations (so both are in the `tee_state` participant set).
2. As participant A (already attested), call `submit_participant_info` again with `attached_deposit = 1 NEAR`.
3. Observe: `attestation_insertion_result` is `UpdatedExistingParticipant` → `is_new_attestation = false`; `voter_account()` succeeds → `caller_is_not_participant = false`; therefore `attestation_storage_must_be_paid_by_caller = false`.
4. The deposit block is skipped entirely. The call returns `Ok(())`.
5. Check participant A's balance: 1 NEAR is gone. Check the contract balance: 1 NEAR has been added. No refund promise was ever scheduled. [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L134-138)
```rust
        Some(diff) => {
            if diff > NearToken::from_yoctonear(0) {
                log!("refund excess deposit {diff} to {predecessor}");
                Promise::new(predecessor.clone()).transfer(diff).detach();
            }
```

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

**File:** crates/contract/src/lib.rs (L1327-1331)
```rust
        if let Some(diff) = attached.checked_sub(required)
            && diff > NearToken::from_yoctonear(0)
        {
            Promise::new(proposer).transfer(diff).detach();
        }
```

**File:** docs/running-an-mpc-node-in-tdx-external-guide.md (L2039-2039)
```markdown
- **`Attached deposit is lower than required. Attached: X, required: Y`** — first-time joiners must attach enough yoctoNEAR for storage; the node attaches `0`, so call `submit_participant_info` manually with `--deposit` once. Exact amount tracked in [#903](https://github.com/near/mpc/issues/903).
```
