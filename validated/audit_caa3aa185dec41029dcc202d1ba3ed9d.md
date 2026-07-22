### Title
Unvalidated `builder` Field in `ProposalInit` Allows Malicious Proposer to Redirect All Block Transaction Fees to Arbitrary Address — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

The `builder` field in `ProposalInit` is accepted from the network and used verbatim as `sequencer_address` in the block execution context, but `is_proposal_init_valid` never checks it against any locally-trusted reference. Because all transaction fees are transferred to `sequencer_address`, a malicious proposer can set `builder` to any address and redirect the entire block's fee revenue to themselves. Validators accept the proposal, compute the same `ProposalCommitment` (which embeds the attacker-supplied address), and the block is committed with the wrong sequencer.

---

### Finding Description

**Step 1 – Proposer-controlled field, no validation.**

`is_proposal_init_valid` validates `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, `timestamp`, all four L1 gas prices, and `fee_proposal_fri`. The `builder` field is never mentioned. [1](#0-0) 

**Step 2 – `builder` becomes `sequencer_address` in block context.**

`convert_to_sn_api_block_info` maps `init.builder` directly to `BlockInfo.sequencer_address`: [2](#0-1) 

**Step 3 – `sequencer_address` is the fee-collection address.**

The blockifier transfers every transaction's fee to `block_context.block_info.sequencer_address`. In concurrency mode the balance is patched post-execution; in sequential mode it is written directly. Either way, the destination is the address that came from `init.builder`. [3](#0-2) 

**Step 4 – `sequencer_address` is also committed into the block hash.**

`PartialBlockHashComponents::new` stores `block_info.sequencer_address` as the `sequencer` field, which is then hashed into the partial block hash and ultimately into `ProposalCommitment`. [4](#0-3) [5](#0-4) 

**Step 5 – Both proposer and validator use the same `builder` value, so the commitment check passes.**

The validator calls `convert_to_sn_api_block_info(init)` with the received `init`, runs the block through the batcher, and compares the resulting `ProposalCommitment` against `ProposalFin.proposal_commitment`. Because both sides derive the commitment from the same `init.builder`, the check at line 244 passes even when `builder` is an attacker-controlled address. [6](#0-5) 

**Step 6 – The proposer's own code acknowledges the field is not yet committee-sourced.**

The TODO comment in `build_proposal.rs` explicitly notes that `builder_address` should eventually come from a committee but currently comes from local config — meaning any proposer can freely set it to any value: [7](#0-6) 

---

### Impact Explanation

Every transaction fee paid in the block is transferred to `sequencer_address`, which equals `init.builder`. A malicious proposer sets `builder` to an attacker-controlled wallet. Validators accept the proposal without checking the field. The block is committed with the attacker's address as sequencer, and the entire block's fee revenue is permanently redirected. This matches the allowed Critical impact: *"Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact."*

---

### Likelihood Explanation

Any node that wins a consensus proposer slot can execute this attack with a single-field change to `ProposalInit`. No special privileges beyond being a consensus participant are required. The attack is silent — no error is raised, no metric fires, and the `ProposalCommitment` comparison succeeds.

---

### Recommendation

In `is_proposal_init_valid`, validate `init_proposed.builder` against a locally-trusted expected sequencer address (e.g., derived from the committee or from a node-local config value that mirrors what honest proposers emit). Until the committee source is available, at minimum enforce that `init_proposed.builder` equals the validator's own configured `builder_address`, or reject proposals whose `builder` differs from the value the local node would have set.

```rust
// Example guard to add inside is_proposal_init_valid:
if init_proposed.builder != proposal_init_validation.expected_builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.expected_builder, init_proposed.builder
        ),
    ));
}
```

---

### Proof of Concept

1. Attacker operates a consensus validator node and wins a proposer slot for block N.
2. Attacker modifies `initiate_build` (or crafts a raw `ProposalInit` message) to set `builder = attacker_wallet_address` instead of the node's configured `builder_address`.
3. The `ProposalInit` is broadcast to all validators.
4. Each validator calls `is_proposal_init_valid` — the `builder` field is never checked; validation passes.
5. Each validator calls `convert_to_sn_api_block_info(init)`, producing `BlockInfo { sequencer_address: attacker_wallet_address, … }`.
6. The batcher executes all transactions with `sequencer_address = attacker_wallet_address`; every fee transfer credits `attacker_wallet_address`.
7. `BlockExecutionArtifacts::new` computes `PartialBlockHashComponents` with `sequencer = attacker_wallet_address`; the resulting `ProposalCommitment` matches the proposer's `ProposalFin.proposal_commitment`.
8. `validate_proposal` returns `Ok(built_block)` — no mismatch detected.
9. Consensus decides on the block; `decision_reached` commits it. All fees from block N are in `attacker_wallet_address`. [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L243-247)
```rust
    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
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

**File:** crates/blockifier/src/concurrency/fee_utils.rs (L105-157)
```rust
pub fn add_fee_to_sequencer_balance(
    fee_token_address: ContractAddress,
    state: &mut impl UpdatableState,
    actual_fee: Fee,
    block_context: &BlockContext,
    sequencer_balance: (Felt, Felt),
    sender_address: ContractAddress,
    state_diff: &mut StateMaps,
) {
    assert_ne!(
        sender_address, block_context.block_info.sequencer_address,
        "The sender cannot be the sequencer."
    );
    let (low, high) = sequencer_balance;
    let sequencer_balance_low_as_u128 =
        low.to_u128().expect("sequencer balance low should be u128");
    let sequencer_balance_high_as_u128 =
        high.to_u128().expect("sequencer balance high should be u128");
    let (new_value_low, overflow_low) = sequencer_balance_low_as_u128.overflowing_add(actual_fee.0);
    let (new_value_high, overflow_high) =
        sequencer_balance_high_as_u128.overflowing_add(overflow_low.into());
    assert!(
        !overflow_high,
        "The sequencer balance overflowed when adding the fee. This should not happen."
    );
    let (sequencer_balance_key_low, sequencer_balance_key_high) =
        get_sequencer_balance_keys(block_context);
    let writes = StateMaps {
        storage: HashMap::from([
            ((fee_token_address, sequencer_balance_key_low), Felt::from(new_value_low)),
            ((fee_token_address, sequencer_balance_key_high), Felt::from(new_value_high)),
        ]),
        ..StateMaps::default()
    };

    // Modify state_diff to accurately reflect the post tx-execution state, after fee transfer to
    // the sequencer. We assume that a non-sequencer sender cannot reduce the sequencer's
    // balance—only increases are possible.

    if sequencer_balance_high_as_u128 != new_value_high {
        // Update the high balance only if it has changed.
        state_diff
            .storage
            .insert((fee_token_address, sequencer_balance_key_high), Felt::from(new_value_high));
    }

    if sequencer_balance_low_as_u128 != new_value_low {
        // Update the low balance only if it has changed.
        state_diff
            .storage
            .insert((fee_token_address, sequencer_balance_key_low), Felt::from(new_value_low));
    }
    state.apply_writes(&writes, &ContractClassMapping::default());
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L223-235)
```rust
impl PartialBlockHashComponents {
    pub fn new(block_info: &BlockInfo, header_commitments: BlockHeaderCommitments) -> Self {
        Self {
            header_commitments,
            block_number: block_info.block_number,
            l1_gas_price: block_info.gas_prices.l1_gas_price_per_token(),
            l1_data_gas_price: block_info.gas_prices.l1_data_gas_price_per_token(),
            l2_gas_price: block_info.gas_prices.l2_gas_price_per_token(),
            sequencer: SequencerContractAddress(block_info.sequencer_address),
            timestamp: block_info.block_timestamp,
            starknet_version: block_info.starknet_version,
        }
    }
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-281)
```rust
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
            .chain(&block_commitments.concatenated_counts)
            .chain(&block_commitments.state_diff_commitment.0.0)
            .chain(&block_commitments.transaction_commitment.0)
            .chain(&block_commitments.event_commitment.0)
            .chain(&block_commitments.receipt_commitment.0)
            .chain_iter(
                gas_prices_to_hash(
                    &partial_block_hash_components.l1_gas_price,
                    &partial_block_hash_components.l1_data_gas_price,
                    &partial_block_hash_components.l2_gas_price,
                    &block_hash_version,
                )
                .iter(),
            )
            .chain(
                &Felt::try_from(&partial_block_hash_components.starknet_version)
                    .expect("Expect ASCII version"),
            )
            .chain(&Felt::ZERO)
            .chain(&previous_block_hash.0)
            .get_poseidon_hash(),
    ))
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L173-175)
```rust
        proposer: args.build_param.proposer,
        builder: args.builder_address,
        timestamp,
```

**File:** crates/apollo_batcher/src/block_builder.rs (L166-194)
```rust
        let l1_da_mode = L1DataAvailabilityMode::from_use_kzg_da(block_info.use_kzg_da);
        let transactions_data =
            prepare_txs_hashing_data(&execution_data.execution_infos_and_signatures);
        // TODO(Ayelet): Remove the clones.
        let (header_commitments, measurements) = calculate_block_commitments(
            &transactions_data,
            ThinStateDiff::from(commitment_state_diff.clone()),
            l1_da_mode,
            &block_info.starknet_version,
        )
        .await;
        record_and_log_block_commitment_measurements(block_info.block_number, measurements);
        let partial_block_hash_components =
            PartialBlockHashComponents::new(&block_info, header_commitments);
        let l2_gas_used = execution_data.l2_gas_used();
        Self {
            execution_data,
            commitment_state_diff,
            compressed_state_diff,
            #[cfg(feature = "os_input")]
            initial_reads,
            bouncer_weights,
            l2_gas_used,
            casm_hash_computation_data_sierra_gas,
            casm_hash_computation_data_proving_gas,
            compiled_class_hashes_for_migration,
            final_n_executed_txs,
            partial_block_hash_components,
        }
```
