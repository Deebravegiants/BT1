### Title
Gateway `authorized_declarer_accounts` Whitelist and `block_declare` Flag Bypassed via Consensus Proposal Path - (File: `crates/apollo_gateway/src/gateway.rs`)

### Summary
The gateway enforces `authorized_declarer_accounts` (a per-address whitelist) and `block_declare` (a global kill-switch) as admission controls for declare transactions. Neither control is applied on the consensus proposal validation path. A malicious proposer can include a declare transaction from any address in a proposal; every validator will execute it through the batcher without checking either restriction, committing an unauthorized contract declaration to the chain.

### Finding Description

**Guarded path (gateway).**
`check_declare_permissions` is called inside `add_tx_inner` before any conversion or execution:

```rust
// crates/apollo_gateway/src/gateway.rs  lines 228-233
if let RpcTransaction::Declare(ref declare_tx) = tx {
    if let Err(e) = self.check_declare_permissions(declare_tx) {
        ...
        return Err(e);
    }
}
```

`check_declare_permissions` (lines 407-433) enforces:
- `block_declare` — rejects all declares when `true`.
- `authorized_declarer_accounts` — rejects any sender not in the whitelist. [1](#0-0) 

The config description is explicit: *"Authorized declarer accounts. If set, **only these accounts can declare new contracts**."* [2](#0-1) 

**Unguarded path (consensus validator).**
When a validator receives a proposal, `handle_proposal_part` converts each transaction via `transaction_converter.convert_consensus_tx_to_internal_consensus_tx` and forwards it directly to the batcher:

```rust
// crates/apollo_consensus_orchestrator/src/validate_proposal.rs  lines 602-635
let conversion_results =
    futures::future::join_all(txs.into_iter().map(|tx| {
        transaction_converter.convert_consensus_tx_to_internal_consensus_tx(tx)
    }))
    ...
let input = SendTxsForProposalInput { proposal_id, txs };
let response = match batcher.send_txs_for_proposal(input).await { ... };
``` [3](#0-2) 

`convert_consensus_tx_to_internal_consensus_tx` calls the shared `convert_rpc_tx_to_internal` helper, which compiles the Sierra class and computes the class hash but performs **no** `authorized_declarer_accounts` or `block_declare` check: [4](#0-3) [5](#0-4) 

`is_proposal_init_valid` validates height, timestamp, starknet version, l1_da_mode, l2_gas_price, and fee_proposal, but contains no per-transaction sender-address authorization: [6](#0-5) 

The batcher's `validate_block` path also has no such check: [7](#0-6) 

### Impact Explanation

When `authorized_declarer_accounts` is configured (non-`None`) or `block_declare = true`, the operator's intent is that **no** unauthorized declare transaction reaches the chain. A malicious proposer bypasses both controls entirely: the unauthorized declare is executed by every honest validator's batcher and committed to the canonical state. The resulting class hash is permanently registered in the state trie, and any contract can subsequently be deployed from it — an outcome the operator explicitly tried to prevent.

This matches the **High** impact category: *"Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing"* — the gateway admission control is rendered ineffective by the consensus ingestion path.

### Likelihood Explanation

The attacker must be a current-round proposer in the consensus network. When `authorized_declarer_accounts` is `None` (the default), there is no restriction to bypass. The vulnerability is active only when the operator has explicitly set the whitelist or enabled `block_declare`, which is a deliberate operational choice (e.g., during a controlled rollout). Once those flags are set, any proposer can trivially include a forbidden declare in a proposal with no additional effort. [8](#0-7) [9](#0-8) 

### Recommendation

1. **Enforce at the consensus boundary.** In `handle_proposal_part` (or inside `convert_consensus_tx_to_internal_consensus_tx`), check `block_declare` and `authorized_declarer_accounts` for every `RpcTransaction::Declare` received in a proposal batch. Return `HandledProposalPart::Invalid` on violation so the proposal is rejected without aborting the batcher.

2. **Alternatively, move the restriction to the batcher.** Pass the declare-permission config to `ValidateTransactionProvider` / `BlockBuilder` so the blockifier layer enforces it uniformly regardless of ingestion path.

3. **Document the scope.** If the restriction is intentionally gateway-only (admission-control only, not a chain-level invariant), document this explicitly so operators are not misled by the config description.

### Proof of Concept

```
Precondition: gateway_config.static_config.authorized_declarer_accounts = ["0x1"]
              (only address 0x1 is allowed to declare)

1. Attacker (a validator / proposer) constructs a valid RpcDeclareTransactionV3
   with sender_address = 0x2 (not in the whitelist).

2. Attacker includes this transaction in a ProposalPart::Transactions batch
   and streams it to all validators as part of a normal consensus proposal.

3. Each honest validator calls handle_proposal_part →
   convert_consensus_tx_to_internal_consensus_tx(declare_tx).
   → convert_rpc_tx_to_internal compiles the Sierra class and returns
     InternalRpcTransaction without checking authorized_declarer_accounts.

4. The internal tx is forwarded to the batcher via send_txs_for_proposal.
   The batcher executes it through blockifier with no permission check.

5. finish_proposal returns a ProposalCommitment that includes the declare.
   Validators sign the commitment; consensus reaches decision.

6. The unauthorized class hash is now permanently registered in the
   Starknet state trie, reachable by any deploy_account or deploy syscall.
``` [10](#0-9) [3](#0-2) [11](#0-10)

### Citations

**File:** crates/apollo_gateway/src/gateway.rs (L228-233)
```rust
        if let RpcTransaction::Declare(ref declare_tx) = tx {
            if let Err(e) = self.check_declare_permissions(declare_tx) {
                metric_counters.record_add_tx_failure(&e);
                return Err(e);
            }
        }
```

**File:** crates/apollo_gateway/src/gateway.rs (L407-433)
```rust
    fn check_declare_permissions(
        &self,
        declare_tx: &RpcDeclareTransaction,
    ) -> Result<(), StarknetError> {
        // TODO(noamsp): Return same error as in Python gateway.
        if self.config.static_config.block_declare {
            return Err(StarknetError {
                code: StarknetErrorCode::UnknownErrorCode(
                    "StarknetErrorCode.BLOCKED_TRANSACTION_TYPE".to_string(),
                ),
                message: "Transaction type is temporarily blocked.".to_string(),
            });
        }
        let RpcDeclareTransaction::V3(declare_v3_tx) = declare_tx;
        if !self.config.is_authorized_declarer(&declare_v3_tx.sender_address) {
            return Err(StarknetError {
                code: StarknetErrorCode::KnownErrorCode(
                    KnownStarknetErrorCode::UnauthorizedDeclare,
                ),
                message: format!(
                    "Account address {} is not allowed to declare contracts.",
                    &declare_v3_tx.sender_address
                ),
            });
        }
        Ok(())
    }
```

**File:** crates/apollo_gateway_config/src/config.rs (L49-51)
```rust
    pub block_declare: bool,
    #[serde(default, deserialize_with = "deserialize_comma_separated_str")]
    pub authorized_declarer_accounts: Option<Vec<ContractAddress>>,
```

**File:** crates/apollo_gateway_config/src/config.rs (L99-106)
```rust
        dump.extend(ser_optional_param(
            &serialize_optional_comma_separated(&self.authorized_declarer_accounts),
            "".to_string(),
            "authorized_declarer_accounts",
            "Authorized declarer accounts. If set, only these accounts can declare new contracts. \
             Addresses are in hex format and separated by a comma with no space.",
            ParamPrivacyInput::Public,
        ));
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-321)
```rust
#[instrument(level = "warn", skip_all, fields(?proposal_init_validation, ?init_proposed))]
async fn is_proposal_init_valid(
    proposal_init_validation: &ProposalInitValidation,
    init_proposed: &ProposalInit,
    clock: &dyn Clock,
    l1_gas_price_provider: Arc<dyn L1GasPriceProviderClient>,
    gas_price_params: &GasPriceParams,
) -> ValidateProposalResult<()> {
    let now: u64 = clock.unix_now();
    let last_block_timestamp =
        proposal_init_validation.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
    if init_proposed.timestamp < last_block_timestamp {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "Timestamp is too old: last_block_timestamp={}, proposed={}",
                last_block_timestamp, init_proposed.timestamp
            ),
        ));
    }
    if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "Timestamp is in the future: now={}, block_timestamp_window_seconds={}, \
                 proposed={}",
                now,
                proposal_init_validation.block_timestamp_window_seconds,
                init_proposed.timestamp
            ),
        ));
    }
    if init_proposed.starknet_version != proposal_init_validation.starknet_version {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "starknet_version mismatch: expected={:?}, proposed={:?}",
                proposal_init_validation.starknet_version, init_proposed.starknet_version
            ),
        ));
    }
    // `version_constant_commitment` is proposer-supplied (network-derived). It is not yet a real
    // commitment (see `expected_version_constant_commitment`): the only valid value is the
    // sentinel, so reject anything else. Enforcing the same value the proposer emits keeps the two
    // sides in lockstep, so a real value cannot ship on one side without the other.
    let expected_commitment = expected_version_constant_commitment();
    if init_proposed.version_constant_commitment != expected_commitment {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "version_constant_commitment mismatch: expected={expected_commitment:?}, \
                 proposed={:?}",
                init_proposed.version_constant_commitment
            ),
        ));
    }
    if !(init_proposed.height == proposal_init_validation.height
        && init_proposed.l1_da_mode == proposal_init_validation.l1_da_mode
        && init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri)
    {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            "ProposalInit validation failed".to_string(),
        ));
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L598-647)
```rust
        Some(ProposalPart::Transactions(TransactionBatch { transactions: txs })) => {
            // TODO(guyn): check that the length of txs and the number of batches we receive is not
            // so big it would fill up the memory (in case of a malicious proposal)
            debug!("Received transaction batch with {} txs", txs.len());
            let conversion_results =
                futures::future::join_all(txs.into_iter().map(|tx| {
                    transaction_converter.convert_consensus_tx_to_internal_consensus_tx(tx)
                }))
                .await
                .into_iter()
                .collect::<Result<Vec<_>, _>>();
            let conversion_results = match conversion_results {
                Ok(results) => results,
                Err(e) => {
                    return HandledProposalPart::Failed(format!(
                        "Failed to convert transactions. Stopping the build of the current \
                         proposal. {e:?}"
                    ));
                }
            };

            // Separate internal transactions from verification and store proof tasks. Each task
            // verifies the proof and stores it in the proof manager. Tasks are collected
            // and awaited later in the fin case.
            let (txs, tasks): (
                Vec<InternalConsensusTransaction>,
                Vec<Option<VerifyAndStoreProofTask>>,
            ) = conversion_results.into_iter().unzip();
            verify_and_store_proof_tasks.extend(tasks.into_iter().flatten());

            debug!(
                "Converted transactions to internal representation. hashes={:?}",
                txs.iter().map(|tx| tx.tx_hash()).collect::<Vec<TransactionHash>>()
            );

            content.push(txs.clone());
            let input = SendTxsForProposalInput { proposal_id, txs };
            let response = match batcher.send_txs_for_proposal(input).await {
                Ok(response) => response,
                Err(e) => {
                    return HandledProposalPart::Failed(format!(
                        "Failed to send transactions to batcher: {e:?}"
                    ));
                }
            };
            match response {
                SendTxsForProposalStatus::Processing => HandledProposalPart::Continue,
                SendTxsForProposalStatus::InvalidProposal(err) => HandledProposalPart::Invalid(err),
            }
        }
```

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L184-202)
```rust
    async fn convert_consensus_tx_to_internal_consensus_tx(
        &self,
        tx: ConsensusTransaction,
    ) -> TransactionConverterResult<(InternalConsensusTransaction, Option<VerifyAndStoreProofTask>)>
    {
        match tx {
            ConsensusTransaction::RpcTransaction(tx) => {
                let (internal_tx, proof_data) = self.convert_rpc_tx_to_internal(tx).await?;
                let task = proof_data.map(|(proof_facts, proof)| {
                    self.spawn_verify_and_store_proof(proof_facts, proof)
                });
                Ok((InternalConsensusTransaction::RpcTransaction(internal_tx), task))
            }
            ConsensusTransaction::L1Handler(tx) => {
                let internal_tx = self.convert_consensus_l1_handler_to_internal_l1_handler(tx)?;
                Ok((InternalConsensusTransaction::L1Handler(internal_tx), None))
            }
        }
    }
```

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L334-392)
```rust
    async fn convert_rpc_tx_to_internal(
        &self,
        tx: RpcTransaction,
    ) -> TransactionConverterResult<(InternalRpcTransaction, Option<(ProofFacts, Proof)>)> {
        let (tx_without_hash, proof_data) = match tx {
            RpcTransaction::Invoke(RpcInvokeTransaction::V3(tx)) => {
                let proof_data = if tx.proof_facts.is_empty() {
                    None
                } else {
                    Some((tx.proof_facts.clone(), tx.proof.clone()))
                };
                (InternalRpcTransactionWithoutTxHash::Invoke(tx.into()), proof_data)
            }
            RpcTransaction::Declare(RpcDeclareTransaction::V3(tx)) => {
                let ClassHashes { class_hash, executable_class_hash_v2 } =
                // TODO(Dori): Make this async and spawn a task to compile and add it to the class manager.
                    self.class_manager_client.add_class(tx.contract_class).await?;
                // TODO(Aviv): Ensure that we do not want to
                // allow declare with compiled class hash v1.
                if tx.compiled_class_hash != executable_class_hash_v2 {
                    return Err(TransactionConverterError::ValidateCompiledClassHashError(
                        ValidateCompiledClassHashError::CompiledClassHashMismatch {
                            computed_class_hash: executable_class_hash_v2,
                            supplied_class_hash: tx.compiled_class_hash,
                        },
                    ));
                }
                (
                    InternalRpcTransactionWithoutTxHash::Declare(InternalRpcDeclareTransactionV3 {
                        sender_address: tx.sender_address,
                        compiled_class_hash: tx.compiled_class_hash,
                        signature: tx.signature,
                        nonce: tx.nonce,
                        class_hash,
                        resource_bounds: tx.resource_bounds,
                        tip: tx.tip,
                        paymaster_data: tx.paymaster_data,
                        account_deployment_data: tx.account_deployment_data,
                        nonce_data_availability_mode: tx.nonce_data_availability_mode,
                        fee_data_availability_mode: tx.fee_data_availability_mode,
                    }),
                    None,
                )
            }
            RpcTransaction::DeployAccount(RpcDeployAccountTransaction::V3(tx)) => {
                let contract_address = tx.calculate_contract_address()?;
                (
                    InternalRpcTransactionWithoutTxHash::DeployAccount(
                        InternalRpcDeployAccountTransaction {
                            tx: RpcDeployAccountTransaction::V3(tx),
                            contract_address,
                        },
                    ),
                    None,
                )
            }
        };
        let tx_hash = tx_without_hash.calculate_transaction_hash(&self.chain_id)?;
        Ok((InternalRpcTransaction { tx: tx_without_hash, tx_hash }, proof_data))
```

**File:** crates/apollo_batcher/src/batcher.rs (L478-566)
```rust
    #[instrument(skip(self), err)]
    pub async fn validate_block(
        &mut self,
        validate_block_input: ValidateBlockInput,
    ) -> BatcherResult<()> {
        let proposal_metrics_handle = ProposalMetricsHandle::new();
        let active_height = self.active_height.ok_or(BatcherError::NoActiveHeight)?;
        verify_block_input(
            active_height,
            validate_block_input.block_info.block_number,
            validate_block_input.retrospective_block_hash,
        )?;

        // Ignore errors. If start_block fails, then subsequent calls to l1 provider will fail on
        // out of session and l1 provider will restart and bootstrap again.
        let _ = self
            .l1_events_provider_client
            .start_block(SessionState::Validate, validate_block_input.block_info.block_number)
            .await
            .inspect_err(|err| {
                error!(
                    "L1 provider is not ready to start validating block {}: {}. ",
                    validate_block_input.block_info.block_number, err
                );
                BATCHER_L1_EVENTS_PROVIDER_ERRORS.increment(1);
            });

        // A channel to send the transactions to include in the block being validated.
        let (input_tx_sender, input_tx_receiver) =
            tokio::sync::mpsc::channel(self.config.static_config.input_stream_content_buffer_size);
        let (final_n_executed_txs_sender, final_n_executed_txs_receiver) =
            tokio::sync::oneshot::channel();

        let tx_provider = ValidateTransactionProvider::new(
            input_tx_receiver,
            final_n_executed_txs_receiver,
            self.l1_events_provider_client.clone(),
            validate_block_input.block_info.block_number,
        );
        let (block_builder, abort_signal_sender) = self
            .block_builder_factory
            .create_block_builder(
                BlockMetadata {
                    block_info: validate_block_input.block_info,
                    retrospective_block_hash: validate_block_input.retrospective_block_hash,
                },
                BlockBuilderExecutionParams {
                    deadline: deadline_as_instant(validate_block_input.deadline)?,
                    is_validator: true,
                    proposer_idle_detection_delay: self
                        .config
                        .dynamic_config
                        .proposer_idle_detection_delay_millis,
                    n_concurrent_txs: self.config.dynamic_config.n_concurrent_txs,
                    tx_polling_interval_millis: self
                        .config
                        .dynamic_config
                        .validate_tx_polling_interval_millis,
                },
                self.config.dynamic_config.native_classes_whitelist.clone(),
                Box::new(tx_provider),
                None,
                None,
                tokio::runtime::Handle::current(),
            )
            .map_err(|err| {
                error!("Failed to get block builder: {}", err);
                BatcherError::InternalError
            })?;

        self.spawn_proposal(
            validate_block_input.proposal_id,
            block_builder,
            abort_signal_sender,
            Some(final_n_executed_txs_sender),
            None,
            proposal_metrics_handle,
        )
        .await?;

        let validation_already_exists =
            self.validate_tx_streams.insert(validate_block_input.proposal_id, input_tx_sender);
        assert!(
            validation_already_exists.is_none(),
            "Proposal {} already exists. This should have been checked when spawning the proposal.",
            validate_block_input.proposal_id
        );

        Ok(())
```

**File:** crates/apollo_deployments/resources/app_configs/gateway_config.json (L2-4)
```json
  "gateway_config.static_config.authorized_declarer_accounts": "",
  "gateway_config.static_config.authorized_declarer_accounts.#is_none": true,
  "gateway_config.static_config.block_declare": false,
```
