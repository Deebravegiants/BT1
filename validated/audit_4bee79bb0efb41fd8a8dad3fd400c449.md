## Title
Multisig transaction execution can run an arbitrary unapproved payload instead of the voted-on payload when `AbortIfMultisigPayloadMismatch` is not enabled - (`File: aptos-move/framework/aptos-framework/sources/multisig_account.move`)

## Summary
This mirrors the Arbitrum bug's core invariant: a privileged state (there, an unrivalled timer; here, a quorum of owner approvals) is bound to one specific claimed entity (an approved payload), but the on-chain validation only checks a *structural* condition (approval count / sequence number) rather than an exact identity match to the thing that was actually authorized, so a different, unapproved entity can consume that privilege.

## Finding Description
`multisig_account::create_transaction` stores the full `payload` on-chain (`payload: option::some(payload)`, `payload_hash: option::none()`), and owners vote/approve based on that stored payload [1](#0-0) .

At execution time, the VM computes the `provided_payload` from the entry function/script actually included in the *executing transaction's executable* (not from the stored `MultisigAccount.transactions[seq].payload`) and passes it into `validate_multisig_transaction` [2](#0-1) .

`validate_multisig_transaction` checks quorum/timelock, and then:
```
if (transaction.payload_hash.is_some()) { assert!(sha3_256(payload) == *payload_hash, ...); };
if (features::abort_if_multisig_payload_mismatch_enabled()
    && transaction.payload.is_some()
    && !payload.is_empty()) {
    assert!(payload == *stored_payload, ...);
}
``` [3](#0-2) 

When the transaction was created via `create_transaction` (full payload stored, `payload_hash` is `none`), the *only* guard that the executed content matches the approved content is the `abort_if_multisig_payload_mismatch_enabled()` feature-gated branch. If that feature is not enabled, `validate_multisig_transaction` never compares the `provided_payload` in the executing transaction to `transaction.payload` that owners actually approved. Execution then proceeds to run whatever entry function/script is in the *executor's own transaction* under the multisig account's signer, via `execute_multisig_payload` → `validate_and_execute_entry_function`/`validate_and_execute_script`, using the multisig account as signer [4](#0-3) . This is the same class of flaw as the C4 report: authority (approvals accumulated for a specific claimed payload) is checked structurally (quorum count + sequence number) and is inherited by whatever payload the executor supplies, rather than being cryptographically bound to the exact approved content, unless an optional feature flag closes the gap.

## Impact Explanation
If `AbortIfMultisigPayloadMismatch` is disabled, any single owner of a k-of-n multisig account who can produce a valid transaction (with a valid sequence number matching the resolved multisig sequence, and enough *other* owners' approvals for *some* prior payload proposal) can execute a completely different entry function/script as the multisig account's signer. Since multisig accounts are resource accounts commonly used to custody APT and fungible assets and to hold admin/upgrade authority over other contracts, this allows an unprivileged (non-quorum-approved) payload — e.g., `aptos_account::transfer` draining funds, or `code::publish_package_txn` replacing modules — to execute with full multisig-account authority. This is a direct custody-grade theft/authority-takeover vector for any live asset or upgrade capability controlled by the multisig account.

## Likelihood Explanation
This depends entirely on whether `AbortIfMultisigPayloadMismatch` is active on mainnet. It is a governance-controlled feature flag (`AptosFeatureFlag::ABORT_IF_MULTISIG_PAYLOAD_MISMATCH`), and its current activation state on Aptos mainnet could not be confirmed from the repository index alone (the on-chain `Features` bitmap is not represented in source). If the flag is enabled network-wide, this path is closed. If it is disabled or not yet activated for any currently-live multisig account (e.g., during migration windows or on networks that lag governance upgrades), the bypass is fully exploitable by any single owner with a valid sequence number.

## Recommendation
Make the payload-match check for on-chain-stored payloads unconditional (remove the `abort_if_multisig_payload_mismatch_enabled()` gate) so that whenever `transaction.payload.is_some()`, the provided execution payload must always equal the stored, voted-on payload, regardless of feature flag state. Alternatively, deprecate the code path that allows execution to proceed without validating equality, and confirm/document the current on-chain activation status of `AbortIfMultisigPayloadMismatch` on mainnet.

## Proof of Concept
Conceptual PoC (cannot be run without live state to confirm the feature flag is disabled):
1. Owner A calls `multisig_account::create_transaction(owner_A, multisig_addr, payload_transfer_1_APT_to_charity)`, storing the full payload on chain.
2. Owners B, C (up to quorum k) call `approve_transaction` for that sequence number, believing they are approving the 1 APT charity transfer.
3. Owner A submits a *different* top-level transaction whose executable is `aptos_account::transfer(multisig_addr_as_signer, attacker, entire_balance)`, targeting the same `multisig_address` and the same resolved `sequence_number`.
4. `run_multisig_prologue` computes `provided_payload` from A's actual submitted executable (the drain transfer), not from the approved payload [5](#0-4) .
5. `validate_multisig_transaction` passes: quorum/timelock checks succeed (based on the *unrelated* stored transaction's votes), `payload_hash` is `none` so that branch is skipped, and if `abort_if_multisig_payload_mismatch_enabled()` is false, the stored-payload-equality branch is also skipped entirely.
6. `execute_multisig_payload` runs A's drain-transfer entry function with the multisig account as signer, draining the account's full APT balance to the attacker [6](#0-5) .

Confirming exploitability requires verifying the live on-chain status of the `AbortIfMultisigPayloadMismatch` feature flag, which is outside what the repository index can show; a Devin session with access to a live/test network or governance history would be needed to check this definitively.

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

**File:** aptos-move/aptos-vm/src/aptos_vm.rs (L1305-1335)
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
            TransactionExecutableRef::Script(script) => {
                if !self.features().is_multisig_script_enabled() {
                    let s = VMStatus::error(
                        StatusCode::FEATURE_UNDER_GATING,
                        Some("Multisig script payload is not enabled".to_string()),
                    );
                    return Ok((s, discarded_output(StatusCode::FEATURE_UNDER_GATING)));
                }
                bcs::to_bytes(&MultisigTransactionPayload::Script(script.clone()))
                    .map_err(|_| invariant_violation_error())?
            },
```

**File:** aptos-move/aptos-vm/src/aptos_vm.rs (L1468-1517)
```rust
    fn execute_multisig_payload(
        &self,
        resolver: &impl AptosMoveResolver,
        code_storage: &impl AptosCodeStorage,
        mut session: UserSession,
        gas_meter: &mut impl AptosGasMeter,
        traversal_context: &mut TraversalContext,
        multisig_address: AccountAddress,
        payload: &MultisigTransactionPayload,
        change_set_configs: &ChangeSetConfigs,
        trace_recorder: &mut impl TraceRecorder,
    ) -> Result<UserSessionChangeSet, VMStatus> {
        let serialized_signers =
            SerializedSigners::new(vec![serialized_signer(&multisig_address)], None);

        // If txn args are not valid, we'd still consider the transaction as executed but
        // failed. This is primarily because it's unrecoverable at this point.
        session.execute(|session| match payload {
            MultisigTransactionPayload::EntryFunction(entry_function) => self
                .validate_and_execute_entry_function(
                    code_storage,
                    session,
                    &serialized_signers,
                    gas_meter,
                    traversal_context,
                    entry_function,
                    trace_recorder,
                ),
            MultisigTransactionPayload::Script(script) => self.validate_and_execute_script(
                session,
                &serialized_signers,
                code_storage,
                gas_meter,
                traversal_context,
                script,
                trace_recorder,
            ),
        })?;

        // Resolve any pending module publishes in case the multisig transaction is deploying
        // modules.
        self.resolve_pending_code_publish_and_finish_user_session(
            session,
            resolver,
            code_storage,
            gas_meter,
            traversal_context,
            change_set_configs,
        )
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
