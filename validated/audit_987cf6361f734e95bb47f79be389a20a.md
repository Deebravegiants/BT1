Based on my investigation, I found a genuine custody-relevant analog in `aptos_framework::multisig_account`, distinct from the Sablier gas-griefing issue but sharing the same root theme: **an unprivileged/partial actor can cause the actually-executed action to diverge from what was approved**, corrupting custody accounting for the multisig-controlled account.

I want to flag upfront: I could not fully confirm the *current default on-chain state* of the `ABORT_IF_MULTISIG_PAYLOAD_MISMATCH` feature flag on Aptos mainnet (i.e., whether it is enabled or still disabled by default) within my available tool budget — this materially affects likelihood, so I call that out explicitly below.

### Title
Multisig transaction execution payload is not verified against the approved payload unless `abort_if_multisig_payload_mismatch` feature is enabled - ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
`multisig_account::create_transaction` stores the **full transaction payload** on-chain and owners vote (`approve_transaction`/`vote_transanction`) on that stored payload by sequence number [1](#0-0) . However, at execution time, the VM-invoked prologue `validate_multisig_transaction` receives a separate `payload: vector<u8>` argument (the payload of the outer submitted transaction) and only checks it against the stored, approved payload when the feature `abort_if_multisig_payload_mismatch_enabled()` is turned on [2](#0-1) . If that feature is not enabled, quorum/timelock checks are validated (`can_execute`, `num_signatures_required`, `can_execute_with_timelock`) but the actual bytes that will be executed as the multisig account are never checked against what owners approved.

### Finding Description
The approval flow only binds votes to a `sequence_number`, not to the payload content, for on-chain-stored-payload transactions:
- `vote_transanction` records approval keyed by `sequence_number` only [3](#0-2) .
- `validate_multisig_transaction` verifies quorum/timelock for that `sequence_number` [4](#0-3) .
- The binding check between the *approved* `transaction.payload` and the *actually submitted execution* `payload` argument only fires under the `abort_if_multisig_payload_mismatch_enabled` feature gate [2](#0-1) .

Note the `payload_hash` branch (used by `create_transaction_with_hash`) is checked unconditionally [5](#0-4) , so the gap only applies to the full-payload-on-chain path created via `create_transaction`, which the module's own documentation recommends for "decentralization/transparency" [6](#0-5) .

If the feature is off, any owner who can reach quorum for *some* proposed transaction at the next sequence number can execute an entirely different entry-function payload as the multisig account's signer — e.g. swap a benign-looking, approved "pay vendor X" transaction for "transfer all APT/objects to attacker" or "add attacker as owner" — because nothing ties the executed bytes to the bytes the owners actually reviewed and voted on.

### Impact Explanation
The multisig account is a resource account that can hold APT, fungible-asset stores, and object ownership, and its signer authority is exactly what governs those assets [7](#0-6) . Executing arbitrary, unapproved payloads as this signer is a direct custody break: theft/misdirection of APT or object-held assets, or reassignment of multisig ownership/control, satisfies "Supply or custody accounting corruption that moves value to the wrong holder" and "Unauthorized takeover of ... multisig control." This would be Critical if the feature is disabled by default on mainnet.

### Likelihood Explanation
Likelihood hinges entirely on whether `abort_if_multisig_payload_mismatch_enabled` is active. I was unable to conclusively verify the mainnet default within the available searches (the flag exists in `features.move`/`aptos_features.rs` and is referenced in `aptos_vm.rs`/`transaction_validation.rs`, suggesting it is treated as a rollout-gated mitigation rather than baked-in enforcement). If it is still disabled anywhere (e.g., non-mainnet networks, or was only recently enabled on mainnet with existing multisigs created before the fix), the gap is live. This should be treated as **unverified/needs confirmation** rather than a confirmed live exploit — I recommend a background session with full repo/genesis-config access to check the feature's on-chain enabled status and history.

### Recommendation
Make the payload-match check unconditional (not feature-gated) for any `MultisigTransaction` where `transaction.payload.is_some()`, so execution can never diverge from what owners approved, independent of feature flag state. Alternatively, deprecate the full-on-chain-payload path in favor of hash-based creation (already unconditionally checked) until the flag is permanently enabled network-wide.

### Proof of Concept
1. Owner A calls `create_transaction(owner_A, multisig, payload_A)` where `payload_A` = "transfer 10 APT to vendor," which is stored fully on-chain and auto-approved by A [1](#0-0) .
2. Owners B, C call `approve_transaction` reviewing `payload_A` in `get_transaction`, reaching quorum for that `sequence_number`.
3. On a network/config where `abort_if_multisig_payload_mismatch_enabled()` is false, malicious owner A submits the actual execution transaction with `payload_B` = "transfer all APT to attacker" (different bytes, same `sequence_number`).
4. `validate_multisig_transaction` checks quorum/timelock for the sequence number (satisfied) and skips the `payload == stored_payload` check entirely because the feature flag is off [2](#0-1) .
5. The VM executes `payload_B` as the multisig account signer, diverting funds without genuine quorum approval of that content.

If, upon deeper investigation with full repo access, the flag is confirmed enabled unconditionally on mainnet with no legacy multisig accounts affected, this finding should be downgraded to informational/already-mitigated.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1-13)
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
///
/// Transactions need to be executed in order of creation, similar to transactions for a normal Aptos account (enforced
/// with account nonce).
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L21-27)
```text
/// 3. To create a new transaction, an owner can call create_transaction with the transaction payload. This will store
/// the full transaction payload on chain, which adds decentralization (censorship is not possible as the data is
/// available on chain) and makes it easier to fetch all transactions waiting for execution. If saving gas is desired,
/// an owner can alternatively call create_transaction_with_hash where only the payload hash is stored. Later execution
/// will be verified using the hash. Only owners can create transactions and a transaction id (incremeting id) will be
/// assigned.
/// 4. To approve or reject a transaction, other owners can call approve() or reject() with the transaction id.
```

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1373-1384)
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
```
