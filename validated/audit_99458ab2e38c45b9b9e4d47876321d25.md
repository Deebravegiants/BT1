### Title
Storage Deposit Permanently Lost When `clean_invalid_attestations` Removes TEE Attestation Entries Without Refunding Submitter - (File: `crates/contract/src/lib.rs`)

### Summary
`submit_participant_info` charges the calling node operator a storage-staking deposit proportional to the bytes written. That deposit is consumed immediately and its amount is never stored for later retrieval. When `clean_invalid_attestations` subsequently removes those entries (triggered automatically after resharing or callable by any account), the freed storage tokens accrue to the contract's own balance and are never returned to the original submitter. This is the direct analog of `destroyEscrow()` deleting escrow state without returning deposited tokens.

### Finding Description
`submit_participant_info` measures storage growth and charges the caller exactly for it: [1](#0-0) 

The deposit amount is consumed for storage staking. Crucially, neither the amount nor the recipient address is persisted anywhere in contract state — there is no `PendingStorageRefund` map or equivalent. The only refund path is the excess-deposit refund at submission time.

`clean_invalid_attestations` (called automatically with `RESHARE_CLEAN_INVALID_ATTESTATIONS_MAX_SCAN = 100` entries per resharing event, and also callable by any unprivileged account) removes stored attestation entries: [2](#0-1) 

When an entry is removed, NEAR's storage-staking mechanism releases the locked tokens back into the **contract's** balance — not back to the original submitter. Because the deposit amount and the submitter's identity were never stored, there is no mechanism to issue a refund. The storage deposit is permanently absorbed by the contract.

The intentional asymmetry already documented in `submit_participant_info` — "we do not refund freed bytes … the caller already paid for the larger entry" — applies only to re-submissions that shrink an existing entry: [3](#0-2) 

That comment does not cover the deletion case triggered by `clean_invalid_attestations`, where the entire entry is removed and the full storage deposit is silently forfeited.

### Impact Explanation
Every node operator who called `submit_participant_info` and paid a storage deposit loses that deposit whenever `clean_invalid_attestations` removes their entry. The freed NEAR tokens remain in the contract's balance with no path back to the original payer. This breaks the production accounting invariant that storage deposits are returned when the storage they cover is freed. Impact: **Medium** — balance/participant-state accounting invariant broken without requiring network-level DoS or operator misconfiguration.

### Likelihood Explanation
`clean_invalid_attestations` is triggered automatically after every resharing event (the most common governance operation) and is also a public callable. Resharing changes the participant set, which invalidates attestations for removed participants. Those participants paid storage deposits that are now permanently lost. Likelihood: **Medium** — resharing is a routine, expected operation.

### Recommendation
At submission time, store the deposit amount and the submitter's account ID alongside the attestation entry (analogous to how the proposed `PendingAttestation` design stores `attached_deposit`):

```rust
pub struct StoredAttestation {
    // ... existing fields ...
    pub storage_deposit: NearToken,
    pub depositor: AccountId,
}
```

When `clean_invalid_attestations` removes an entry, issue a `Promise::new(depositor).transfer(storage_deposit)` refund before deletion. This mirrors the refund pattern already used in `require_deposit` and the proposed `on_attestation_verified` yield-callback cleanup path. [4](#0-3) 

### Proof of Concept

1. Node operator Alice calls `submit_participant_info` with a valid attestation. The contract charges her `storage_byte_cost × bytes_written` (e.g., ~0.1 mNEAR for a typical attestation payload). The deposit is consumed; no record of the amount or Alice's identity is kept.

2. A governance vote calls `vote_new_parameters`, triggering resharing and removing Alice from the participant set.

3. After resharing completes, `clean_invalid_attestations` is called (automatically or by any account). Alice's now-invalid attestation entry is removed.

4. The storage tokens freed by removing Alice's entry flow into the contract's balance. Alice receives nothing.

5. Alice's storage deposit is permanently lost. The contract's balance is silently inflated by the forfeited amount. There is no on-chain event, no refund promise, and no recovery path. [1](#0-0) [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L106-108)
```rust
/// Entries to scan in the post-reshare `clean_invalid_attestations` sweep. External
/// callers may pick a different value; this only governs the automatic invocation.
const RESHARE_CLEAN_INVALID_ATTESTATIONS_MAX_SCAN: u32 = 100;
```

**File:** crates/contract/src/lib.rs (L122-140)
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
```

**File:** crates/contract/src/lib.rs (L826-848)
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
```

**File:** crates/contract/src/pending_requests.rs (L1-15)
```rust
//! Storage and bookkeeping for pending request fan-out.
//!
//! Each pending-request map stores a `Vec<YieldIndex>` so that duplicate
//! submissions of the same request key queue up and all receive the same MPC
//! response. This module owns:
//!
//! * the cap on how many yields may be queued for a single key,
//! * the queue mutations (`push`, FIFO pop, drain),
//! * the read/write policy on the fan-out map: `push_pending_yield` appends,
//!   `resolve_yields_for` drains the full queue on a response, and
//!   `pop_oldest_pending_yield` removes the head entry on a timeout.
//!
//! Callers in `lib.rs` go through these helpers rather than touching the maps
//! directly, so the queue policy lives in one place.

```
