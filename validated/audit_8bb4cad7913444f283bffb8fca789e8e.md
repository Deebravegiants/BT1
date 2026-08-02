### Title
Multisig-approved payload substitution due to feature-gated payload verification — (`File: aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`validate_multisig_transaction()`, the VM-invoked prologue function that authorizes execution of a multisig-owned account's approved transaction, only checks that the payload actually being executed matches the payload that owners voted on when the feature flag `abort_if_multisig_payload_mismatch_enabled` is turned on **and** the submitted payload is non-empty. When that condition isn't met, an executor can submit a different entry-function payload than the one the owners approved, while the vote/quorum bookkeeping is keyed only by `sequence_number`, not by the payload's content.

### Finding Description
Aptos's `multisig_account` module lets owners vote on a `MultisigTransaction` identified by a `sequence_number`. When created via `create_transaction()`, the full `payload` is stored on-chain and owners are expected to inspect and approve exactly that payload [1](#0-0) .

Execution is authorized by `validate_multisig_transaction()`, called from the VM's `run_multisig_prologue` before the transaction actually runs [2](#0-1) . This function:
1. Confirms enough owner approvals exist for the pending `sequence_number` [3](#0-2) .
2. Only *conditionally* checks whether the `payload` supplied at execution time (`payload: vector<u8>`, sourced from the executor's own signed transaction, i.e. the `executable` field they control) matches the stored `transaction.payload`:

```move
// aptos-move/framework/aptos-framework/sources/multisig_account.move:1373-1384
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
``` [4](#0-3) 

This is structurally the same flaw described in the external report: the authorization primitive (owner votes / signature) is bound only to a coarse identifier (`sequence_number`, analogous to `module`+`moduleInitData`), but a security-relevant parameter that determines *what actually executes* (the `payload`, analogous to `moduleType`) is not unconditionally covered by that authorization. The VM independently derives `provided_payload` from the executor's own transaction executable and only reconciles it against the on-chain-approved payload behind a feature gate [5](#0-4) .

Note: only the hash-only creation path (`create_transaction_with_hash`, using `payload_hash`) is unconditionally verified via `sha3_256(payload) == *payload_hash` [6](#0-5) . The full-payload path (`create_transaction`, the common/simpler UX) relies entirely on the feature-gated check.

### Impact Explanation
If `abort_if_multisig_payload_mismatch_enabled` is not active for a given execution path (e.g., not yet enabled, or the executor submits a non-empty payload while some other condition of the gate isn't met), any owner who is permitted to execute the transaction can submit a **different** entry-function payload (e.g., a coin/fungible-asset transfer or mint to an attacker-controlled address, or an admin call reassigning control) while quorum bookkeeping still treats it as the vote that was cast for the originally displayed/approved payload. Because the multisig account is itself a resource account that can hold and move APT/fungible assets and call privileged functions on other modules, this allows theft or redirection of multisig-custodied value without genuine authorization — corrupting the "approved payload" custody invariant that owners rely on when voting.

### Likelihood Explanation
Exploitability is entirely conditioned on the on-chain state of the `abort_if_multisig_payload_mismatch_enabled` feature flag (governed by `aptos_framework::features`). I was not able to confirm within the available tool budget whether this flag is enabled by default on current mainnet (`aptos-move/framework/move-stdlib/sources/configs/features.move` references it, but I did not get to read its default-enablement list before running out of iterations). If the flag is enabled on mainnet, this path is not exploitable today; if it is disabled or only conditionally rolled out, this represents a live, unprivileged payload-substitution vector for any account using the full-payload (`create_transaction`) creation flow. This uncertainty should be resolved before treating this as a confirmed live issue.

### Recommendation
- Make payload verification for the full-payload path (`transaction.payload.is_some()`) unconditional, independent of the `abort_if_multisig_payload_mismatch_enabled` feature flag and independent of whether the submitted `payload` is empty.
- Alternatively, bind the vote/approval record itself to a hash of the payload (as is already done for the hash-only creation path) rather than only to `sequence_number`, so that quorum satisfaction is intrinsically tied to the exact payload being executed.
- Confirm and document the current mainnet state of `abort_if_multisig_payload_mismatch_enabled`; if disabled, prioritize enabling it via governance immediately.

### Proof of Concept
Conceptual sequence (dependent on the feature flag being disabled for the executing account/version):
1. Owner A calls `create_transaction(owner_A, multisig_addr, payload_transfer_to_treasury)` — visible on-chain, other owners inspect and approve this payload.
2. Owners B and C call `approve_transaction(..., sequence_number)`, reaching quorum for that `sequence_number`.
3. Owner A (or any owner permitted to execute) submits the actual on-chain transaction with `extra_config.multisig_address = multisig_addr` but an `executable` containing a different `EntryFunction` payload, e.g. `payload_transfer_to_attacker`.
4. `run_multisig_prologue` → `validate_multisig_transaction` checks quorum for `sequence_number` (satisfied) and, because `abort_if_multisig_payload_mismatch_enabled` is false (or payload emptiness bypass applies), skips comparing `payload_transfer_to_attacker` against the stored `payload_transfer_to_treasury`.
5. `execute_multisig_transaction` in the VM proceeds to execute `payload_transfer_to_attacker` as the multisig account signer, moving multisig-custodied funds to the attacker without genuine quorum approval of that specific action [7](#0-6) .

I could not fully verify the exact default value of `abort_if_multisig_payload_mismatch_enabled` on mainnet or the full body of `get_next_transaction_payload()` (which reconciles `provided_payload` with stored payload/hash) within the remaining tool budget — a Devin session with full repo access would be needed to confirm the flag's current enablement and finalize whether this is exploitable today versus already mitigated by governance-enabled feature flags.

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1332-1353)
```text
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

**File:** aptos-move/aptos-vm/src/transaction_validation.rs (L419-478)
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

    session
        .execute_function_bypass_visibility(
            &MULTISIG_ACCOUNT_MODULE,
            VALIDATE_MULTISIG_TRANSACTION,
            vec![],
            serialize_values(&vec![
                MoveValue::Signer(txn_data.sender),
                MoveValue::Address(multisig_address),
                MoveValue::vector_u8(provided_payload),
            ]),
            &mut UnmeteredGasMeter,
            traversal_context,
            module_storage,
        )
        .map(|_return_vals| ())
        .map_err(expect_no_verification_errors)
        .or_else(|err| convert_prologue_error(err, log_context))
```

**File:** aptos-move/aptos-vm/src/aptos_vm.rs (L1300-1348)
```rust
        // Step 1: Obtain the payload. If any errors happen here, the entire transaction should fail
        let invariant_violation_error = || {
            PartialVMError::new(StatusCode::UNKNOWN_INVARIANT_VIOLATION_ERROR)
                .with_message("MultiSig transaction error".to_string())
                .finish(Location::Undefined)
        };
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
            TransactionExecutableRef::Encrypted => {
                // Decryption failed. Return an error so the caller runs the failure epilogue,
                // which increments the sequence number and charges gas.
                return Err(VMStatus::error(
                    StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT,
                    Some(
                        "Encrypted multisig transaction decryption failed; payload not available"
                            .to_string(),
                    ),
                ));
            },
        };
```

**File:** aptos-move/aptos-vm/src/aptos_vm.rs (L1469-1518)
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
