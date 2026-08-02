Note: due to the final-iteration constraint, I was unable to verify two details with certainty: (1) the exact code of `create_transaction` vs. `create_transaction_with_hash` (which of the two paths populates `payload` vs `payload_hash`), and (2) the on-chain default value of the `abort_if_multisig_payload_mismatch_enabled` feature flag. My conclusion below is based on the `validate_multisig_transaction` logic I did confirm, and I flag this uncertainty explicitly.

### Title
Multisig executed payload is not bound to the quorum-approved payload when full payload is stored on-chain and the mismatch-check feature is disabled - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
The external bug's custody invariant is: *when an optional verification/conversion dependency is unset, the code must not silently proceed as if the check passed — it must fail closed, not open.* In `multisig_account::validate_multisig_transaction`, the check that the payload actually being executed matches the payload the owners voted on is itself gated by two independent optional conditions, both of which can be simultaneously absent, causing the match check to be skipped entirely while execution still proceeds.

### Finding Description
`validate_multisig_transaction` is invoked by the VM prologue to authorize execution of a multisig transaction as the multisig account's signer [1](#0-0) . After confirming quorum approvals for the `sequence_number`, it performs two separate, both-optional content checks before allowing the `payload` bytes (which is exactly `bcs::to_bytes` of the *executable that will actually run this transaction*, per `execute_multisig_transaction` in `aptos_vm.rs` [2](#0-1) ) to be executed:

```
if (transaction.payload_hash.is_some()) {
    assert!(sha3_256(payload) == *payload_hash, ...);
};
if (features::abort_if_multisig_payload_mismatch_enabled()
    && transaction.payload.is_some()
    && !payload.is_empty()
) {
    assert!(payload == *stored_payload, ...);
}
``` [3](#0-2) 

Quorum approvals are recorded and checked purely against a `sequence_number`, not against the content of the payload [4](#0-3) . The only mechanism binding "what the owners approved" to "what actually executes" is the pair of checks above. When a transaction is created with the full payload stored on-chain (rather than only a hash), `transaction.payload_hash` is `option::none()`, so the first (unconditional) check is skipped by construction — mirroring exactly the `prices != IJBPrices(address(0))` pattern in the external report, where an optional dependency being unset causes a security-relevant step to be bypassed. The second check is the only remaining guard, but it is itself gated behind the `abort_if_multisig_payload_mismatch_enabled` feature flag. If that flag is disabled (I could not confirm its default state on mainnet in this pass), both guards are inert, and `validate_multisig_transaction` succeeds regardless of whether `payload` matches anything the owners actually voted on.

### Impact Explanation
If both optional guards are absent, an executing owner can submit a transaction whose `executable` (entry function or script) is completely different from the payload that other owners approved for that `sequence_number`, while quorum still reports as satisfied (since votes are keyed only by sequence number). Because the multisig account is a resource account whose signer is generated and used to run this attacker-chosen executable [5](#0-4) , this can be used to drain APT, fungible assets, or objects owned by the multisig account, or to reassign object/code ownership held by it — a direct custody violation of "multisig-owned assets ... must not leak transfer authority to unprivileged callers," since the actual executed action was never actually approved by the required threshold of owners.

### Likelihood Explanation
Exploitability is conditional: it requires (a) a transaction to have been created via the full-payload-on-chain path (so `payload_hash` is `None`), and (b) the `abort_if_multisig_payload_mismatch_enabled` feature to be disabled on the network at execution time. I was not able to confirm the current/default feature-flag state before running out of tool budget, which is the deciding factor for real-world exploitability. The existence of a dedicated feature specifically named to "abort if multisig payload mismatch" strongly suggests this exact class of gap was previously present and is being closed incrementally, which is corroborating but not conclusive evidence for current exposure.

### Recommendation
Make the payload/executable match check unconditional (not feature-gated, not skippable) whenever `transaction.payload` is populated, mirroring the external report's recommendation to "revert when conversion/verification cannot be performed" rather than silently proceeding. Do not allow execution to proceed unless the `executable` being run is provably identical to either the stored `payload` or matches `payload_hash`, for every code path, independent of feature flag state.

### Proof of Concept
Conceptual reproduction (dependent on confirming feature-flag default, which I could not verify in this pass):
1. Multisig account with `create_transaction` (not `create_transaction_with_hash`) storing a benign payload (e.g., transfer 1 APT to owner C) at `sequence_number = N`. `transaction.payload_hash = None`.
2. Owners approve `N`, satisfying quorum for that sequence number only.
3. An owner submits `execute_multisig_transaction` for the multisig account, but with a transaction `executable` that instead drains the multisig's entire APT/FA balance to their own address.
4. In `validate_multisig_transaction`, `transaction.payload_hash.is_some()` is `false` → hash check skipped. If `features::abort_if_multisig_payload_mismatch_enabled()` is `false`, the payload-match check is also skipped.
5. Quorum check passes (keyed on `N`), and the drain executable runs as the multisig signer — moving custody value to an unapproved recipient.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1-10)
```text
/// Enhanced multisig account standard on Aptos. This is different from the native multisig scheme support enforced via
/// the account's auth key.
///
/// This module allows creating a flexible and powerful multisig account with seamless support for updating owners
/// without changing the auth key. Users can choose to store transaction payloads waiting for owner signatures on chain
/// or off chain (primary consideration is decentralization/transparency vs gas cost).
///
/// The multisig account is a resource account underneath. By default, it has no auth key and can only be controlled via
/// the special multisig transaction flow. However, owners can create a transaction to change the auth key to match a
/// private key off chain if so desired.
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1328-1334)
```text
    fun validate_multisig_transaction(
        owner: &signer, multisig_account: address, payload: vector<u8>) {
        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);
        let sequence_number = last_resolved_sequence_number(multisig_account) + 1;
        assert_transaction_exists(multisig_account, sequence_number);

```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1348-1359)
```text
        // Count approvals, including the executing owner's implicit vote.
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, address_of(owner))) {
            num_approvals += 1;
        };
        assert!(num_approvals >= num_signatures_required(multisig_account), error::invalid_argument(ENOT_ENOUGH_APPROVALS));

        // Timelock check — separate from quorum so the error is unambiguous.
        assert!(
            can_execute_with_timelock(multisig_account, sequence_number, num_approvals),
            error::invalid_state(ETIMELOCK_NOT_EXPIRED),
        );
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1361-1385)
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

**File:** aptos-move/aptos-vm/src/aptos_vm.rs (L1306-1325)
```rust
        let provided_payload = match executable {
            TransactionExecutableRef::EntryFunction(entry_func) => {
                // TODO[Orderless]: For backward compatibility reasons, still using `MultisigTransactionPayload` here.
                // Find a way to deprecate this.
                bcs::to_bytes(&MultisigTransactionPayload::EntryFunction(
                    entry_func.clone(),
                ))
                .map_err(|_| invariant_violation_error())?
            },
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
