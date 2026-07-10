### Title
NEAR Permanently Frozen in `submit_participant_info` When Existing Participant Re-submits Attestation — (File: `crates/contract/src/lib.rs`)

### Summary
`submit_participant_info` is marked `#[payable]` but only processes `attached_deposit` inside a conditional block. When an existing participant re-submits their attestation (not a new insertion), the deposit-handling branch is entirely skipped and any NEAR attached to the call is silently absorbed into the contract balance with no refund path and no withdrawal mechanism.

### Finding Description
The function `submit_participant_info` is decorated `#[payable]`, allowing callers to attach NEAR tokens. [1](#0-0) 

Inside the function, deposit handling is gated on a boolean:

```rust
let attestation_storage_must_be_paid_by_caller =
    is_new_attestation || caller_is_not_participant;
``` [2](#0-1) 

The entire block that reads `env::attached_deposit()`, checks sufficiency, and issues a refund is wrapped in `if attestation_storage_must_be_paid_by_caller { … }`: [3](#0-2) 

When `is_new_attestation` is `false` **and** `caller_is_not_participant` is `false` — i.e., an already-registered participant re-submits their attestation (e.g., to refresh an expiring TEE quote) — neither branch of the `||` is true. The deposit block is skipped entirely. Any NEAR attached to the call is accepted by the runtime (because the function is `#[payable]`) but is never read, never validated, and never refunded. It is permanently added to the contract's balance.

There is no `withdraw` or balance-recovery method anywhere in the contract, so the locked NEAR cannot be retrieved.

### Impact Explanation
Attached NEAR is permanently frozen inside the MPC contract. The contract has no withdrawal function, so the funds are irrecoverable. This breaks the production accounting invariant that every NEAR deposited into a `#[payable]` function is either consumed for its stated purpose or refunded. This maps to:

> **Medium** — Balance/accounting invariant violation that permanently freezes caller funds without relying on network-level DoS or operator misconfiguration.

### Likelihood Explanation
`submit_participant_info` is called by MPC nodes on a recurring basis to refresh TEE attestations before they expire. A node operator who copies a prior invocation (which included a storage deposit) and re-uses it for a re-submission, or whose tooling always attaches a small deposit "just in case," will silently lose that NEAR. The function's `#[payable]` annotation gives no indication that the deposit will be ignored in the re-submission path.

### Recommendation
Add an explicit guard at the top of the `else` branch (when `attestation_storage_must_be_paid_by_caller` is `false`) that rejects any non-zero deposit, mirroring the pattern recommended in the original report:

```rust
if !attestation_storage_must_be_paid_by_caller {
    let attached = env::attached_deposit();
    if attached > NearToken::from_yoctonear(0) {
        // Refund the entire deposit; no storage cost applies here.
        Promise::new(account_id.clone()).transfer(attached).detach();
    }
}
```

Alternatively, remove `#[payable]` from `submit_participant_info` entirely and split it into two entry points — one for new participants (payable, storage deposit required) and one for re-submissions (non-payable).

### Proof of Concept

1. Participant `alice.near` calls `submit_participant_info` for the first time. `is_new_attestation = true`, so `attestation_storage_must_be_paid_by_caller = true`. Storage cost is charged correctly and any excess is refunded.

2. Alice's TEE quote nears expiry. She calls `submit_participant_info` again with `1 NEAR` attached (e.g., copied from her original invocation script). Now `is_new_attestation = false` and `caller_is_not_participant = false`, so `attestation_storage_must_be_paid_by_caller = false`.

3. The deposit block at lines 826–849 is skipped. `env::attached_deposit()` is never called. The 1 NEAR is silently transferred to the contract's balance. [3](#0-2) 

4. No withdrawal function exists in the contract. The 1 NEAR is permanently frozen. [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L149-173)
```rust
#[near(contract_state)]
#[derive(Debug)]
pub struct MpcContract {
    protocol_state: ProtocolContractState,
    pending_signature_requests: LookupMap<SignatureRequest, Vec<YieldIndex>>,
    pending_ckd_requests: LookupMap<CKDRequest, Vec<YieldIndex>>,
    pending_verify_foreign_tx_requests: LookupMap<VerifyForeignTransactionRequest, Vec<YieldIndex>>,
    proposed_updates: ProposedUpdates,
    // TODO(#3475): drop this once we upgrade the contract and nodes start using
    // the new API.
    node_foreign_chain_support: SupportedForeignChainsByNode,
    config: Config,
    tee_state: TeeState,
    accept_requests: bool,
    node_migrations: NodeMigrations,
    // TODO(#2937): Remove via state migration.
    metrics: Metrics,
    foreign_chains: Lazy<ForeignChainsMetadata>,
    /// The verifier contract account trusted for DCAP verification, or [`None`]
    /// until participants vote one in. Not yet used to dispatch verification.
    // TODO(#3639): once participants have voted a verifier in, make this
    // non-optional via a migration that requires it be set.
    tee_verifier_account_id: Option<AccountId>,
    tee_verifier_votes: TeeVerifierVotes,
}
```

**File:** crates/contract/src/lib.rs (L757-760)
```rust
    /// endpoint.
    #[payable]
    #[handle_result]
    pub fn submit_participant_info(
```

**File:** crates/contract/src/lib.rs (L823-824)
```rust
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
