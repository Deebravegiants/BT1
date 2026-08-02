Given the scan across custody-relevant Aptos flows (account key-rotation signature schemes, `secp256k1`/`ethereum_derivable_account` recovery, `object.move` transfer authority, and `multisig_account.move` execution flow), the strongest local analog to the "unchecked signature/recovery result weakens quorum enforcement" bug class is in the multisig transaction execution path, where a stored **full payload** commitment is not enforced with the same rigor as a stored **hash** commitment. [1](#0-0) 

### Title
Multisig transaction execution can bypass owner-approved payload when full payload is stored on-chain - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
`validate_multisig_transaction`, the VM prologue hook that authorizes execution of a multisig transaction, enforces a strict content check between the payload provided at execution time and the on-chain-committed payload only when either (a) the transaction was created with a hash commitment, or (b) an experimental feature flag `abort_if_multisig_payload_mismatch_enabled` is turned on. When a transaction is created via `create_transaction` (full payload stored on-chain, no hash) and that feature flag is not active, an executor can submit an arbitrary, unrelated payload for execution while the module still treats the transaction as having received the owners' approvals recorded against the original (different) payload.

### Finding Description
`create_transaction` stores the full payload with `payload_hash: option::none()` [2](#0-1) . Owners vote on the transaction only by `sequence_number`, via `vote_transanction`, which never re-derives or compares the payload content — it just records a boolean against the owner address for that sequence number [3](#0-2) .

At execution time, `validate_multisig_transaction` is invoked by the VM with the payload the executor actually wants to run: [4](#0-3) 

The hash-committed case (`transaction.payload_hash.is_some()`) is checked unconditionally: `sha3_256(payload) == *payload_hash`. But the full-payload-committed case is only checked when `features::abort_if_multisig_payload_mismatch_enabled()` is true, `transaction.payload.is_some()`, and the caller-supplied `payload` is non-empty. If the feature is not active for the network, or if the mismatch check is bypassed by other means, there is no guarantee that the payload used for execution is the one owners actually approved. The module only verifies "enough owners voted `true` for this sequence number," not "enough owners voted for this exact payload."

This breaks the custody invariant that quorum approval must bind to the exact operation being executed — directly analogous to the external bug, where the bridge contract counted a defective/unintended signature toward quorum instead of enforcing that only genuine intended actions count. Here, the "signature" analog is the owner vote, and the missing binding is between the vote and the payload content.

### Impact Explanation
If exploitable (i.e., on a network/state where `abort_if_multisig_payload_mismatch_enabled` is not on, or via any other code path that omits the mismatch assertion), a single owner who created (and therefore auto-approved) a seemingly benign multisig transaction — e.g., "transfer 1 APT to X" — could, once nominal quorum is reached from other owners voting blind on the sequence number, execute a completely different payload such as `add_owners`, `update_signatures_required`, an arbitrary `EntryFunction` call that drains the multisig's APT/fungible-asset holdings, or transfers/burns objects owned by the multisig resource account. This is a direct custody violation: multisig-held value and multisig control authority (owner set, signature threshold) can be redirected to an unprivileged/unapproved party without a valid quorum over the actual operation performed.

### Likelihood Explanation
Exploitability depends entirely on whether `abort_if_multisig_payload_mismatch_enabled` is active for the deployment being assessed. If it is enabled on current mainnet, this specific path is closed for full-payload transactions (though the underlying design gap — approvals bound to sequence number, not payload — remains a latent risk if the flag were ever disabled or if a different execution entry point omits the check). I could not verify the current on-chain/mainnet activation status of this flag from the indexed code alone (the flag is referenced in `features.move`, but the deployed activation state requires on-chain governance data not present in the repo index).

### Recommendation
- Short term: Make the full-payload/execution-payload equality check for `transaction.payload.is_some()` unconditional (remove the feature-flag gate), matching the unconditional hash-check behavior, so that "enough approvals" always refers to the exact payload being executed.
- Alternatively, bind vote records to a payload/content hash rather than only to `sequence_number`, so a vote cannot be reinterpreted as approval for a different payload.
- Long term: Add Move Prover specs / fuzzing asserting that `successful_transaction_execution_cleanup` can never run with a `transaction_payload` argument that differs (post-hash) from what was approved, across all feature-flag states.

### Proof of Concept
1. Owner A and Owner B form a 2-of-2 multisig account.
2. Owner A calls `create_transaction(A, multisig_addr, benign_payload)` — this stores `benign_payload` fully on-chain and auto-registers A's approval [2](#0-1) .
3. Owner B reviews `benign_payload` (e.g., "transfer 1 APT to A") and calls `approve_transaction(B, multisig_addr, seq)`.
4. On a network/state where `abort_if_multisig_payload_mismatch_enabled` is not enabled, Owner A submits a `MultisigTransaction` execution with a *different* payload — e.g., `add_owners([attacker])` or a large-value `coin::transfer` to attacker — as the actual entry-function payload.
5. `validate_multisig_transaction` passes because `transaction.payload_hash.is_none()` (skips hash check) and the full-payload mismatch check is skipped (feature disabled), while `num_approvals >= num_signatures_required` is satisfied from the votes on the sequence number.
6. The malicious payload executes as the multisig account signer, reassigning ownership/control or moving multisig-held funds without true quorum over that specific operation.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1171-1183)
```text
        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);

        let creator = address_of(owner);
        let transaction = MultisigTransaction {
            payload: option::some(payload),
            payload_hash: option::none<vector<u8>>(),
            votes: simple_map::create<address, bool>(),
            creator,
            creation_time_secs: now_seconds(),
        };
        add_transaction(creator, multisig_account, transaction);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1225-1253)
```text
    public entry fun vote_transanction(
        owner: &signer, multisig_account: address, sequence_number: u64, approved: bool) {
        assert_multisig_account_exists(multisig_account);
        let multisig_account_resource = borrow_global_mut<MultisigAccount>(multisig_account);
        assert_is_owner_internal(owner, multisig_account_resource);

        assert!(
            multisig_account_resource.transactions.contains(sequence_number),
            error::not_found(ETRANSACTION_NOT_FOUND),
        );
        let transaction = multisig_account_resource.transactions.borrow_mut(sequence_number);
        let votes = &mut transaction.votes;
        let owner_addr = address_of(owner);

        if (votes.contains_key(&owner_addr)) {
            *votes.borrow_mut(&owner_addr) = approved;
        } else {
            votes.add(owner_addr, approved);
        };

        emit(
            Vote {
                multisig_account,
                owner: owner_addr,
                sequence_number,
                approved,
            }
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1328-1385)
```text
    fun validate_multisig_transaction(
        owner: &signer, multisig_account: address, payload: vector<u8>) {
        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);
        let sequence_number = last_resolved_sequence_number(multisig_account) + 1;
        assert_transaction_exists(multisig_account, sequence_number);

        if (features::multisig_v2_enhancement_feature_enabled()) {
            assert!(
                can_execute(address_of(owner), multisig_account, sequence_number),
                error::invalid_argument(ENOT_ENOUGH_APPROVALS),
            );
        }
        else {
            assert!(
                can_be_executed(multisig_account, sequence_number),
                error::invalid_argument(ENOT_ENOUGH_APPROVALS),
            );
        };

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
