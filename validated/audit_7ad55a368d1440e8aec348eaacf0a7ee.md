### Title
Unvalidated `ProposalInit.builder` Field Allows Malicious Proposer to Inject Arbitrary `sequencer_address` into Committed Block — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`, `crates/apollo_consensus_orchestrator/src/utils.rs`)

---

### Summary

`ProposalInit` carries two identity fields: `proposer` (the consensus identity, validated against the committee) and `builder` (the block-building sequencer address, **never validated**). `convert_to_sn_api_block_info` maps `init.builder` directly to `sequencer_address` in `BlockInfo`. Validators execute and commit the block using that proposer-supplied address without any check. A malicious proposer can set `builder` to any arbitrary address, causing every block they propose to be committed with a wrong `sequencer_address`.

---

### Finding Description

`ProposalInit` has two distinct address fields:

```
proposer: ContractAddress  // "Address of the one who proposed the block in consensus"
builder:  ContractAddress  // "Address of the one who builds/sequences the block"
``` [1](#0-0) 

`convert_to_sn_api_block_info` maps `init.builder` to `sequencer_address`:

```rust
sequencer_address: init.builder,
``` [2](#0-1) 

This function is called on both the proposer side (`build_proposal.rs`) and the validator side (`validate_proposal.rs`, `sequencer_consensus_context.rs`): [3](#0-2) [4](#0-3) 

`is_proposal_init_valid` validates `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, timestamp, and L1 gas prices — but **never checks `init.builder`**: [5](#0-4) 

The `proposer` field is checked against the committee-derived expected proposer in `handle_proposal`: [6](#0-5) 

But `builder` has no analogous check anywhere in the validation pipeline.

The proposer sets `builder` from its own local configuration (`args.builder_address`): [7](#0-6) 

Because both proposer and validator call `convert_to_sn_api_block_info(init)` with the same `init.builder`, they compute the same `ProposalCommitment`, so the fin-comparison check at line 244 of `validate_proposal.rs` does **not** detect the manipulation: [8](#0-7) 

The committed block header then carries the attacker-controlled `sequencer_address`, which is also propagated to state sync: [9](#0-8) 

---

### Impact Explanation

1. **Wrong `sequencer_address` in execution context**: Every transaction in the block executes with the attacker-supplied `sequencer_address` in `BlockInfo`. Contracts that call `get_execution_info` and inspect `block_info.sequencer_address` (e.g., for access control or fee routing) receive the wrong value. This is a wrong syscall result from blockifier execution logic.

2. **Wrong block header committed to state and L1**: The `sequencer_address` is part of the block header stored in state and eventually anchored to L1. The committed block hash reflects the attacker-controlled address, corrupting the authoritative chain state.

3. **Fee misdirection**: In Starknet, transaction fees are transferred from the sender to the `sequencer_address`. A malicious proposer can redirect all fees from every block they propose to any address they choose.

---

### Likelihood Explanation

Low. The attacker must be a validator selected as the round's proposer. However, in a decentralized validator set any validator can be selected, and the window repeats every time that validator is chosen. No special capability beyond being a legitimate validator is required.

---

### Recommendation

In `is_proposal_init_valid`, validate that `init.builder` matches the expected sequencer address for this node/network. The simplest approach is to treat `builder` as a consensus-enforced field: either require `builder == proposer` (if they are always the same entity), or include the expected `builder` in `ProposalInitValidation` and reject proposals where `init.builder` does not match. This mirrors how `init.proposer` is already validated against the committee-derived expected proposer.

---

### Proof of Concept

1. Validator A is selected as proposer for height H, round 0.
2. A constructs `ProposalInit` with `builder = <attacker_controlled_address>` instead of its legitimate sequencer address.
3. A streams the proposal to all peers.
4. Each validator calls `is_proposal_init_valid` — the check passes because `builder` is never inspected.
5. Each validator calls `convert_to_sn_api_block_info(init)`, producing `BlockInfo { sequencer_address: <attacker_controlled_address>, ... }`.
6. The batcher executes all transactions with that `sequencer_address` in the execution context.
7. Both proposer and validators compute the same `ProposalCommitment` (both used the same `init.builder`), so the fin-comparison passes.
8. `decision_reached` commits the block. `update_state_sync_with_new_block` records `sequencer = SequencerContractAddress(init.builder)` — the attacker-controlled address — in the block header.
9. All fee transfers in that block go to `<attacker_controlled_address>`. All contracts that read `get_execution_info().block_info.sequencer_address` see the wrong value. The committed block hash on L1 reflects the wrong sequencer.

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

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-333)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L243-247)
```rust
    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-467)
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
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L397-407)
```rust
        let sequencer = SequencerContractAddress(init.builder);

        let block_header_without_hash = BlockHeaderWithoutHash {
            block_number: height,
            l1_gas_price,
            l1_data_gas_price,
            l2_gas_price,
            l2_gas_consumed: l2_gas_used,
            next_l2_gas_price: self.l2_gas_price,
            sequencer,
            timestamp: BlockTimestamp(init.timestamp),
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

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L169-175)
```rust
    let init = ProposalInit {
        height: args.build_param.height,
        round: args.build_param.round,
        valid_round: args.build_param.valid_round,
        proposer: args.build_param.proposer,
        builder: args.builder_address,
        timestamp,
```
