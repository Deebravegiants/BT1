# Finding: Multisig payload substitution allows an executing owner to run an unapproved transaction

### Title
Multisig transaction approval is not bound to a specific payload when the feature flag is off, allowing payload substitution at execution time - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
`multisig_account.move` lets owners approve a `MultisigTransaction` by voting on a transaction id, then execute it later. When the full payload is stored on-chain (via `create_transaction`), the on-chain approval is supposed to be scoped to that exact payload. However, the binding between "the payload owners voted for" and "the payload actually executed" is only enforced when the feature flag `abort_if_multisig_payload_mismatch_enabled` is turned on. This mirrors the seed bug class exactly: a broad authorization (k-of-n owner approval / whitelisting the multisig account to run *a* transaction) is not cryptographically/structurally bound to one specific set of call parameters, so whoever triggers execution can substitute a different payload than the one that was actually approved.

### Finding Description
`validate_multisig_transaction` (called by the VM prologue for `MultisigTransaction` execution) receives a `payload: vector<u8>` argument supplied by the executing owner's transaction, and validates it against the on-chain stored transaction: [1](#0-0) 

- If the multisig transaction was created with `create_transaction_with_hash` (only a `sha3_256` hash is stored, `payload_hash.is_some()`), the provided payload is verified against the hash — this path is safe. [2](#0-1) 

- If the multisig transaction was created with `create_transaction` (the **full payload** is stored on-chain, `transaction.payload.is_some()`, `payload_hash` is `none`), the check that the provided execution `payload` argument matches the stored `transaction.payload` is **only performed when `features::abort_if_multisig_payload_mismatch_enabled()` returns true**: [3](#0-2) 

- The `create_transaction` function itself stores the full approved payload: [4](#0-3) 

When the feature flag is disabled (or on any deployment where it has not been activated), there is **no check at all** tying the `payload` argument supplied at execution time to the payload that owners actually voted `num_signatures_required` approvals for. The approval/vote mechanism (`vote_transanction`, `can_execute`) only checks that *a* transaction at the given `sequence_number` has enough approvals — it never re-validates the content of what gets executed in this branch: [5](#0-4) 

This is structurally identical to the seeded bug: the multisig owners' signatures/votes act as a broad "whitelist" that authorizes *a* transaction execution slot (the sequence number), not a specific set of parameters, and the executing party can swap in arbitrary parameters at execution time as long as the feature-gated content check is not active.

### Impact Explanation
If exploited, the executing owner (who only needs to be *one* of the owners, and who is the party paying gas and choosing the runtime `payload` argument) can cause the multisig-controlled resource account to execute an entirely different, non-approved entry function/script — e.g., transferring APT or fungible assets, rotating keys, or reassigning ownership — despite only having obtained the required threshold of approvals for a different, benign-looking payload. This directly corrupts custody: value or control held by the multisig account can be moved to an arbitrary holder chosen unilaterally by the executor, bypassing the k-of-n custody invariant the whole module exists to enforce. This is exactly the "Impact Explanation" bucket of "supply or custody accounting corruption that moves value to the wrong holder."

### Likelihood Explanation
Likelihood depends entirely on whether `abort_if_multisig_payload_mismatch_enabled` is active on a given network/state. The existence of a dedicated, explicitly-named defensive feature flag strongly suggests this exact payload-substitution issue was identified as a real gap and patched behind a flag rather than as an unconditional fix. Any deployment, test network, or historical mainnet state where this flag is not yet enabled is fully exposed. I was not able to confirm from local tooling whether this flag is enabled by default on current mainnet genesis/features configuration (that determination requires cross-referencing `aptos-framework/sources/version` / `features.move` default flags at genesis, which I could not fully verify within available search iterations), so the "mainnet-relevant" status of this specific path is uncertain and should be independently confirmed before treating it as currently live.

### Recommendation
Make the payload-matches-stored-payload check unconditional (remove the feature-flag gate), so any multisig transaction created with `create_transaction` always verifies that the value passed to `validate_multisig_transaction` equals `transaction.payload` when the latter is `Some`, regardless of feature flag state. This closes the parameter-substitution class of vulnerability structurally rather than opportunistically.

### Proof of Concept
Conceptual PoC (Move test), assuming `abort_if_multisig_payload_mismatch_enabled` is disabled:
```
// 2-of-3 multisig created by owner_1 with owner_2, owner_3.
create_with_owners(owner_1, vector[owner_2_addr, owner_3_addr], 2, vector[], vector[]);

// owner_1 proposes a benign payload, e.g. "transfer 10 APT to owner_2".
create_transaction(owner_1, multisig_account, benign_payload);

// owner_2 reviews the benign_payload off-chain and approves it.
approve_transaction(owner_2, multisig_account, 1);

// owner_1 (or anyone with 2 signatures) now submits the actual on-chain
// MultisigTransaction execution with a DIFFERENT payload, e.g.
// "transfer entire balance to attacker_addr" or "rotate auth key".
// Because payload_hash is none and the feature flag is off, the second
// consistency check in validate_multisig_transaction is skipped entirely,
// so malicious_payload executes with the multisig account's authority
// despite never having been seen or approved by owner_2.
```
This mirrors the external report's PoC structure: a valid authorization (there, a signature whitelisting a workflow contract; here, k-of-n owner votes on a transaction id) is reused to execute attacker-chosen parameters instead of the ones actually reviewed and approved.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1164-1183)
```text
    public entry fun create_transaction(
        owner: &signer,
        multisig_account: address,
        payload: vector<u8>,
    ) {
        assert!(payload.length() > 0, error::invalid_argument(EPAYLOAD_CANNOT_BE_EMPTY));

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1188-1208)
```text
    public entry fun create_transaction_with_hash(
        owner: &signer,
        multisig_account: address,
        payload_hash: vector<u8>,
    ) {
        // Payload hash is a sha3-256 hash, so it must be exactly 32 bytes.
        assert!(payload_hash.length() == 32, error::invalid_argument(EINVALID_PAYLOAD_HASH));

        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);

        let creator = address_of(owner);
        let transaction = MultisigTransaction {
            payload: option::none<vector<u8>>(),
            payload_hash: option::some(payload_hash),
            votes: simple_map::create<address, bool>(),
            creator,
            creation_time_secs: now_seconds(),
        };
        add_transaction(creator, multisig_account, transaction);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1328-1360)
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

```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1361-1383)
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
```
