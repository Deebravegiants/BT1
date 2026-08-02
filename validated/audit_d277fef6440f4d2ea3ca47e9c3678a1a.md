### Title
Multisig transaction execution can bypass on-chain payload matching, letting the executor swap the approved payload for an arbitrary one - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`multisig_account.move` implements Aptos's enhanced multisig standard, where a resource account holds assets and is only controllable through owner-approved `MultisigTransaction`s. Owners can approve a transaction either by voting on a full payload stored on-chain (`create_transaction`) or on just its hash (`create_transaction_with_hash`). At execution time, the VM calls `validate_multisig_transaction(owner, multisig_account, payload)` with a `payload` supplied by the *executing* owner as part of the actual transaction being run. This is structurally the same trust pattern as the Gondi `callbackData` bug: several parties (co-owners) approve one thing, while a separate, unsigned/unverified blob (`payload`) determines what actually executes.

### Finding Description
In `validate_multisig_transaction` [1](#0-0) , when the transaction was created with the full payload on-chain (`transaction.payload.is_some()`, `transaction.payload_hash.is_none()`), the code that verifies the executor-supplied `payload` matches the stored, owner-approved payload is gated behind a feature flag:

```
if (features::abort_if_multisig_payload_mismatch_enabled()
    && transaction.payload.is_some()
    && !payload.is_empty()
) {
    let stored_payload = transaction.payload.borrow();
    assert!(payload == *stored_payload, error::invalid_argument(EPAYLOAD_DOES_NOT_MATCH));
}
``` [2](#0-1) 

If `abort_if_multisig_payload_mismatch_enabled()` is not enabled on a given network/epoch, this check is entirely skipped whenever a full payload is stored (as opposed to only a hash). All the other checks in the function (`can_execute`/`can_be_executed`, quorum count, timelock) only verify that *enough owners approved a transaction id* - none of them verify that the bytes actually being executed correspond to what those owners approved. The executor-supplied `payload` is the operative transaction payload that gets run as the resource account signer; it is never cryptographically bound to the stored payload unless the flag is on.

This mirrors the report's root cause exactly: co-signers (owners, analogous to the borrower) agree to and approve one thing (the loan terms / a specific payload), but a separate, executor-controlled value (`callbackData` / the execution-time `payload` argument) is what is actually run, and its equivalence to the approved value is either unverified or only optionally verified.

### Impact Explanation
A multisig account is often used to custody APT, fungible assets, resource-account/code-object upgrade authority, etc. If the payload-match check is not enforced:
- Any owner who reaches quorum to *approve* execution of a benign, publicly-visible payload (e.g., "transfer 1 APT to charity") can instead execute a completely different payload at execution time (e.g., "transfer entire multisig balance to attacker", "rotate auth key", "publish malicious code to a co-owned code object"), since the assertion binding execution to the approved content is skipped.
- This breaks the fundamental custody invariant of a k-of-n multisig: that funds/objects/code controlled by the account can only move according to content that k owners actually reviewed and approved.
- The result is theft or owner/authority reassignment of any assets held by the multisig resource account, with no cryptographic signature or on-chain data tying the approved intent to the executed action.

### Likelihood Explanation
This depends entirely on the run-time state of the `abort_if_multisig_payload_mismatch_enabled` feature flag. If it is enabled network-wide, the mismatch is always rejected and the finding is not exploitable. If it is disabled (e.g., not yet activated, rolled back, or disabled for a specific deployment/testnet), the check is fully bypassable by any single owner who is also submitting the execution transaction, with no special privilege beyond being one of the co-owners (the same "unprivileged root cause" pattern as the report). I was not able to fully confirm the current default/activation status of this specific flag within the available context (only partial matches on the flag name were found, without a clear numeric ID and default value in `features.move`), so likelihood should be validated against the target network's actual feature-flag state before treating this as confirmed-exploitable in production.

### Recommendation
Make the payload-match check unconditional and not feature-flag-gated: whenever `transaction.payload.is_some()`, always assert `payload == *stored_payload` (not just when `!payload.is_empty()` and the flag is on). If backward compatibility during the flag's rollout is a concern, the safer default should be "abort on mismatch" rather than "skip verification," i.e., invert the flag's polarity so that omission of the flag fails closed, not open. This ensures that what a quorum of owners approved is cryptographically guaranteed to be exactly what executes, closing the same class of "approved terms vs. executed calldata" mismatch that the external report identified.

### Proof of Concept
Conceptual sequence (would need to be validated against the live status of `abort_if_multisig_payload_mismatch_enabled`):
1. `owner_1` creates a 2-of-3 multisig account holding APT, and calls `create_transaction(owner_1, multisig, payload_A)` where `payload_A` is a benign entry function call, e.g., `aptos_account::transfer(charity, 1_00000000)`. This stores `payload_A` on-chain (`transaction.payload = some(payload_A)`, `payload_hash = none`). [3](#0-2) 
2. `owner_2` reviews `payload_A` on-chain and calls `approve_transaction(owner_2, multisig, seq)`, reaching the 2-of-3 quorum.
3. `owner_1` (or any owner permitted to execute) submits the actual on-chain `MultisigTransaction` execution with a *different* payload, `payload_B` = drain the entire multisig APT balance to their own address.
4. In `validate_multisig_transaction`, quorum/timelock checks pass (2 approvals recorded against sequence number `seq`); since `transaction.payload_hash` is `none`, the hash check is skipped; and if `abort_if_multisig_payload_mismatch_enabled()` is false, the direct payload-equality check is also skipped entirely. [4](#0-3) 
5. `payload_B` executes as the multisig resource account signer, draining funds that `owner_2` never approved.

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
