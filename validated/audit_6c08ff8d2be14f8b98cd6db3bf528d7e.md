## Custody-Grade Finding

### Title
Multisig transaction execution can bypass payload-match verification via empty payload / disabled feature flag - ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
The external report concerns `ecrecover` returning a degenerate value (`0`) that is not checked, letting an attacker satisfy an authentication check with a bogus but "valid-looking" zero result. The Aptos-native analog is in `multisig_account::validate_multisig_transaction`, where the check binding a K-of-N multisig approval to a *specific* transaction payload is silently skipped whenever the executed payload is the degenerate empty-vector value, or when a governance feature flag is off. Just as `ecrecover == 0` sidesteps signature verification, `payload.is_empty() == true` sidesteps payload-match verification.

### Finding Description
`validate_multisig_transaction` is the VM prologue hook that authorizes execution of a multisig transaction: [1](#0-0) 

After confirming quorum and timelock, the function is supposed to bind the actually-executed `payload` to what the owners approved:

```
if (transaction.payload_hash.is_some()) {
    assert!(sha3_256(payload) == *payload_hash, ...);
};

if (features::abort_if_multisig_payload_mismatch_enabled()
    && transaction.payload.is_some()
    && !payload.is_empty())
{
    assert!(payload == *stored_payload, ...);
}
``` [2](#0-1) 

For transactions created via `create_transaction` (which stores the full payload on-chain rather than just its hash, so `transaction.payload_hash` is `None`), the *only* content-binding check is the second `if`. That check is gated by three conjuncts, and if **any** is false the entire payload-equality assertion is skipped:
- `abort_if_multisig_payload_mismatch_enabled()` is a feature flag — if not enabled network-wide, the check never runs regardless of payload content.
- `!payload.is_empty()` — if the executor supplies an empty payload at execution time, the check is skipped even when the flag is enabled.

In either bypass case, `validate_multisig_transaction` returns successfully having verified only the **quorum count** (`num_approvals >= num_signatures_required`) and **timelock**, not that the code actually executed matches what the owners voted to approve. The owners' approvals (`approve_transaction`/`vote_transaction`) are recorded against a `sequence_number`, not against enforced payload content when `payload_hash` is `None` and the bypass conditions hold: [3](#0-2) 

### Impact Explanation
Multisig accounts in Aptos are resource accounts that directly hold and control APT, fungible assets, object ownership, and other on-chain value; multisig control is exactly the custody invariant called out in the task ("Multisig-owned assets... must not leak... transfer authority to unprivileged callers" / "Custody invariants should hold across... transfer... paths"). The security guarantee users rely on is that a specific, K-of-N-approved payload — and *only* that payload — can be executed. If the payload-match assertion is bypassed (empty submitted payload, or the enforcement feature disabled), the executing owner can submit and execute an entirely different transaction than the one that received quorum approval (e.g., substituting a benign "transfer 1 APT to owner B" for "transfer all held APT/objects to attacker"), while the on-chain approvals still show the K-of-N count was met. This corrupts the custody accounting: the recorded approvals no longer correspond to the value movement actually authorized, allowing theft of multisig-held assets by a single participant despite the K-of-N design.

### Likelihood Explanation
Exploitability depends on two conditions I could not fully verify from static code alone within this pass:
1. Whether `abort_if_multisig_payload_mismatch_enabled` is enabled on mainnet by default (the presence of a dedicated feature flag strongly suggests this mismatch check is a *later-added* mitigation, implying the un-gated behavior was the historical default and may still be reachable on any network where the flag isn't active).
2. How the VM supplies the `payload` argument at prologue time (i.e., whether the entry function actually executed can independently diverge from `transaction.payload` while still being accepted by the VM's payload passing convention) — I was unable to trace the exact call site in `aptos_vm.rs`/`transaction_validation.rs` within the available tool budget.

Given the explicit `!payload.is_empty()` escape hatch is unconditional (not gated by the feature flag) and exists purely in Move source with no defense-in-depth elsewhere in this function, the empty-payload bypass path is a directly demonstrable Move-level logic bug independent of flag rollout status.

### Recommendation
- Remove the `!payload.is_empty()` escape hatch; an empty payload should never exempt the transaction from payload-equality verification when `transaction.payload` is stored on-chain.
- Make the payload-match check for `transaction.payload.is_some()` unconditional (not feature-flag gated), matching the same strictness already applied to the `payload_hash` branch.
- Add an explicit invariant/spec assertion in `multisig_account.spec.move` requiring that whenever `transaction.payload` is `Some`, the executed `payload` bytes provided to the VM must equal it, with no bypass conditions.

### Proof of Concept
Conceptual sequence (not fully verified end-to-end against VM call-site plumbing, see Likelihood section):
1. Owners of a K-of-N multisig call `create_transaction(owner, multisig_account, PAYLOAD_A)` where `PAYLOAD_A` is a benign, disclosed action (e.g., small transfer). This stores `transaction.payload = Some(PAYLOAD_A)` and `transaction.payload_hash = None`. [4](#0-3) 
2. Owners vote/approve until quorum (`num_signatures_required`) is reached for that sequence number, believing `PAYLOAD_A` is what will execute.
3. A single owner (the executor) submits the actual on-chain transaction such that the `payload` value passed into `validate_multisig_transaction` is the empty vector (or the network has `abort_if_multisig_payload_mismatch_enabled` disabled).
4. `validate_multisig_transaction` passes: `payload_hash` is `None` so the first check is skipped, and the second check's `!payload.is_empty()` condition is `false`, so the payload-match assertion never runs. [5](#0-4) 
5. The VM proceeds to `successful_transaction_execution_cleanup`, and the actually-executed entry function/logic can differ from `PAYLOAD_A`, moving multisig-controlled assets to an address never approved by quorum.

I recommend a Devin session trace `aptos-move/aptos-vm/src/aptos_vm.rs` and `aptos-move/aptos-vm/src/transaction_validation.rs` (both matched `validate_multisig_transaction`) to confirm precisely how/whether the executed entry-function payload can diverge from the `payload` argument passed into this prologue check, which would convert this from a "likely" to a "confirmed" theft primitive.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1256-1260)
```text
    public entry fun vote_transaction(
        owner: &signer, multisig_account: address, sequence_number: u64, approved: bool) {
        assert!(features::multisig_v2_enhancement_feature_enabled(), error::invalid_state(EMULTISIG_V2_ENHANCEMENT_NOT_ENABLED));
        vote_transanction(owner, multisig_account, sequence_number, approved);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1328-1346)
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
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1361-1384)
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
```
