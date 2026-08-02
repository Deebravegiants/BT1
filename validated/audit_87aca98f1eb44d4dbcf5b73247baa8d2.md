## Summary

The Chainlink report's root cause is a **binding failure between the "request" and its "fulfillment"**: an oracle records a request, but at fulfillment time trusts caller-supplied data instead of re-verifying it against what was actually agreed to, so an attacker can substitute malicious content and it still gets accepted/executed.

The closest custody-grade analog in this repository is in Aptos's **k-of-n multisig account execution flow** (`multisig_account.move`), where the *content that owners vote on* and the *content that actually gets executed by the VM* are two independently-supplied values, and the check that they must match is **conditionally gated by a feature flag** rather than unconditionally enforced.

## Finding Description

In `multisig_account::validate_multisig_transaction` (the prologue run by the VM before executing a `Multisig` transaction), owners vote to approve a `MultisigTransaction` whose full payload can be stored on-chain via `create_transaction`: [1](#0-0) 

At execution time, the **actual entry function that the VM will run is not derived from this stored payload** — it comes from the `executable: TransactionExecutableRef` field of the transaction the *executor* independently constructs and submits: [2](#0-1) 

The prologue's job is to verify that this executor-supplied `provided_payload` matches what owners approved. For the hash-only path (`create_transaction_with_hash`), this check is unconditional: [3](#0-2) 

But for the **full-payload-stored path** (`create_transaction`), the equivalent verification is only performed **if the feature flag `abort_if_multisig_payload_mismatch_enabled` is on**: [4](#0-3) 

If that feature is disabled (or not yet activated on a given network), the branch is skipped entirely — `num_approvals` is still checked against `num_signatures_required` for the *originally stored* transaction record, but nothing constrains the **actual bytes that will be executed by the VM** to match what owners voted on. The executor can submit an `EntryFunction` executable with arbitrary arguments (e.g., a different recipient address or a different amount than the one owners approved), and it will pass the prologue and be executed as the multisig account signer, using the votes that were cast for a *different, unrelated* transaction.

This is structurally identical to the Chainlink bug: the "request" (owners' approval of a specific payload) and the "fulfillment" (VM execution of executor-chosen bytes) are only bound together by an optional, flag-gated equality check instead of an invariant enforced at the protocol level.

## Impact Explanation

This breaks the core custody invariant of the multisig-account model: that funds/authority held by a `k`-of-`n` multisig can only move according to a payload that actually received `k` approvals. Under the described condition, a single owner (or any account able to author transactions on the multisig's behalf once quorum is nominally recorded) can redirect an approved transfer to an arbitrary address or amount, resulting in **theft or arbitrary reassignment of any asset custodied by the resource-account-backed multisig** (APT, coins, fungible assets, or any entry function callable with the multisig signer, including object/FA ownership transfers). This meets the "theft" and "supply/custody accounting corruption that moves value to the wrong holder" custody-impact criteria.

## Likelihood Explanation

The likelihood depends entirely on the on-chain state of the `abort_if_multisig_payload_mismatch_enabled` feature flag, which I could not verify from the indexed code (no genesis/mainnet feature-activation list was found in the search). If this flag is not activated on a given deployment (e.g., a newly forked chain, an L2, a devnet, or if it is rolled back/not yet enabled), every full-payload multisig account on that chain is exposed. Since the flag's very existence and the accompanying comments ("If the transaction payload is stored on chain and there is a provided payload, verify...") indicate this check was retrofitted rather than foundational, its default/rollout status is a critical unknown that should be confirmed before treating this as exploitable on Aptos mainnet today.

## Recommendation

Make payload-matches-approval verification for the full-payload path **unconditional** (remove the feature-flag gate, matching the unconditional hash-check for the hash-only path), or reject any `EntryFunction`/`Script` executable whose content differs from `transaction.payload` regardless of feature state. Alternatively, bind the VM's actual executable to the stored payload directly (ignore executor-supplied payload bytes) whenever a full payload exists on-chain, so there is no path where votes for one payload can be spent on execution of another.

## Proof of Concept

1. Owners `O1`,`O2` create a 2-of-2 multisig account with a resource-account-held APT balance.
2. `O1` calls `create_transaction(owner=O1, multisig_account, payload=EntryFunction(aptos_account::transfer(recipient=O1, amount=10)))`.
3. `O2` calls `approve_transaction` for that sequence number, reaching the 2-of-2 threshold for the *stored* transaction.
4. `O1` (the executor) submits a `Multisig` transaction whose `transaction_executable` is `EntryFunction(aptos_account::transfer(recipient=Attacker, amount=<entire balance>))` instead of the approved payload.
5. If `abort_if_multisig_payload_mismatch_enabled` is not active, `validate_multisig_transaction` at [4](#0-3)  skips the mismatch check (the `if` condition is false), `num_approvals >= num_signatures_required` still passes (checked against the *stored* transaction's votes), and the VM executes the attacker-chosen `executable`, draining the multisig account to `Attacker` instead of `O1`.

**Caveat / what remains unverified:** I was not able to confirm, from the indexed files, the mainnet activation status of `abort_if_multisig_payload_mismatch_enabled` (no genesis feature-flag list was found in this pass). This is essential to determine whether the gap is currently live or has already been closed by feature activation; without that confirmation this should be treated as a conditional finding pending verification of the flag's on-chain state.

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

**File:** aptos-move/aptos-vm/src/transaction_validation.rs (L419-460)
```rust
pub(crate) fn run_multisig_prologue(
    session: &mut SessionExt<impl AptosMoveResolver>,
    module_storage: &impl ModuleStorage,
    txn_data: &TransactionMetadata,
    executable: TransactionExecutableRef,
    multisig_address: AccountAddress,
    features: &Features,
    log_context: &AdapterLogSchema,
    traversal_context: &mut TraversalContext,
) -> Result<(), VMStatus> {
    let unreachable_error = VMStatus::error(StatusCode::UNREACHABLE, None);
    // Note[Orderless]: Earlier the `provided_payload` was being calculated as bcs::to_bytes(MultisigTransactionPayload::EntryFunction(entry_function)).
    // So, converting the executable to this format.
    let provided_payload = match executable {
        TransactionExecutableRef::EntryFunction(entry_function) => bcs::to_bytes(
            &MultisigTransactionPayload::EntryFunction(entry_function.clone()),
        )
        .map_err(|_| unreachable_error.clone())?,
        TransactionExecutableRef::Empty => {
            if features.is_abort_if_multisig_payload_mismatch_enabled() {
                vec![]
            } else {
                bcs::to_bytes::<Vec<u8>>(&vec![]).map_err(|_| unreachable_error.clone())?
            }
        },
        TransactionExecutableRef::Script(script) => {
            if !features.is_multisig_script_enabled() {
                return Err(VMStatus::error(
                    StatusCode::FEATURE_UNDER_GATING,
                    Some("Multisig script payload is not enabled".to_string()),
                ));
            }
            bcs::to_bytes(&MultisigTransactionPayload::Script(script.clone()))
                .map_err(|_| unreachable_error.clone())?
        },
        TransactionExecutableRef::Encrypted => {
            return Err(VMStatus::error(
                StatusCode::FEATURE_UNDER_GATING,
                Some("Encrypted payload not supported for multisig transactions".to_string()),
            ));
        },
    };
```
