### Title
Unvalidated `builder` Field in `ProposalInit` Allows Proposer to Redirect All Block Fees and Corrupt Block Hash - (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`ProposalInit` carries a `builder` field (the sequencer/block-builder address). `is_proposal_init_valid()` validates height, L1/L2 gas prices, DA mode, starknet version, and fee proposal, but **never checks `builder`**. `convert_to_sn_api_block_info()` maps `init.builder` directly to `BlockInfo.sequencer_address`, which is the fee-transfer recipient for every transaction in the block and is hashed into the canonical block hash. Any proposer can set `builder` to an arbitrary address, redirecting all block fees to themselves and producing a block hash that encodes the wrong sequencer.

### Finding Description

`ProposalInit` has two identity fields:

```rust
pub proposer: ContractAddress,   // consensus identity, validated by committee
pub builder: ContractAddress,    // block-builder identity, NEVER validated
```

`is_proposal_init_valid()` checks `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, all four L1 gas prices, and `fee_proposal_fri`. The `builder` field is absent from `ProposalInitValidation` entirely and is never compared against any locally-trusted reference.

`convert_to_sn_api_block_info()` then unconditionally promotes the proposer-supplied value:

```rust
Ok(starknet_api::block::BlockInfo {
    ...
    sequencer_address: init.builder,   // ← attacker-controlled
    ...
})
```

This `BlockInfo` is forwarded to the batcher via `ValidateBlockInput` in `initiate_validation()`. The batcher executes every transaction in the block with this `BlockInfo`, so:

1. **Fee transfer recipient** — every fee transfer calls `transfer(recipient=block_info.sequencer_address, ...)`, sending fees to the attacker's address.
2. **Block hash** — `PartialBlockHashComponents::new(block_info, ...)` sets `sequencer: SequencerContractAddress(block_info.sequencer_address)`, which is chained into `calculate_block_hash()`. All validators accept the same unvalidated `builder`, so they all compute and commit the same (corrupted) block hash.
3. **Execution context** — contracts that call `get_execution_info().block_info.sequencer_address` observe the attacker's address.

### Impact Explanation

- **Fee theft (economic impact)**: All transaction fees in the block are transferred to the attacker-controlled `builder` address instead of the legitimate sequencer. This is a direct, quantifiable loss of funds for the sequencer operator.
- **Wrong block hash committed to L1**: The canonical block hash encodes the wrong `sequencer_address`. Every downstream consumer (state sync, L1 anchoring, proof verification) receives a hash derived from attacker-supplied data.
- **Wrong execution context for contracts**: Any contract logic that branches on `get_execution_info().block_info.sequencer_address` (e.g., fee-token contracts, access-control checks) executes incorrectly.

### Likelihood Explanation

The proposer role rotates among all committee members. Any validator that reaches its proposer turn can exploit this with zero preconditions — no special approvals, no prior state, no external dependencies. The attack is a single-field modification in the outgoing `ProposalInit` message. Validators accept the proposal because `is_proposal_init_valid()` has no guard for `builder`.

### Recommendation

Add `builder` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid()`:

```rust
pub(crate) struct ProposalInitValidation {
    ...
    pub builder: ContractAddress,   // add this
}
```

```rust
if init_proposed.builder != proposal_init_validation.builder {
    return Err(ValidateProposalError::InvalidProposalInit(...));
}
```

The validator's own `builder_address` (already stored in `SequencerConsensusContext`) should be the reference value, populated when constructing `ProposalInitValidation` in `validate_proposal()`.

### Proof of Concept

1. Attacker controls a validator node that is scheduled to propose at height H.
2. In `initiate_build()`, the attacker patches the outgoing `ProposalInit` to set `builder = attacker_address` instead of `self.builder_address`.
3. The `ProposalInit` is broadcast to all peers.
4. Each peer calls `validate_proposal()` → `is_proposal_init_valid()`. None of the checks cover `builder`. The proposal passes validation.
5. `initiate_validation()` calls `convert_to_sn_api_block_info(&init)`, producing `BlockInfo { sequencer_address: attacker_address, ... }`.
6. The batcher executes all transactions with this `BlockInfo`. Every fee transfer sends funds to `attacker_address`.
7. `calculate_block_hash()` hashes `attacker_address` as the sequencer. All validators commit this hash.
8. The attacker receives all fees from block H; the legitimate sequencer receives nothing.

---

**Key code locations:**

`ProposalInit.builder` field (never validated): [1](#0-0) 

`is_proposal_init_valid()` — complete list of checks, `builder` absent: [2](#0-1) 

`convert_to_sn_api_block_info()` — `builder` promoted to `sequencer_address` without validation: [3](#0-2) 

`ProposalInitValidation` — no `builder` field: [4](#0-3) 

`PartialBlockHashComponents::new()` — `sequencer_address` enters block hash: [5](#0-4)

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L107-107)
```rust
    pub builder: ContractAddress,
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

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-333)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L231-231)
```rust
            sequencer: SequencerContractAddress(block_info.sequencer_address),
```
