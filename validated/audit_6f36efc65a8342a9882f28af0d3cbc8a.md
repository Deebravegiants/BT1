### Title
Unvalidated `builder` Field in `ProposalInit` Allows Malicious Proposer to Inject Arbitrary `sequencer_address` into Block Hash and Execution Context - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`ProposalInit` carries two identity fields: `proposer` (the consensus proposer, validated against the committee) and `builder` (the block-builder/sequencer address, **never validated**). The `builder` field flows directly into the `sequencer_address` used for block execution and `PartialBlockHashComponents`, which is the input to the block hash. A malicious but authenticated proposer can set `builder` to any arbitrary address, causing every validator to execute the block and commit a block hash with a wrong `sequencer_address`.

---

### Finding Description

**Two distinct identity fields in `ProposalInit`:**

`ProposalInit` has both a `proposer` and a `builder` field: [1](#0-0) 

The `proposer` field is validated in `single_height_consensus.rs::handle_proposal` against the committee-derived expected proposer: [2](#0-1) 

**`builder` is never validated in `is_proposal_init_valid`:**

The orchestrator-level validation function `is_proposal_init_valid` checks `height`, `l1_da_mode`, `l2_gas_price_fri`, timestamp bounds, `starknet_version`, `version_constant_commitment`, L1 gas prices, and `fee_proposal_fri` — but contains **no check on `init.builder`**: [3](#0-2) 

**`builder` flows into `sequencer_address` used for execution and block hash:**

`initiate_validation` calls `convert_to_sn_api_block_info(init)` and passes the resulting `block_info` (which contains `sequencer_address` derived from `init.builder`) to the batcher for execution: [4](#0-3) 

After decision, `update_state_sync_with_new_block` explicitly assigns `init.builder` as the sequencer: [5](#0-4) 

**`sequencer_address` is a direct input to the block hash:**

`PartialBlockHashComponents::new` takes `block_info.sequencer_address` and stores it as `sequencer`, which is then chained into the Poseidon block hash: [6](#0-5) [7](#0-6) 

**`builder` is a static local config, not a free parameter:**

The node configuration treats `builder_address` as a static, locally-configured value: [8](#0-7) 

In `initiate_build`, the proposer sets `builder: args.builder_address` from its own local config: [9](#0-8) 

The validator has its own `builder_address` config but never checks that `init.builder` matches it.

---

### Impact Explanation

A malicious but authenticated proposer sets `init.builder` to an attacker-controlled address. Every validator's `is_proposal_init_valid` passes without objection. The batcher executes all transactions with `sequencer_address = attacker_address`. Consequences:

1. **Wrong block hash committed**: `PartialBlockHashComponents.sequencer` contains the attacker's address; the resulting `PartialBlockHash` and final block hash are wrong. This is a wrong-state commitment anchored to L1.
2. **Fee redirection**: Starknet fee transfers are directed to `sequencer_address`. With a spoofed `builder`, all transaction fees in the block are paid to the attacker's address instead of the legitimate sequencer.
3. **Syscall poisoning**: Any contract calling `get_sequencer_address()` during execution receives the attacker's address. Contracts that gate privileged operations on the sequencer address (e.g., system contracts) can be bypassed or manipulated.

---

### Likelihood Explanation

Requires a malicious but legitimately authenticated proposer — i.e., a validator that has been selected by the committee for a given height/round. In a decentralized validator set this is a realistic threat. No external attacker capability is needed; the proposer simply sets one field in the `ProposalInit` message it broadcasts.

---

### Recommendation

Add a check for `init.builder` inside `is_proposal_init_valid` in `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`. The validator should compare `init_proposed.builder` against the locally-trusted `builder_address` from its static config (surfaced through `ProposalInitValidation`). If they differ, return `Err(ValidateProposalError::InvalidProposalInit(...))` with a descriptive message, mirroring the existing pattern used for `l2_gas_price_fri`, `l1_da_mode`, and `height`.

---

### Proof of Concept

1. Attacker is a committee-selected proposer for height H, round R.
2. Attacker constructs `ProposalInit { proposer: <legitimate_proposer>, builder: <attacker_address>, ... }`.
3. Attacker broadcasts this `ProposalInit` to all validators.
4. Each validator calls `is_proposal_init_valid` — no check on `builder` exists; validation passes.
5. `initiate_validation` calls `convert_to_sn_api_block_info(init)` → `block_info.sequencer_address = attacker_address`.
6. Batcher executes all transactions with `sequencer_address = attacker_address`; fee transfers go to `attacker_address`.
7. `BlockExecutionArtifacts::new` calls `PartialBlockHashComponents::new(&block_info, ...)` → `sequencer = attacker_address`.
8. `PartialBlockHash::from_partial_block_hash_components` hashes `attacker_address` into the block hash.
9. Consensus reaches decision; the committed block hash encodes `attacker_address` as the sequencer, and all fees for that block have been redirected.

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

**File:** crates/apollo_consensus/src/single_height_consensus.rs (L114-120)
```rust
        let Ok(proposer_id) = self.committee.get_proposer(height, init.round) else {
            return VecDeque::new();
        };
        if init.proposer != proposer_id {
            warn!("Invalid proposer: expected {:?}, got {:?}", proposer_id, init.proposer);
            return VecDeque::new();
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L397-412)
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
            l1_da_mode: init.l1_da_mode,
            fee_proposal_fri: init.fee_proposal_fri,
            // TODO(guy.f): Figure out where/if to get the values below from and fill them.
            ..Default::default()
        };
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-260)
```rust
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
            .chain(&block_commitments.concatenated_counts)
```

**File:** crates/apollo_node/resources/config_schema.json (L2797-2801)
```json
  "consensus_manager_config.context_config.static_config.builder_address": {
    "description": "The address of the contract that builds the block.",
    "privacy": "Public",
    "value": "0x0"
  },
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
