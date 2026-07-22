### Title
Unvalidated `ProposalInit.builder` Field Allows Malicious Proposer to Inject Arbitrary Sequencer Address into Block Hash and Fee Accounting — (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` validates every security-sensitive field of `ProposalInit` except `builder` (the sequencer/builder address). A single malicious proposer can set `init.builder` to any arbitrary address. All honest validators accept the proposal without checking `builder`, execute the block with the attacker-controlled sequencer address, and commit a block whose hash and fee-recipient are both wrong.

---

### Finding Description

`ProposalInit` carries a `builder` field — the address of the entity that sequences the block and receives transaction fees. [1](#0-0) 

During proposal validation, `is_proposal_init_valid` checks `timestamp`, `starknet_version`, `version_constant_commitment`, `height`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices, and `fee_proposal_fri`. The `builder` field is never compared against any trusted reference: [2](#0-1) 

`ProposalInitValidation` — the struct that carries the validator's locally-trusted reference values — has no `builder` field at all: [3](#0-2) 

After `is_proposal_init_valid` returns `Ok`, `initiate_validation` calls `convert_to_sn_api_block_info(init)`, which maps `init.builder` directly to `sequencer_address` in `BlockInfo`: [4](#0-3) 

That `BlockInfo` is forwarded to the batcher as `ValidateBlockInput.block_info`. The batcher uses `sequencer_address` in two ways:

1. **Transaction execution** — the sequencer address is the fee recipient in the execution context.
2. **Block hash computation** — `PartialBlockHashComponents::new` stores `sequencer_address` as `sequencer`, which is chained into the Poseidon block hash: [5](#0-4) [6](#0-5) 

The `ProposalFinMismatch` guard at line 244 does **not** protect against this attack. It compares `batcher_block_commitment` (computed from the batcher's output, which already used the attacker-supplied `builder`) against `received_fin.proposal_commitment` (which the malicious proposer pre-computed using the same wrong `builder`). Both sides agree on the wrong value, so the check passes: [7](#0-6) 

The proposer constructs the commitment as `proposal_commitment_from(partial_block_hash_with_attacker_builder, fee_proposal_fri)`: [8](#0-7) 

---

### Impact Explanation

**Critical — Incorrect fee/balance with economic impact; wrong block hash committed to L1.**

- **Fee theft**: All transaction fees in the block are paid to `sequencer_address`. A malicious proposer sets `builder` to their own address, redirecting every fee from every transaction in that block to themselves.
- **Wrong block hash**: The sequencer address is a direct input to the Poseidon block hash chain. A wrong `builder` produces a wrong `partial_block_hash`, which propagates to the final `BlockHash` stored on-chain and anchored to L1.

---

### Likelihood Explanation

Any consensus participant that is selected as proposer for a round can trigger this. In BFT consensus, proposer selection rotates among all validators. No special privilege is required beyond being the current-round proposer. A single malicious proposer suffices — all honest validators accept the proposal because none of them check `builder`.

---

### Recommendation

Add `builder` (the expected sequencer address) to `ProposalInitValidation` and enforce an exact-match check in `is_proposal_init_valid`, analogous to the existing checks for `height`, `l1_da_mode`, and `l2_gas_price_fri`:

```rust
// In ProposalInitValidation:
pub builder: ContractAddress,

// In is_proposal_init_valid:
if init_proposed.builder != proposal_init_validation.builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!("builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder, init_proposed.builder),
    ));
}
```

The expected `builder` should be populated from the node's own configured builder address when constructing `ProposalInitValidation` in `validate_proposal` and `set_height_and_round`. [9](#0-8) 

---

### Proof of Concept

1. Malicious validator is selected as proposer for round R at height H.
2. Proposer constructs `ProposalInit` with `builder = ATTACKER_ADDRESS` (any address they control).
3. Proposer sends `ProposeBlockInput` to its own batcher with `block_info.sequencer_address = ATTACKER_ADDRESS`.
4. Batcher executes all transactions with `sequencer_address = ATTACKER_ADDRESS` → fees accumulate to attacker.
5. Batcher returns `partial_block_hash` computed with `sequencer = ATTACKER_ADDRESS`.
6. Proposer computes `fin.proposal_commitment = proposal_commitment_from(partial_block_hash, fee_proposal_fri)`.
7. Proposer streams `ProposalPart::Init(init)`, transactions, and `ProposalPart::Fin(fin)` to all validators.
8. Each honest validator calls `is_proposal_init_valid` — passes (no `builder` check).
9. Each validator calls `convert_to_sn_api_block_info(init)` → `sequencer_address = ATTACKER_ADDRESS`.
10. Each validator's batcher re-executes with `ATTACKER_ADDRESS`, produces the same `partial_block_hash`.
11. `batcher_block_commitment == received_fin.proposal_commitment` → `ProposalFinMismatch` check passes.
12. All validators vote for the proposal; consensus decides; block is committed with `ATTACKER_ADDRESS` as sequencer and the wrong block hash anchored to L1. [10](#0-9) [11](#0-10)

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L107-108)
```rust
    pub builder: ContractAddress,
    /// L1 data availability mode.
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L75-85)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L153-171)
```rust
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
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L243-247)
```rust
    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L312-321)
```rust
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L224-235)
```rust
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L256-259)
```rust
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L163-171)
```rust
pub(crate) fn proposal_commitment_from(
    partial: PartialBlockHash,
    fee_proposal: Option<GasPrice>,
) -> ProposalCommitment {
    let Some(fee_proposal) = fee_proposal else {
        return ProposalCommitment(partial.0);
    };
    ProposalCommitment(Poseidon::hash_array(&[partial.0, Felt::from(fee_proposal.0)]))
}
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L880-900)
```rust
                let proposal_init_validation = ProposalInitValidation {
                    height: init.height,
                    block_timestamp_window_seconds: self
                        .config
                        .static_config
                        .block_timestamp_window_seconds,
                    previous_proposal_init: self.previous_proposal_init.clone(),
                    l1_da_mode: self.l1_da_mode,
                    l2_gas_price_fri: self
                        .config
                        .dynamic_config
                        .override_l2_gas_price_fri
                        .map(GasPrice)
                        .unwrap_or(self.l2_gas_price),
                    starknet_version: StarknetVersion::LATEST,
                    fee_actual: compute_fee_actual(
                        &self.fee_proposals_window,
                        init.height,
                        VersionedConstants::latest_constants().fee_proposal_window_size,
                    ),
                };
```
