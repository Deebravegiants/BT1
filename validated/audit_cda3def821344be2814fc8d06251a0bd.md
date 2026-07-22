### Title
Unvalidated `ProposalInit.builder` Used as `sequencer_address` Allows Malicious Proposer to Redirect Fees and Corrupt Execution Context - (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` validates many fields of a received `ProposalInit` (height, L1/L2 gas prices, timestamp, starknet version, version constant commitment, L1 DA mode) but never validates `init.builder`. The `builder` field is proposer-supplied and is passed over the wire without any local cross-check. `convert_to_sn_api_block_info` then maps `init.builder` directly to `sequencer_address` in the `BlockInfo` that drives every transaction execution in the block. A malicious proposer can set `builder` to any arbitrary address, causing all fee transfers to be directed to that address and causing the `get_sequencer_address` syscall to return a wrong value for every transaction in the block.

---

### Finding Description

`ProposalInit` carries two distinct address fields:

- `proposer`: the consensus identity of the block proposer (validated against the committee in `handle_proposal`)
- `builder`: the address that builds/sequences the block, used as `sequencer_address` during execution [1](#0-0) 

When a validator receives a proposal, `is_proposal_init_valid` is called. It checks `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, all four L1 gas prices, `timestamp`, and `fee_proposal_fri`. It does **not** check `init.builder` against any locally-known expected value: [2](#0-1) 

After validation passes, `convert_to_sn_api_block_info` maps the unvalidated `init.builder` directly to `sequencer_address`: [3](#0-2) 

This `BlockInfo` is then passed to the batcher for both proposal building and validation: [4](#0-3) 

The same `init.builder` is also written into the committed block header as `sequencer`: [5](#0-4) 

The proposer sets `builder` from its own static config with a TODO noting it is not yet sourced from the committee: [6](#0-5) 

---

### Impact Explanation

**Critical — Incorrect fee/balance effect with economic impact.**

The `sequencer_address` in `BlockInfo` is the address that receives transaction fees during blockifier execution. By setting `builder` to an attacker-controlled address, a malicious proposer redirects all fee payments for every transaction in the block to that address. Legitimate sequencer revenue is stolen.

**Critical — Wrong syscall result from blockifier execution logic.**

The `get_sequencer_address` syscall returns `block_info.sequencer_address`. Any contract that queries this (e.g., for access control, fee-related logic, or protocol-level checks) receives the attacker-supplied address instead of the legitimate sequencer address, producing wrong execution results, wrong events, and wrong receipts that are committed to the chain.

**Wrong block header commitment.**

The `sequencer` field in `BlockHeaderWithoutHash` is derived from `init.builder`, so the committed block header carries the wrong sequencer address, corrupting the authoritative on-chain record.

---

### Likelihood Explanation

Any consensus participant that is legitimately selected as proposer for a round can exploit this. No special privilege beyond being the current-round proposer is required. The attacker simply sets `builder` to any address in their `ProposalInit` before broadcasting. All validators will accept the proposal because `is_proposal_init_valid` does not check this field.

---

### Recommendation

Add a check inside `is_proposal_init_valid` (or as a pre-check before calling it) that rejects any `ProposalInit` where `init.builder` does not match the locally-configured or committee-derived expected builder address. Until the committee-based builder address is available (per the existing TODO), the validator should at minimum enforce that `init.builder` equals the locally-configured `builder_address` from its own static config, since all honest nodes in the current single-sequencer deployment share the same expected value.

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

`ProposalInitValidation` should be extended with an `expected_builder: ContractAddress` field populated from the node's static config.

---

### Proof of Concept

1. Attacker node is selected as proposer for height H, round R.
2. Attacker constructs `ProposalInit` with all valid fields (height, gas prices, timestamp, etc.) but sets `builder = attacker_fee_collection_address`.
3. Attacker broadcasts the proposal stream.
4. Each validator calls `is_proposal_init_valid` — all checks pass because `builder` is never checked.
5. `initiate_validation` calls `convert_to_sn_api_block_info(&init)`, producing a `BlockInfo` with `sequencer_address = attacker_fee_collection_address`.
6. The batcher executes all transactions in the block with this `BlockInfo`. Every fee transfer goes to `attacker_fee_collection_address`.
7. Every `get_sequencer_address` syscall in the block returns `attacker_fee_collection_address`.
8. The block is committed with `sequencer = attacker_fee_collection_address` in the block header.
9. The attacker has stolen all transaction fees for block H and corrupted the sequencer address visible to all contracts executed in that block. [7](#0-6) [8](#0-7)

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L397-406)
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
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L806-808)
```rust
            // TODO(Asmaa): Get it from committee once we have it.
            builder_address: self.config.static_config.builder_address,
            cancel_token,
```
