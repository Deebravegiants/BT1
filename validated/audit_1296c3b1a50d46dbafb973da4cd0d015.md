### Title
Unvalidated `builder` Field in `ProposalInit` Allows Malicious Proposer to Redirect Sequencer Fees and Corrupt Block Execution Context — (`crates/apollo_consensus_orchestrator/src/utils.rs`)

---

### Summary

`ProposalInit.builder` is a proposer-supplied field that is passed directly as `sequencer_address` into every block's `BlockInfo` during both proposal building and validation. The validator's `is_proposal_init_valid` function never checks `builder` against any locally-trusted reference. A malicious proposer can set `builder` to an arbitrary address; all validators will execute the block with that address as the sequencer, causing fee transfers to be redirected to the attacker-controlled address and exposing a wrong `sequencer_address` to every contract that calls `get_execution_info`.

---

### Finding Description

`convert_to_sn_api_block_info` maps `ProposalInit` to `starknet_api::block::BlockInfo`:

```rust
// crates/apollo_consensus_orchestrator/src/utils.rs  line 329-347
Ok(starknet_api::block::BlockInfo {
    block_number: init.height,
    block_timestamp: BlockTimestamp(init.timestamp),
    sequencer_address: init.builder,   // ← taken verbatim from the wire
    gas_prices: GasPrices { ... },
    ...
})
``` [1](#0-0) 

This `BlockInfo` is forwarded to the batcher as `ValidateBlockInput.block_info` inside `initiate_validation`:

```rust
// crates/apollo_consensus_orchestrator/src/validate_proposal.rs  line 455-467
let input = ValidateBlockInput {
    proposal_id,
    deadline: ...,
    retrospective_block_hash: ...,
    block_info: convert_to_sn_api_block_info(init)?,   // init.builder → sequencer_address
};
batcher.validate_block(input).await?;
``` [2](#0-1) 

The validator's `is_proposal_init_valid` checks `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, L1 gas prices (within margin), and `fee_proposal_fri` (within margin). It never checks `builder`:

```rust
// crates/apollo_consensus_orchestrator/src/validate_proposal.rs  line 312-321
if !(init_proposed.height == proposal_init_validation.height
    && init_proposed.l1_da_mode == proposal_init_validation.l1_da_mode
    && init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri)
{
    return Err(ValidateProposalError::InvalidProposalInit(...));
}
// No check on init_proposed.builder
``` [3](#0-2) 

`ProposalInitValidation` (the locally-derived reference struct) does not carry a `builder` field at all:

```rust
// crates/apollo_consensus_orchestrator/src/validate_proposal.rs  line 74-85
pub(crate) struct ProposalInitValidation {
    pub height: BlockNumber,
    pub block_timestamp_window_seconds: u64,
    pub previous_proposal_init: Option<PreviousProposalInitInfo>,
    pub l1_da_mode: L1DataAvailabilityMode,
    pub l2_gas_price_fri: GasPrice,
    pub starknet_version: StarknetVersion,
    pub fee_actual: Option<GasPrice>,
    // no builder / sequencer_address field
}
``` [4](#0-3) 

The honest proposer sets `builder` from its own node configuration:

```rust
// crates/apollo_consensus_orchestrator/src/build_proposal.rs  line 169-188
let init = ProposalInit {
    ...
    builder: args.builder_address,   // from local config
    ...
};
``` [5](#0-4) 

A malicious proposer can substitute any address here. Because every validator calls `convert_to_sn_api_block_info(init)` with the same wire-supplied `init`, all validators execute the block with the attacker-chosen `sequencer_address`. The `ProposalFin` commitment comparison at line 244 of `validate_proposal.rs` then passes (both sides computed the commitment over the same wrong `sequencer_address`), and the block is committed. [6](#0-5) 

---

### Impact Explanation

**Fee redirection (economic impact).** In Starknet, transaction fees are transferred to `block_info.sequencer_address`. A malicious proposer sets `builder` to an attacker-controlled address; every fee-paying transaction in that block transfers its fee to the attacker instead of the legitimate sequencer. This is a direct, per-block economic loss proportional to total fees in the block.

**Wrong `sequencer_address` exposed to contracts.** The `get_execution_info` syscall returns `block_info.sequencer_address` to executing contracts. Any contract that branches on the sequencer address (e.g., access-control, fee-rebate, or oracle logic) will observe the attacker-supplied value, producing wrong execution results and wrong state.

**Wrong block header committed.** The sequencer address is part of `BlockHeaderWithoutHash` and therefore part of the block hash and state commitment. A committed block with a wrong sequencer address produces a wrong authoritative on-chain state root.

---

### Likelihood Explanation

Any validator that wins a proposal round can exploit this. In a rotating-proposer BFT system, every validator eventually proposes. No special privilege beyond being a committee member is required. The attack is silent: the `ProposalFin` commitment check passes because all validators independently reproduce the same wrong execution, so no mismatch is detected.

---

### Recommendation

Add `builder` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid`:

```rust
pub(crate) struct ProposalInitValidation {
    ...
    pub expected_builder: ContractAddress,  // from local node config
}

// in is_proposal_init_valid:
if init_proposed.builder != proposal_init_validation.expected_builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!("builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.expected_builder, init_proposed.builder),
    ));
}
```

The `expected_builder` should be derived from the same source as `args.builder_address` in `ProposalBuildArguments` — the node's own configuration — so the validator independently knows the correct value without trusting the proposer.

---

### Proof of Concept

1. Malicious validator wins round `r` at height `h` and becomes proposer.
2. It constructs `ProposalInit` with `builder = <attacker_wallet>` (all other fields valid).
3. It streams the proposal to all peers.
4. Each honest validator calls `is_proposal_init_valid` — passes (no `builder` check).
5. Each honest validator calls `initiate_validation` → `convert_to_sn_api_block_info` → `sequencer_address = <attacker_wallet>`.
6. Blockifier executes all transactions; fee transfers credit `<attacker_wallet>`.
7. `finish_proposal` returns a `partial_block_hash` computed over the block with `sequencer_address = <attacker_wallet>`.
8. `proposal_commitment_from(partial_block_hash, fee_proposal)` matches the proposer's `ProposalFin.proposal_commitment` — no mismatch.
9. Consensus decides; block committed with wrong sequencer address and all fees redirected.

### Citations

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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-475)
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
