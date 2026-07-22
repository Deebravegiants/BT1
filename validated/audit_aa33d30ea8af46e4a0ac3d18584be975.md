### Title
`ProposalInit.builder` accepted without validation, injecting arbitrary `sequencer_address` into block execution and block hash — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` validates every security-sensitive field of a received `ProposalInit` (height, timestamp, starknet_version, l1_da_mode, l2_gas_price_fri, all four L1 gas prices, fee_proposal_fri, version_constant_commitment) but never checks `init.builder`. That field is passed verbatim to `convert_to_sn_api_block_info`, which maps it to `sequencer_address` in the `BlockInfo` handed to the batcher. A malicious proposer can therefore inject any `ContractAddress` as the block's sequencer address, causing every transaction in that block to execute with a wrong `sequencer_address`, producing wrong `get_execution_info` / `get_sequencer_address` syscall results, a wrong block hash, and wrong committed state.

---

### Finding Description

**Root cause — missing field in `ProposalInitValidation`**

`ProposalInitValidation` (the struct that carries the validator's locally-trusted reference values) contains `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `block_timestamp_window_seconds`, `previous_proposal_init`, and `fee_actual`. It does not contain a `builder_address` field. [1](#0-0) 

Consequently, `is_proposal_init_valid` has no reference value to compare `init.builder` against, and the field is silently accepted for any value. [2](#0-1) 

**Propagation — `builder` becomes `sequencer_address`**

After `is_proposal_init_valid` returns `Ok`, `initiate_validation` calls `convert_to_sn_api_block_info(init)`. That function maps `init.builder` directly to `sequencer_address` in the `starknet_api::block::BlockInfo` that is forwarded to the batcher: [3](#0-2) 

The same path is taken on the build side: [4](#0-3) 

On the build side `builder` is set from the locally-configured `self.config.static_config.builder_address`: [5](#0-4) 

On the validate side there is no equivalent check — the proposer-supplied value is used as-is.

**Execution impact — `get_execution_info` / `get_sequencer_address` syscalls**

The `BlockInfo` (with the attacker-controlled `sequencer_address`) is passed to the batcher's `validate_block` call and used for every transaction executed in that proposal. Contracts that call `get_execution_info` or `get_sequencer_address` receive the attacker-chosen address: [6](#0-5) [7](#0-6) [8](#0-7) 

**Commitment impact — wrong block hash**

`finalize_decision` also calls `convert_to_sn_api_block_info(init)` with the same unvalidated `init`, so the committed block carries the wrong `sequencer_address` in its header, producing a wrong block hash: [9](#0-8) 

---

### Impact Explanation

**Critical — Wrong state/receipt/event/revert result from blockifier/syscall/execution logic for accepted input.**

Any contract that branches on `get_execution_info().block_info.sequencer_address` (e.g., fee-token contracts, access-control contracts, or any contract that whitelists the sequencer) will observe the attacker-chosen address instead of the real one. The resulting execution outputs (storage writes, events, return values, reverts) are wrong. Because both the proposer and all validators use the same `init.builder` value when computing the `ProposalCommitment`, consensus reaches agreement on the corrupted block, and the wrong state is permanently committed.

---

### Likelihood Explanation

**Low.** Exploiting this requires a consensus validator to be selected as the round's proposer and to deliberately set `builder` to a value other than the network-agreed `builder_address`. In Starknet's current permissioned validator set this is a constrained threat model. However, the invariant is structurally broken: the validator node has a locally-configured `builder_address` that it never enforces on received proposals, so any future expansion of the validator set or any compromise of a single validator key is sufficient to trigger the bug.

---

### Recommendation

1. Add `builder_address: ContractAddress` to `ProposalInitValidation`.
2. Populate it from `self.config.static_config.builder_address` at the call site in `sequencer_consensus_context.rs` (alongside the existing `l1_da_mode`, `l2_gas_price_fri`, etc.).
3. In `is_proposal_init_valid`, add a check analogous to the existing `l1_da_mode` / `height` check:

```rust
if init_proposed.builder != proposal_init_validation.builder_address {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder_address, init_proposed.builder
        ),
    ));
}
``` [10](#0-9) 

---

### Proof of Concept

1. A validator node is selected as proposer for height H.
2. In `initiate_build`, instead of using `args.builder_address` (the locally-configured value), the attacker sets `builder: ContractAddress::from(0xdeadbeef_u64)` in the `ProposalInit` before streaming it to peers.
3. Every validating peer calls `is_proposal_init_valid` — the function checks `height`, `l1_da_mode`, `l2_gas_price_fri`, gas prices, `starknet_version`, `version_constant_commitment`, `fee_proposal_fri`, and `timestamp`. None of these checks involve `builder`. The function returns `Ok(())`.
4. `initiate_validation` calls `convert_to_sn_api_block_info(init)`, producing a `BlockInfo` with `sequencer_address = 0xdeadbeef`.
5. The batcher executes all transactions in the proposal with `sequencer_address = 0xdeadbeef`. Any contract calling `get_execution_info` sees `0xdeadbeef` as the sequencer.
6. The batcher returns a `ProposalCommitment` computed over the corrupted block. The validator's locally-computed commitment matches (it used the same `init.builder`), so `ProposalFinMismatch` is not triggered.
7. Consensus reaches decision on the corrupted block. `finalize_decision` commits it with `sequencer_address = 0xdeadbeef` in the block header and block hash. [11](#0-10) [12](#0-11)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L74-85)
```rust
#[derive(Clone, Debug)]
pub(crate) struct ProposalInitValidation {
    pub height: BlockNumber,
    pub block_timestamp_window_seconds: u64,
    pub previous_proposal_init: Option<PreviousProposalInitInfo>,
    pub l1_da_mode: L1DataAvailabilityMode,
    pub l2_gas_price_fri: GasPrice,
    pub starknet_version: StarknetVersion,
    /// fee_actual from the sliding window. `None` until the window has accumulated
    /// `fee_proposal_window_size` entries (startup / near-genesis).
    pub fee_actual: Option<GasPrice>,
}
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L141-249)
```rust
pub(crate) async fn validate_proposal(
    mut args: ProposalValidateArguments,
) -> ValidateProposalResult<ProposalCommitment> {
    let mut content = Vec::new();
    let mut verify_and_store_proof_tasks: Vec<VerifyAndStoreProofTask> = Vec::new();
    let now = args.deps.clock.now();

    let Some(deadline) = now.checked_add_signed(chrono::TimeDelta::from_std(args.timeout).unwrap())
    else {
        return Err(ValidateProposalError::CannotCalculateDeadline { timeout: args.timeout, now });
    };

    is_proposal_init_valid(
        &args.proposal_init_validation,
        &args.init,
        args.deps.clock.as_ref(),
        args.deps.l1_gas_price_provider,
        &args.gas_price_params,
    )
    .await?;

    initiate_validation(
        args.deps.batcher.clone(),
        args.deps.state_sync_client,
        &args.init,
        args.proposal_id,
        args.timeout + args.batcher_timeout_margin,
        args.deps.clock.as_ref(),
        args.compare_retrospective_block_hash,
    )
    .await?;

    let deadline_params = ProposalDeadlineParams {
        clock: args.deps.clock.clone(),
        deadline,
        cancel_token: args.cancel_token.clone(),
    };

    // Validating the rest of the proposal parts.
    let (built_block, received_fin, finished_info) = loop {
        tokio::select! {
            _ = args.cancel_token.cancelled() => {
                // Ignoring batcher errors, to better reflect the proposal interruption.
                batcher_abort_proposal(args.deps.batcher.as_ref(), args.proposal_id).await.ok();
                return Err(ValidateProposalError::ProposalInterrupted(
                    "validating proposal parts".to_string(),
                ));
            }
            _ = args.deps.clock.sleep_until(deadline) => {
                // Ignoring batcher errors, to better reflect the proposal deadline timeout.
                batcher_abort_proposal(args.deps.batcher.as_ref(), args.proposal_id).await.ok();
                return Err(ValidateProposalError::ValidationTimeout(
                    "validating proposal parts".to_string(),
                ));
            }
            proposal_part = args.content_receiver.next() => {
                match handle_proposal_part(
                    args.proposal_id,
                    args.deps.batcher.as_ref(),
                    proposal_part.clone(),
                    &mut content,
                    &mut verify_and_store_proof_tasks,
                    args.deps.transaction_converter.clone(),
                    &deadline_params,
                    args.init.fee_proposal_fri,
                ).await {
                    HandledProposalPart::Finished(built_block, received_fin, finished_info) => {
                        break (built_block, received_fin, finished_info);
                    }
                    HandledProposalPart::Continue => {continue;}
                    HandledProposalPart::Invalid(err) => {
                        // No need to abort since the Batcher is the source of this info.
                        return Err(ValidateProposalError::InvalidProposal(err));
                    }
                    HandledProposalPart::Failed(fail_reason) => {
                        batcher_abort_proposal(args.deps.batcher.as_ref(), args.proposal_id).await?;
                        return Err(ValidateProposalError::ProposalPartFailed(fail_reason,proposal_part));
                    }
                    HandledProposalPart::Timeout(msg) => {
                        // Ignoring batcher errors, to better reflect the validation timeout.
                        batcher_abort_proposal(args.deps.batcher.as_ref(), args.proposal_id).await.ok();
                        return Err(ValidateProposalError::ValidationTimeout(msg));
                    }
                    HandledProposalPart::Interrupted(msg) => {
                        // Ignoring batcher errors, to better reflect the proposal interruption.
                        batcher_abort_proposal(args.deps.batcher.as_ref(), args.proposal_id).await.ok();
                        return Err(ValidateProposalError::ProposalInterrupted(msg));
                    }
                }
            }
        }
    };

    let n_executed_txs = content.iter().map(|batch| batch.len()).sum::<usize>();
    CONSENSUS_NUM_BATCHES_IN_PROPOSAL.set_lossy(content.len());
    CONSENSUS_NUM_TXS_IN_PROPOSAL.set_lossy(n_executed_txs);

    // Update valid_proposals before sending fin to avoid a race condition
    // with `repropose` being called before `valid_proposals` is updated.
    let mut valid_proposals = args.valid_proposals.lock().unwrap();
    valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info);

    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }

    Ok(built_block)
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L253-321)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-476)
```rust
    let input = ValidateBlockInput {
        proposal_id,
        deadline: clock.now() + chrono_timeout,
        retrospective_block_hash: retrospective_block_hash(
            batcher.clone(),
            state_sync_client,
            init,
            compare_retrospective_block_hash,
        )
        .await
        .map_err(ValidateProposalError::from)?,
        block_info: convert_to_sn_api_block_info(init)?,
    };
    debug!("Initiating validate proposal: input={input:?}");
    batcher.validate_block(input.clone()).await.map_err(|err| {
        ValidateProposalError::Batcher(
            format!("Failed to initiate validate proposal {input:?}."),
            err,
        )
    })?;
    Ok(())
}
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L301-348)
```rust
pub(crate) fn convert_to_sn_api_block_info(
    init: &ProposalInit,
) -> Result<starknet_api::block::BlockInfo, StarknetApiError> {
    if init.l1_gas_price_fri.0 == 0
        || init.l1_gas_price_wei.0 == 0
        || init.l1_data_gas_price_fri.0 == 0
        || init.l1_data_gas_price_wei.0 == 0
        || init.l2_gas_price_fri.0 == 0
    {
        warn!("Zero gas price detected in block info: {:?}", init);
    }

    let l1_gas_price_fri = NonzeroGasPrice::new(init.l1_gas_price_fri)?;
    let l1_data_gas_price_fri = NonzeroGasPrice::new(init.l1_data_gas_price_fri)?;
    let l1_gas_price_wei = NonzeroGasPrice::new(init.l1_gas_price_wei)?;
    let l1_data_gas_price_wei = NonzeroGasPrice::new(init.l1_data_gas_price_wei)?;
    let l2_gas_price_fri = NonzeroGasPrice::new(init.l2_gas_price_fri)?;
    let proposal_init_info = PreviousProposalInitInfo::from(init);
    let eth_to_fri_rate = calculate_eth_to_fri_rate(&proposal_init_info)?;

    let l2_gas_price_wei = NonzeroGasPrice::new(init.l2_gas_price_fri.fri_to_wei(eth_to_fri_rate)?)
        .inspect_err(|_| {
            warn!(
                "L2 gas price in wei is zero! Conversion rate: {eth_to_fri_rate}, L2 gas price in \
                 FRI: {}",
                init.l2_gas_price_fri
            )
        })?;
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
            strk_gas_prices: GasPriceVector {
                l1_gas_price: l1_gas_price_fri,
                l1_data_gas_price: l1_data_gas_price_fri,
                l2_gas_price: l2_gas_price_fri,
            },
            eth_gas_prices: GasPriceVector {
                l1_gas_price: l1_gas_price_wei,
                l1_data_gas_price: l1_data_gas_price_wei,
                l2_gas_price: l2_gas_price_wei,
            },
        },
        use_kzg_da: init.l1_da_mode.is_use_kzg_da(),
        starknet_version: init.starknet_version,
    })
}
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L169-205)
```rust
    let init = ProposalInit {
        height: args.build_param.height,
        round: args.build_param.round,
        valid_round: args.build_param.valid_round,
        proposer: args.build_param.proposer,
        builder: args.builder_address,
        timestamp,
        l1_da_mode: args.l1_da_mode,
        l2_gas_price_fri: args.l2_gas_price,
        l1_gas_price_wei: l1_prices_wei.l1_gas_price,
        l1_data_gas_price_wei: l1_prices_wei.l1_data_gas_price,
        l1_gas_price_fri: l1_prices_fri.l1_gas_price,
        l1_data_gas_price_fri: l1_prices_fri.l1_data_gas_price,
        starknet_version: starknet_api::block::StarknetVersion::LATEST,
        // TODO(Asmaa): Put the real value once we have it.
        // Sentinel until then; see `expected_version_constant_commitment` for why this is the
        // single source of truth shared with the validator.
        version_constant_commitment: expected_version_constant_commitment(),
        fee_proposal_fri: Some(args.fee_proposal),
    };

    let retrospective_block_hash = wait_for_retrospective_block_hash(
        args.deps.batcher.clone(),
        args.deps.state_sync_client.clone(),
        &init,
        args.deps.clock.as_ref(),
        args.retrospective_block_hash_deadline,
        args.retrospective_block_hash_retry_interval_millis,
        args.compare_retrospective_block_hash,
    )
    .await?;

    let build_proposal_input = ProposeBlockInput {
        proposal_id: args.proposal_id,
        deadline: args.batcher_deadline,
        retrospective_block_hash,
        block_info: convert_to_sn_api_block_info(&init)?,
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L551-556)
```rust
        // The conversion should never fail, if we already managed to get a decision.
        let cende_block_info = convert_to_sn_api_block_info(init).expect(
            "Failed to convert block info to SN API block info (required for state sync and \
             preparing the cende blob). IMPORTANT: The block was committed; a revert might be \
             required for the node to be able to proceed.",
        );
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L806-808)
```rust
            // TODO(Asmaa): Get it from committee once we have it.
            builder_address: self.config.static_config.builder_address,
            cancel_token,
```

**File:** crates/blockifier/src/execution/deprecated_syscalls/hint_processor.rs (L725-734)
```rust
    fn get_sequencer_address(
        _request: GetSequencerAddressRequest,
        _vm: &mut VirtualMachine,
        syscall_handler: &mut Self,
    ) -> DeprecatedSyscallResult<GetSequencerAddressResponse> {
        syscall_handler.verify_not_in_validate_mode("get_sequencer_address")?;
        Ok(GetSequencerAddressResponse {
            address: syscall_handler.get_block_info().sequencer_address,
        })
    }
```

**File:** crates/blockifier/src/execution/native/syscall_handler.rs (L220-231)
```rust
    fn get_block_info(&self) -> BlockInfo {
        let block_info = match self.base.context.execution_mode {
            ExecutionMode::Execute => self.base.context.tx_context.block_context.block_info(),
            ExecutionMode::Validate => {
                &self.base.context.tx_context.block_context.block_info_for_validate()
            }
        };
        BlockInfo {
            block_number: block_info.block_number.0,
            block_timestamp: block_info.block_timestamp.0,
            sequencer_address: Felt::from(block_info.sequencer_address),
        }
```
