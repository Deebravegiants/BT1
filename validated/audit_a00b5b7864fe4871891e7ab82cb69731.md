### Title
Unvalidated `ProposalInit.builder` Field Allows Proposer to Inject Arbitrary `sequencer_address` into Block Execution and Block Hash — (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` validates most `ProposalInit` fields but never checks `builder`. That field is used verbatim as `sequencer_address` in `BlockInfo`, which feeds both the blockifier execution context (readable by every contract via `get_execution_info`) and the `PartialBlockHashComponents` that determine the canonical block hash. A malicious-but-legitimate proposer can set `builder` to any address, causing every validator to execute the block with the wrong sequencer address and commit a block hash that encodes that wrong address.

---

### Finding Description

**Unvalidated field.** `ProposalInitValidation` contains `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, L1 gas prices, and `fee_actual`. It has no `builder` field, so `is_proposal_init_valid` never compares `init_proposed.builder` against any locally-trusted value. [1](#0-0) 

The combined guard at lines 312–321 checks `height`, `l1_da_mode`, and `l2_gas_price_fri` but omits `builder` entirely. [2](#0-1) 

**Propagation into execution.** `convert_to_sn_api_block_info` maps `init.builder` directly to `sequencer_address` in the `BlockInfo` that is handed to the batcher for both proposal and validation paths. [3](#0-2) 

**Propagation into block hash.** `PartialBlockHashComponents::new` copies `block_info.sequencer_address` into the `sequencer` field, which is then hashed into the canonical block hash by `calculate_block_hash`. [4](#0-3) [5](#0-4) 

The Cairo OS confirms `sequencer_address` is the third element hashed into `STARKNET_BLOCK_HASH1`. [6](#0-5) 

**Proposer sets `builder` freely.** During `initiate_build`, the proposer writes its own `builder_address` config value into `ProposalInit.builder` with no constraint from the network. [7](#0-6) 

Because the validator never checks this field, any value the proposer places there passes `is_proposal_init_valid`, is forwarded to `initiate_validation` → `validate_block`, and is used by the batcher to execute every transaction in the block. [8](#0-7) 

---

### Impact Explanation

**Wrong execution result (Critical).** Every transaction in the block is executed with the attacker-controlled `sequencer_address`. Contracts that call `get_execution_info` to read the sequencer address — for fee routing, access control, or any other purpose — receive the injected value. This is a wrong syscall result for every accepted transaction in the block.

**Wrong block hash (Critical).** The `PartialBlockHash` committed by consensus and stored in `ProposalCommitment` encodes the injected `sequencer_address`. The resulting canonical block hash diverges from what it would be under the legitimate `builder_address`. Because the retrospective block hash of this block is later used to validate future proposals, the corruption propagates forward.

**Wrong fee collection (Critical, economic).** Starknet routes transaction fees to `sequencer_address`. An attacker who sets `builder` to an address they control diverts all fees from the block to themselves.

---

### Likelihood Explanation

The trigger requires the attacker to be the elected proposer for a round — a legitimate consensus participant. No external or unprivileged actor is needed. The proposer is already authenticated (the `proposer` field is checked against the committee in `manager.rs`), but `builder` is a separate, unchecked field. Any proposer who deviates from the honest protocol can exploit this every time they are elected. [9](#0-8) 

---

### Recommendation

1. Add `expected_builder: ContractAddress` to `ProposalInitValidation`, populated from `ContextStaticConfig.builder_address`.
2. In `is_proposal_init_valid`, add an exact-equality check:
   ```rust
   if init_proposed.builder != proposal_init_validation.expected_builder {
       return Err(ValidateProposalError::InvalidProposalInit(...));
   }
   ```
3. Add a test analogous to `invalid_proposal_init` that mutates `init.builder` and asserts rejection.

---

### Proof of Concept

1. A legitimate proposer is elected for height `H`, round `R`.
2. It constructs `ProposalInit` with all honest fields except `builder = ContractAddress::from(ATTACKER_ADDR)`.
3. It streams `ProposalPart::Init(init)` to all validators.
4. Each validator calls `is_proposal_init_valid` — the function checks `height`, `l1_da_mode`, `l2_gas_price_fri`, L1 prices, `starknet_version`, `version_constant_commitment`, and `fee_proposal_fri`. None of these checks involve `builder`. The function returns `Ok(())`.
5. `initiate_validation` calls `convert_to_sn_api_block_info(&init)`, which sets `sequencer_address = ATTACKER_ADDR` in `BlockInfo`.
6. The batcher executes all transactions with `sequencer_address = ATTACKER_ADDR`. Every `get_execution_info` syscall returns `ATTACKER_ADDR` as the sequencer.
7. `PartialBlockHashComponents::new` records `sequencer = ATTACKER_ADDR`. The resulting `PartialBlockHash` — and therefore `ProposalCommitment` — encodes the attacker's address.
8. Consensus reaches decision; the block is committed with the wrong sequencer address in both execution state and the canonical block hash.

### Citations

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

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-347)
```rust
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-282)
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
}
```

**File:** crates/apollo_starknet_os_program/src/cairo/starkware/starknet/core/os/block_hash.cairo (L30-50)
```text
    let hash_state = hash_init();
    with hash_state {
        hash_update_single(BLOCK_HASH_VERSION);
        hash_update_single(block_info.block_number);
        hash_update_single(state_root);
        hash_update_single(block_info.sequencer_address);
        hash_update_single(block_info.block_timestamp);
        hash_update_single(header_commitments.packed_lengths);
        hash_update_single(header_commitments.state_diff_commitment);
        hash_update_single(header_commitments.transaction_commitment);
        hash_update_single(header_commitments.event_commitment);
        hash_update_single(header_commitments.receipt_commitment);
        hash_update_single(gas_prices_hash);
        hash_update_single(starknet_version);
        hash_update_single(0);
        hash_update_single(previous_block_hash);
    }

    let block_hash = hash_finalize(hash_state=hash_state);
    return block_hash;
}
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L169-188)
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
```

**File:** crates/apollo_consensus/src/manager.rs (L849-866)
```rust
                let Ok(proposer) =
                    get_proposer_for_height(&self.committee_provider, init.height, init.round)
                        .await
                else {
                    warn!(
                        "VIRTUAL_PROPOSER_LOOKUP_FAILED: Failed to determine virtual proposer for \
                         height {} round {}. Dropping proposal.",
                        init.height.0, init.round
                    );
                    return Ok(VecDeque::new());
                };
                if proposer != init.proposer {
                    warn!(
                        "Invalid proposer for height {} and round {}: expected {:?}, got {:?}",
                        init.height.0, init.round, proposer, init.proposer
                    );
                    return Ok(VecDeque::new());
                }
```
