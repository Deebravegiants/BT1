### Title
Unvalidated Zero `builder` Address in `ProposalInit` Causes All Block Fees to Be Burned — (`File: crates/apollo_consensus_orchestrator/src/utils.rs`)

### Summary

`ProposalInit.builder` is mapped directly to `BlockInfo.sequencer_address` — the address that receives every transaction fee in a block — without any zero-address check in either the proposer path or the validator path. The production config schema ships with `builder_address = "0x0"` as its default value. Any operator who does not explicitly override this field will propose blocks that route all fees to the zero address, and every validator node will accept those proposals because `is_proposal_init_valid` never inspects the `builder` field.

### Finding Description

`convert_to_sn_api_block_info` converts a `ProposalInit` into the `starknet_api::block::BlockInfo` that the batcher uses for every transaction in the block:

```rust
// crates/apollo_consensus_orchestrator/src/utils.rs  line 332
sequencer_address: init.builder,
``` [1](#0-0) 

`sequencer_address` is the fee-recipient address. Every fee transfer executed by the blockifier credits this address. The function validates that all five gas prices are non-zero (via `NonzeroGasPrice::new`), but performs no equivalent check on `init.builder`. [2](#0-1) 

The validator's `is_proposal_init_valid` checks timestamp, `starknet_version`, `version_constant_commitment`, `height`, `l1_da_mode`, `l2_gas_price_fri`, L1 gas prices, and `fee_proposal_fri`. It never checks `init.builder`: [3](#0-2) 

The proposer populates `init.builder` from `args.builder_address`, which comes from `ContextStaticConfig.builder_address`: [4](#0-3) 

The production config schema ships this field with a default of `"0x0"`: [5](#0-4) 

### Impact Explanation

`BlockInfo.sequencer_address` is the sole recipient of all fee transfers for every transaction in the block. When it is `ContractAddress(0x0)`, the blockifier's fee-transfer logic credits address zero: [6](#0-5) 

Fees are irretrievably lost. This matches: **Critical — Incorrect fee/balance effect with economic impact.**

### Likelihood Explanation

The default value of `builder_address` in the shipped `config_schema.json` is `"0x0"`. Any operator who deploys the node without explicitly setting this field will silently burn all sequencer fees. Validators accept such proposals without warning because `is_proposal_init_valid` does not inspect `init.builder`. The misconfiguration is invisible at startup and only manifests as missing revenue.

### Recommendation

1. **Proposer side**: In `initiate_build`, assert `args.builder_address != ContractAddress::default()` before constructing `ProposalInit`.
2. **Validator side**: Add a check in `is_proposal_init_valid` (or in `convert_to_sn_api_block_info`) that rejects any `init.builder == ContractAddress::default()`.
3. **Config**: Change the default value of `consensus_manager_config.context_config.static_config.builder_address` from `"0x0"` to a sentinel that forces explicit configuration, or add a startup validation that panics when the address is zero.

### Proof of Concept

1. Deploy a sequencer node without setting `builder_address` (use the default `"0x0"`).
2. The node proposes blocks with `ProposalInit { builder: ContractAddress(0x0), … }`.
3. Validator nodes call `is_proposal_init_valid` → all checks pass (builder is never inspected).
4. `initiate_validation` calls `convert_to_sn_api_block_info(&init)` → `BlockInfo { sequencer_address: ContractAddress(0x0), … }`.
5. The batcher executes every transaction with `sequencer_address = 0x0`; every fee transfer credits address zero.
6. All transaction fees in every block produced by this node are permanently burned.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L304-317)
```rust
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
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-333)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
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

**File:** crates/apollo_node/resources/config_schema.json (L2797-2801)
```json
  "consensus_manager_config.context_config.static_config.builder_address": {
    "description": "The address of the contract that builds the block.",
    "privacy": "Public",
    "value": "0x0"
  },
```

**File:** crates/blockifier/src/concurrency/fee_utils.rs (L39-62)
```rust
        let sequencer_balance = state
        .get_fee_token_balance(
            tx_context.block_context.block_info.sequencer_address,
            tx_context.fee_token_address()
        )
        // TODO(barak, 01/07/2024): Consider propagating the error.
        .unwrap_or_else(|error| {
            panic!(
                "Access to storage failed. Probably due to a bug in Papyrus. {error:?}: {error}"
            )
        });

        // Fix the transfer call info.
        fill_sequencer_balance_reads(fee_transfer_call_info, sequencer_balance);
        // Update the balance.
        add_fee_to_sequencer_balance(
            tx_context.fee_token_address(),
            state,
            tx_execution_info.receipt.fee,
            &tx_context.block_context,
            sequencer_balance,
            tx_context.tx_info.sender_address(),
            state_diff,
        );
```
