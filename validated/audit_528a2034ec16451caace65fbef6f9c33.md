### Title
`ProposalInit.builder` Is Never Validated by the Validator, Allowing a Malicious Proposer to Inject an Arbitrary `sequencer_address` into the Block Hash - (File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs)

### Summary

`ProposalInit` carries a `builder` field ("Address of the one who builds/sequences the block") that the proposer sets from its own configuration. The validator's `is_proposal_init_valid` function checks many `ProposalInit` fields but never checks `builder`. Because `builder` is passed through `convert_to_sn_api_block_info` as `block_info.sequencer_address`, and `sequencer_address` is a direct input to `PartialBlockHashComponents` and therefore to the final block hash, a Byzantine proposer can inject any address as the sequencer of a committed block.

### Finding Description

`ProposalInit` is defined with two address fields:

```rust
/// Address of the one who proposed the block in consensus.
pub proposer: ContractAddress,
/// Address of the one who builds/sequences the block.
pub builder: ContractAddress,
``` [1](#0-0) 

The proposer sets `builder` from its own local configuration:

```rust
let init = ProposalInit {
    proposer: args.build_param.proposer,
    builder: args.builder_address,
    ...
};
``` [2](#0-1) 

`convert_to_sn_api_block_info(&init)` is called in both the proposer path (`initiate_build`) and the validator path (`initiate_validation`) to produce the `BlockInfo` that is handed to the batcher. `BlockInfo.sequencer_address` is populated from `init.builder`. The batcher then builds `PartialBlockHashComponents` from that `BlockInfo`:

```rust
let partial_block_hash_components =
    PartialBlockHashComponents::new(&block_info, header_commitments);
``` [3](#0-2) 

`PartialBlockHashComponents::new` stores `sequencer_address` directly:

```rust
sequencer: SequencerContractAddress(block_info.sequencer_address),
``` [4](#0-3) 

`sequencer` is then chained into the Poseidon block hash:

```rust
.chain(&partial_block_hash_components.sequencer.0)
``` [5](#0-4) 

The validator's `is_proposal_init_valid` checks `timestamp`, `starknet_version`, `version_constant_commitment`, `height`, `l1_da_mode`, `l2_gas_price_fri`, L1 gas prices, and `fee_proposal_fri` — but **never checks `builder`**: [6](#0-5) 

The `ProposalInitValidation` struct that carries the validator's reference values also has no `builder` field: [7](#0-6) 

Because both the proposer and the validator derive `block_info` from the same received `ProposalInit.builder`, they compute identical `PartialBlockHash` values and the `ProposalFinMismatch` guard does not fire:

```rust
if built_block != received_fin.proposal_commitment {
    return Err(ValidateProposalError::ProposalFinMismatch);
}
``` [8](#0-7) 

The block is therefore committed with the attacker-supplied `sequencer_address` baked into the block hash and the block header.

### Impact Explanation

A Byzantine proposer sets `ProposalInit.builder` to an arbitrary address (e.g., `0x0` or a competitor's address). The validator accepts the proposal without objection. The batcher on the validator side computes `PartialBlockHashComponents` with the injected `sequencer_address`, producing the same `ProposalCommitment` as the proposer. Consensus reaches agreement and the block is committed. Every subsequent RPC call to `starknet_getBlockWithTxHashes` / `starknet_getBlockWithTxs` returns the attacker-chosen `sequencer_address` as an authoritative value. The block hash stored in storage is also wrong because `sequencer_address` is a direct input to `calculate_block_hash`.

This matches: **High — RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value.**

### Likelihood Explanation

Any single Byzantine proposer (one of up to `f` faulty nodes in a BFT network) can trigger this on every block they are elected to propose. No special privilege beyond being a consensus participant is required. The attack is silent — no error is logged, no metric fires, and the `ProposalFinMismatch` guard is bypassed by design.

### Recommendation

Add a `builder` field to `ProposalInitValidation` populated from the validator's own configured `builder_address`. In `is_proposal_init_valid`, reject any `ProposalInit` whose `builder` does not equal the locally expected value:

```rust
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

### Proof of Concept

1. A Byzantine proposer node sets `builder_address = ContractAddress(0xdead)` in its local config (or patches `initiate_build` to override `builder`).
2. It wins a consensus round and calls `build_proposal`. `ProposalInit.builder = 0xdead` is broadcast to all validators.
3. Each honest validator calls `validate_proposal` → `is_proposal_init_valid`. No check on `builder` exists; validation passes.
4. `initiate_validation` calls `convert_to_sn_api_block_info(&init)`, producing `BlockInfo { sequencer_address: 0xdead, ... }`.
5. The batcher computes `PartialBlockHashComponents { sequencer: 0xdead, ... }` and returns a `ProposalCommitment` that matches the proposer's (both used `0xdead`).
6. `built_block == received_fin.proposal_commitment` → no `ProposalFinMismatch`.
7. `decision_reached` commits the block. `starknet_getBlockWithTxHashes` returns `sequencer_address: 0xdead` for that block number.

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L102-107)
```rust
    /// Address of the one who proposed the block in consensus.
    pub proposer: ContractAddress,
    /// Block timestamp.
    pub timestamp: u64,
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
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

**File:** crates/apollo_batcher/src/block_builder.rs (L178-179)
```rust
        let partial_block_hash_components =
            PartialBlockHashComponents::new(&block_info, header_commitments);
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L231-231)
```rust
            sequencer: SequencerContractAddress(block_info.sequencer_address),
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L258-258)
```rust
            .chain(&partial_block_hash_components.sequencer.0)
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L244-247)
```rust
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
