### Title
Multisig transaction execution can bypass payload-match verification when full payload is stored on-chain, allowing execution of an unapproved payload - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`multisig_account::validate_multisig_transaction` (invoked by the VM prologue in `aptos-move/aptos-vm/src/transaction_validation.rs` and `aptos-move/aptos-vm/src/aptos_vm.rs`) is supposed to guarantee that the entry-function payload actually executed by a multisig account is the same payload that owners voted to approve. For transactions created via `create_transaction` (full payload stored on-chain, `payload_hash = none`), the only check that the *executed* payload matches the *approved* payload is gated behind the `abort_if_multisig_payload_mismatch_enabled` feature flag. If that feature is not enabled, an executing owner can submit any entry-function payload at execution time and it will run under the multisig account's authority, counted as approved by the votes cast for a completely different, original proposal.

### Finding Description
`create_transaction` stores the full payload on-chain and leaves `payload_hash` as `option::none`: [1](#0-0) 

`validate_multisig_transaction` (executed by the VM prologue before running the multisig transaction) contains two payload-authenticity checks: [2](#0-1) 

1. If `transaction.payload_hash.is_some()` (i.e., the transaction was created via `create_transaction_with_hash`), the provided execution payload is hashed and compared to the stored hash — this check always runs.
2. If instead the full payload was stored on-chain (`transaction.payload.is_some()`, `payload_hash` is `none`), the code only compares the provided execution payload against the stored payload when the feature `features::abort_if_multisig_payload_mismatch_enabled()` is turned on. If that feature is disabled, **no comparison is performed at all** in this branch.

This mirrors the external bug's structure exactly: a value that determines what actually gets executed (here, the entry-function payload; there, the `protocol` enum choosing the transfer function) is not authenticated/bound to what the approving parties (owners) signed off on — the "signature" (owner votes) covers only the sequence number / vote record, not a verified check against the actual bytes executed, unless a specific opt-in feature is on.

The consequence: owners vote to approve a benign payload (e.g., "transfer X APT to Alice"). Any single owner with execution rights can then submit `execute_multisig_transaction` (see `aptos-move/aptos-vm/src/aptos_vm.rs`, `execute_multisig_transaction`, around line 1274) with a `TransactionExecutableRef::EntryFunction` containing an entirely different entry function/arguments (e.g., "transfer all APT to attacker" or "rotate auth key to attacker", any entry function the multisig account is authorized to call). Because the feature gate is off, the execution proceeds using the multisig account's signer, corrupting custody of whatever assets that multisig account controls (APT, fungible assets, objects it owns, etc.) without the quorum having actually approved the executed action. [3](#0-2) 

### Impact Explanation
This breaks the core custody invariant of the multisig-account standard: "the executor must run only what the required quorum of owners approved." If exploitable (i.e., if `abort_if_multisig_payload_mismatch_enabled` is not universally enabled on mainnet or can be toggled/is disabled for some accounts/epoch), any account owner able to trigger execution can redirect the multisig's authority to an arbitrary entry function call — including transferring away APT/fungible assets/objects held by the resource account backing the multisig, rotating keys, or reassigning ownership of resources the multisig controls. This is a full custody bypass of a privileged control structure (multisig-owned assets), matching the "unauthorized takeover of multisig control" and "theft of asset" impact classes in the custody gate.

### Likelihood Explanation
Exploitability is entirely contingent on the on-chain state of the `abort_if_multisig_payload_mismatch_enabled` feature flag, which I could not fully confirm is enabled by default/permanently on mainnet from the available code index — the flag is defined in `aptos-move/framework/move-stdlib/sources/configs/features.move` and referenced in `aptos-move/aptos-release-builder/src/components/feature_flags.rs`, but I was not able to retrieve those file contents to determine default/mainnet activation status due to index limits. If the feature has already been enabled on mainnet and cannot be disabled, this is not exploitable today; if it is still gated/optional or was only recently enabled, it represents a live custody bypass for any multisig account created (or transacting) while the flag was off. This uncertainty means the finding should be treated as **conditional** — its real-world severity depends entirely on feature-flag rollout status that I cannot verify with the tools available.

### Recommendation
Make the payload-match check for full-payload-stored transactions unconditional (not feature-gated), i.e., always assert `payload == *stored_payload` when `transaction.payload.is_some()` and the provided payload is non-empty, regardless of `abort_if_multisig_payload_mismatch_enabled`. Alternatively, deprecate/reject `TransactionExecutableRef::Empty`/mismatched-payload flows entirely for `create_transaction`-based proposals so execution can never diverge from the voted-on payload. Also confirm (via governance/feature-flag records, not available in this index) that `abort_if_multisig_payload_mismatch_enabled` is permanently enabled on mainnet before treating this as purely historical.

### Proof of Concept
1. Owner A creates a k-of-n multisig account `M` holding APT/fungible-asset/object custody.
2. Owner A calls `multisig_account::create_transaction(A, M, payload_benign)` where `payload_benign` encodes `aptos_account::transfer(M, alice, 10)`. This stores `payload = option::some(payload_benign)`, `payload_hash = option::none`. [1](#0-0) 
3. Owners B, C vote `approve_transaction` on this sequence number, believing they are approving `payload_benign`.
4. Instead of executing `payload_benign`, the executing owner submits a `MultisigTransaction` VM transaction whose `TransactionExecutableRef::EntryFunction` actually encodes `aptos_account::transfer(M, attacker, ALL_BALANCE)` (`payload_evil`).
5. In `run_multisig_prologue`/`validate_multisig_transaction`, since `transaction.payload_hash` is `none`, the hash-check branch is skipped; since `abort_if_multisig_payload_mismatch_enabled()` is (hypothetically) disabled, the payload-match branch is also skipped. [2](#0-1) 
6. `num_approvals >= num_signatures_required` still passes (votes were cast for the sequence number, not for specific payload bytes), so validation succeeds.
7. `execute_multisig_transaction` in the VM then executes `payload_evil` (the attacker-controlled entry function) using `M`'s signer, draining the multisig account's APT to `attacker`. [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1163-1183)
```text
    /// Create a multisig transaction, which will have one approval initially (from the creator).
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

**File:** aptos-move/aptos-vm/src/aptos_vm.rs (L1267-1349)
```rust
    // Execute a multisig transaction:
    // 1. Obtain the payload of the transaction to execute. This could have been stored on chain
    // when the multisig transaction was created.
    // 2. Execute the target payload. If this fails, discard the session and keep the gas meter and
    // failure object. In case of success, keep the session and also do any necessary module publish
    // cleanup.
    // 3. Call post transaction cleanup function in multisig account module with the result from (2)
    fn execute_multisig_transaction<'r>(
        &self,
        resolver: &'r impl AptosMoveResolver,
        code_storage: &impl AptosCodeStorage,
        mut session: UserSession<'r>,
        serialized_signers: &SerializedSigners,
        prologue_session_change_set: &SystemSessionChangeSet,
        gas_meter: &mut impl AptosGasMeter,
        traversal_context: &mut TraversalContext,
        txn_data: &TransactionMetadata,
        executable: TransactionExecutableRef,
        multisig_address: AccountAddress,
        log_context: &AdapterLogSchema,
        change_set_configs: &ChangeSetConfigs,
        trace_recorder: &mut impl TraceRecorder,
    ) -> Result<(VMStatus, VMOutput), VMStatus> {
        fail_point!("move_adapter::execute_multisig_transaction", |_| {
            Err(VMStatus::error(
                StatusCode::UNKNOWN_INVARIANT_VIOLATION_ERROR,
                None,
            ))
        });

        Self::charge_intrinsic_and_surcharges(gas_meter, txn_data)?;

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
        // Failures here will be propagated back.
        let payload_bytes: Vec<Vec<u8>> = session
```
