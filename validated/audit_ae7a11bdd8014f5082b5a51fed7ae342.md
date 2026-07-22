### Title
Unvalidated `builder` Field in `ProposalInit` Allows Proposer to Inject Arbitrary `sequencer_address` into Block Execution Context and Committed Header - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`ProposalInit` carries a `builder` field (the address of the block builder/sequencer). This field is accepted verbatim from the network and is never checked in `is_proposal_init_valid`. It is then used directly as the `sequencer_address` in the block's `BlockInfo` for execution and in the committed block header. Any proposer in the committee can set `builder` to an arbitrary address, corrupting the sequencer address visible to all contracts via `get_block_info()` and redirecting sequencer fee payments.

---

### Finding Description

`ProposalInit` has two distinct identity fields:

```
pub proposer: ContractAddress,  // consensus identity
pub builder: ContractAddress,   // block builder / sequencer_address
``` [1](#0-0) 

The `proposer` field is checked at the consensus manager layer against the committee-derived expected proposer:

```rust
if proposer != init.proposer { ... return Ok(VecDeque::new()); }
``` [2](#0-1) 

However, `is_proposal_init_valid` — the function that validates all `ProposalInit` fields before the proposal is accepted — checks `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, all four L1 gas prices, and `fee_proposal_fri`, but **never checks `builder`**: [3](#0-2) 

`ProposalInitValidation` — the struct holding the expected values — has no `builder` field at all: [4](#0-3) 

The unchecked `init.builder` is then used in two critical places:

**1. `convert_to_sn_api_block_info` maps `init.builder` → `sequencer_address` in `BlockInfo`:**

```rust
sequencer_address: init.builder,
``` [5](#0-4) 

This `BlockInfo` is passed to the batcher for both proposal building and validation: [6](#0-5) 

**2. `update_state_sync_with_new_block` commits `init.builder` as the block's `sequencer` in the block header:**

```rust
let sequencer = SequencerContractAddress(init.builder);
``` [7](#0-6) 

---

### Impact Explanation

The `sequencer_address` in `BlockInfo` is exposed to every contract via the `get_block_info()` syscall (returning `block_info.sequencer_address`): [8](#0-7) [9](#0-8) 

A malicious proposer can set `builder` to any address they control. This causes:

1. **Wrong `sequencer_address` in execution context**: Every contract in the block that calls `get_block_info()` sees the attacker-controlled address as the sequencer. Contracts that gate logic on `sequencer_address` (e.g., fee token contracts, access-controlled contracts) will behave incorrectly.

2. **Sequencer fee misdirection**: In Starknet, transaction fees are paid to `sequencer_address`. By substituting their own address as `builder`, a malicious proposer redirects all fee payments for the block to themselves, stealing fees from the legitimate sequencer.

3. **Wrong committed block header**: The `sequencer` field in the finalized block header is `init.builder`, so the on-chain record is permanently corrupted with the attacker's address.

This matches the "Wrong state, receipt, event … or revert result from blockifier/syscall/execution logic" and "Incorrect fee … balance … with economic impact" impact categories.

---

### Likelihood Explanation

Any validator that wins a proposal slot can exploit this. The proposer is authenticated (committee membership), but the `builder` field is entirely under the proposer's control with no constraint. The attack requires no special tooling — the proposer simply sets `builder` to their own address when constructing `ProposalInit` in `initiate_build`. Validators accept the proposal without checking `builder`, so the corrupted value flows through to execution and commitment.

---

### Recommendation

Add a `builder` field to `ProposalInitValidation` containing the locally-configured expected builder address, and add a check in `is_proposal_init_valid`:

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

The `expected_builder` should be sourced from the node's own configuration (the same `builder_address` used in `ProposalBuildArguments`), not from the network message. [10](#0-9) 

---

### Proof of Concept

1. Attacker is a legitimate validator and wins a proposal slot at height H.
2. In `initiate_build`, attacker sets `builder: attacker_controlled_address` instead of the node's configured `builder_address`.
3. The `ProposalInit` is broadcast with `builder = attacker_controlled_address`.
4. Peer validators call `is_proposal_init_valid` — no check on `builder` exists, so validation passes.
5. `initiate_validation` calls `convert_to_sn_api_block_info(&init)`, producing a `BlockInfo` with `sequencer_address = attacker_controlled_address`.
6. The batcher executes all transactions in the block with `sequencer_address = attacker_controlled_address`. All fee payments go to the attacker's address.
7. `update_state_sync_with_new_block` commits the block header with `sequencer = attacker_controlled_address`.
8. The block is finalized. The attacker has collected all sequencer fees for height H, and the block header permanently records the wrong sequencer address. [11](#0-10) [12](#0-11)

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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-322)
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
    let (l1_gas_prices_fri, l1_gas_prices_wei) = get_l1_prices_in_fri_and_wei(
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-474)
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
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L301-347)
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
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L394-412)
```rust
        let l1_gas_price = cende_block_info.gas_prices.l1_gas_price_per_token();
        let l1_data_gas_price = cende_block_info.gas_prices.l1_data_gas_price_per_token();
        let l2_gas_price = cende_block_info.gas_prices.l2_gas_price_per_token();
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

**File:** crates/blockifier/src/execution/native/syscall_handler.rs (L220-232)
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
    }
```

**File:** crates/blockifier/src/execution/syscalls/hint_processor.rs (L388-396)
```rust
        let block_data = vec![
            Felt::from(block_info.block_number.0),
            Felt::from(block_info.block_timestamp.0),
            Felt::from(block_info.sequencer_address),
        ];
        let (block_info_segment_start_ptr, _) = self.allocate_data_segment(vm, &block_data)?;

        Ok(block_info_segment_start_ptr)
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
