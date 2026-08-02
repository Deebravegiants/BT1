## Custody Analog Found: Multisig Payload-Match Bypass via Empty Executable

### Title
Multisig transaction payload-equality enforcement can be bypassed by submitting an empty executable, allowing execution to proceed without validating that the executed payload matches the owner-approved payload - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The external report's core invariant is: an equality check gated behind a `>=`/emptiness condition can be silently skipped, letting a shorter/different value pass as if it matched. The Aptos analog is in `validate_multisig_transaction`, where the check that the payload supplied at execution time matches the payload the owners actually approved is conditioned on the payload not being empty and on a feature flag, creating a bypass path structurally identical to the `equals`-with-offset flaw.

### Finding Description
`multisig_account::validate_multisig_transaction` [1](#0-0)  is the prologue gate that is supposed to ensure the transaction being executed on behalf of a multisig account is exactly the transaction the owners voted for. It performs two distinct equality checks depending on how the transaction was created:

1. If only a hash was stored (`create_transaction_with_hash`), it checks `sha3_256(payload) == *payload_hash` [2](#0-1) .
2. If the full payload was stored on-chain (`create_transaction`), it is *supposed* to check that the payload supplied at execution matches the stored payload exactly — but this check only runs when three conditions all hold: the `abort_if_multisig_payload_mismatch_enabled` feature is on, `transaction.payload.is_some()`, **and** `!payload.is_empty()**: [3](#0-2) 

On the VM side, `run_multisig_prologue` (and the matching `execute_multisig_transaction`) computes `provided_payload` from the submitted `TransactionExecutableRef`. Critically, when the executor submits an **empty** executable (`TransactionExecutableRef::Empty`), and the mismatch-detection feature *is* enabled, `provided_payload` is set to a truly empty `vec![]`: [4](#0-3) [5](#0-4) 

That empty `provided_payload` becomes the `payload` argument to `validate_multisig_transaction`. Because `payload.is_empty()` is now `true`, the guard `!payload.is_empty()` evaluates to `false`, so the entire "verify that the provided payload matches the stored payload" block is skipped — **even when the dedicated safety feature flag is turned on**. This mirrors the C4 finding precisely: the equality check that is supposed to hold unconditionally (`sha3_256`/direct payload equality) is instead gated by a size/emptiness condition that an attacker fully controls, letting them opt out of the very check meant to prevent payload substitution.

Separately, when the feature flag is off entirely (its default/rollout state on any given network), the whole block is skipped unconditionally regardless of payload content — the comment at line 1373 makes explicit that this assert exists specifically to "verify that the provided payload matches the stored payload," implying that absent this feature-gated check, nothing else in the prologue enforces that invariant for on-chain-stored-payload multisig transactions.

### Impact Explanation
If the actual bytes ultimately executed for the multisig account (fetched from `get_next_transaction_payload`, which I could not fully trace to its Move source in this session) can be influenced by the executor-supplied payload rather than being unconditionally forced to the on-chain-stored `transaction.payload`, this bypass would allow any single owner who is permitted to execute a queued transaction to substitute an unapproved payload for the one that received the required k-of-n approvals — a direct authority/custody break for any resource-account-owned or code-object-owned assets controlled by the multisig. This is a Critical impact class (unauthorized transfer/mint/burn/ownership reassignment of multisig-held value) if confirmed.

### Likelihood Explanation
The bypass condition (submitting `TransactionExecutableRef::Empty`) is fully within the control of any transaction submitter and requires no special privilege beyond being able to submit the executing transaction (which itself requires being a multisig owner with sufficient approvals for *some* queued transaction). This makes the trigger trivial to reach; the open question is purely whether `get_next_transaction_payload` treats the (bypassed/unvalidated) `provided_payload` as authoritative in the on-chain-payload-stored case, or whether it always falls back to the stored payload regardless, which would neutralize the practical impact.

### Recommendation
- Remove the `!payload.is_empty()` carve-out from the payload-match assertion in `validate_multisig_transaction`, and instead always assert consistency between what is queued for execution and what is actually submitted (treating "empty" as a mismatch when a full payload is stored on-chain), analogous to changing the ENS `>=` to `==`.
- Make the payload-match check unconditional (not feature-gated) once its correctness is confirmed, since its absence otherwise leaves an unenforced custody invariant.
- Verify and, if necessary, harden `get_next_transaction_payload` (the Move function invoked by `GET_NEXT_TRANSACTION_PAYLOAD` in `aptos_vm.rs`) so that whenever `transaction.payload.is_some()`, the stored payload — not the executor-supplied one — is unconditionally the one that gets executed, independent of this prologue check succeeding or being skipped.

### Proof of Concept
1. Owner A creates a multisig transaction with `create_transaction(owner, multisig, payload_X)`, storing `payload_X` fully on-chain (`transaction.payload_hash` = `none`).
2. Owners approve until quorum for sequence number N.
3. An executing owner submits the execution transaction using `TransactionExecutableRef::Empty` instead of re-supplying `payload_X`.
4. In `run_multisig_prologue`, if `abort_if_multisig_payload_mismatch_enabled` is on, `provided_payload = vec![]` (truly empty); if off, `provided_payload = bcs::to_bytes(&vec![])` (non-empty but garbage, and the whole check is skipped anyway since the feature is off).
5. In `validate_multisig_transaction`, `payload.is_empty()` is true (feature-on case) so the `payload == *stored_payload` assertion at line 1380–1383 never executes; in the feature-off case, the assertion block is skipped by the outer `features::...` guard regardless of payload content.
6. Execution proceeds to `execute_multisig_transaction` → `get_next_transaction_payload`, whose exact selection logic (stored vs. provided) was not verifiable within this investigation's tool budget — this is the one link needed to fully confirm whether an unapproved payload can actually run in place of `payload_X`.

**Note on confidence**: I was unable to locate and read the Move source of `get_next_transaction_payload` within my remaining tool budget, despite it being referenced twice in `multisig_account.move`. That function's exact behavior (does it always prioritize the on-chain `transaction.payload` when present, or can `provided_payload` override it?) is the deciding factor for whether this bypass has real custody impact or is merely a redundant sanity-check gap. I recommend a Devin session read `multisig_account.move`'s `get_next_transaction_payload` function body in full to close this gap before treating this as a confirmed critical finding.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1328-1333)
```text
    fun validate_multisig_transaction(
        owner: &signer, multisig_account: address, payload: vector<u8>) {
        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);
        let sequence_number = last_resolved_sequence_number(multisig_account) + 1;
        assert_transaction_exists(multisig_account, sequence_number);
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1361-1371)
```text
        // If the transaction payload is not stored on chain, verify that the provided payload matches the hashes stored
        // on chain.
        let multisig_account_resource = borrow_global<MultisigAccount>(multisig_account);
        let transaction = multisig_account_resource.transactions.borrow(sequence_number);
        if (transaction.payload_hash.is_some()) {
            let payload_hash = transaction.payload_hash.borrow();
            assert!(
                sha3_256(payload) == *payload_hash,
                error::invalid_argument(EPAYLOAD_DOES_NOT_MATCH_HASH),
            );
        };
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1373-1385)
```text
        // If the transaction payload is stored on chain and there is a provided payload,
        // verify that the provided payload matches the stored payload.
        if (features::abort_if_multisig_payload_mismatch_enabled()
            && transaction.payload.is_some()
            && !payload.is_empty()
        ) {
            let stored_payload = transaction.payload.borrow();
            assert!(
                payload == *stored_payload,
                error::invalid_argument(EPAYLOAD_DOES_NOT_MATCH),
            );
        }
    }
```

**File:** aptos-move/aptos-vm/src/transaction_validation.rs (L437-443)
```rust
        TransactionExecutableRef::Empty => {
            if features.is_abort_if_multisig_payload_mismatch_enabled() {
                vec![]
            } else {
                bcs::to_bytes::<Vec<u8>>(&vec![]).map_err(|_| unreachable_error.clone())?
            }
        },
```

**File:** aptos-move/aptos-vm/src/aptos_vm.rs (L1315-1325)
```rust
            TransactionExecutableRef::Empty => {
                // Default to empty bytes if payload is not provided.
                if self
                    .features()
                    .is_abort_if_multisig_payload_mismatch_enabled()
                {
                    vec![]
                } else {
                    bcs::to_bytes::<Vec<u8>>(&vec![]).map_err(|_| invariant_violation_error())?
                }
            },
```
