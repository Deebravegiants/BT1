### Title
Unvalidated `builder` Field in `ProposalInit` Allows Malicious Proposer to Redirect All Block Fees and Corrupt Execution State — (`File: crates/apollo_consensus_orchestrator/src/utils.rs`)

### Summary

The `builder` field of `ProposalInit` is transmitted over the network by the proposer and is directly used as the `sequencer_address` in `BlockInfo` for all transaction execution in a block. It is never validated by `is_proposal_init_valid` against any locally-trusted reference. A malicious proposer can set `builder` to an arbitrary contract address, causing all fee transfers in the block to be credited to an attacker-controlled address, corrupting the state diff, and causing every `get_execution_info` syscall to return a wrong `sequencer_address`.

### Finding Description

`ProposalInit` carries a `builder` field defined as "Address of the one who builds/sequences the block": [1](#0-0) 

When the proposer builds a block, `builder` is set from local config (`args.builder_address`): [2](#0-1) 

When a validator receives the proposal, `convert_to_sn_api_block_info` maps `init.builder` directly to `sequencer_address` in the `BlockInfo` passed to the batcher: [3](#0-2) 

The `is_proposal_init_valid` function validates timestamp, `starknet_version`, `version_constant_commitment`, `height`, `l1_da_mode`, `l2_gas_price_fri`, L1 gas prices, and `fee_proposal_fri`. It does **not** validate `builder` against any locally-trusted reference: [4](#0-3) 

`ProposalInitValidation` — the struct that carries all locally-derived reference values — has no `builder` field: [5](#0-4) 

The consensus manager does check that `init.proposer` matches the committee-elected proposer: [6](#0-5) 

But `builder` is a separate field and is never subject to any such check.

### Impact Explanation

`sequencer_address` in `BlockInfo` is the address that receives all transaction fees. In the blockifier's fee transfer logic, fees are credited to `block_context.block_info.sequencer_address`: [7](#0-6) 

By setting `builder` to an attacker-controlled address, a malicious proposer causes:

1. **All fee transfers in the block go to the attacker's address** — the state diff records fee token balance increases at the wrong address, permanently corrupting on-chain balances.
2. **`get_execution_info` syscall returns wrong `sequencer_address`** — every contract that reads `block_info.sequencer_address` (e.g., to detect sequencer-is-sender and skip fee checks) sees the attacker's address instead of the legitimate sequencer.
3. **Wrong block header committed** — `sequencer_address` is part of the block header used in block hash computation (visible in `echonet/echo_center.py` line 683), so the committed block hash is computed over a forged sequencer address.

These map to: **Critical — Wrong state, receipt, storage value from blockifier/syscall/execution logic** and **Critical — Incorrect fee/balance with economic impact**.

### Likelihood Explanation

In Tendermint BFT, the proposer role rotates among all validators. Any validator that becomes the proposer for a round can exploit this. No external attacker capability is required — only the ability to be elected proposer, which is a normal part of the protocol. The attack is silent: the proposal passes all existing validation checks and is accepted by all honest validators.

### Recommendation

Add `builder` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid`. The locally-trusted reference value should come from the node's own configuration (the same `builder_address` used in `initiate_build`). The check should be:

```rust
if init_proposed.builder != proposal_init_validation.expected_builder {
    return Err(ValidateProposalError::InvalidProposalInit(...));
}
```

This mirrors the existing pattern for `l2_gas_price_fri`, `l1_da_mode`, and `height` — all of which are locally-derived and enforced against the proposer-supplied value.

### Proof of Concept

1. A validator node is elected proposer for height H, round R.
2. Instead of using its configured `builder_address`, it sets `init.builder = ATTACKER_ADDRESS` in `initiate_build` (or patches the wire message).
3. The `ProposalInit` is broadcast to all peers.
4. Each peer's `handle_proposal` in `manager.rs` checks `init.proposer` against the committee — this passes because `proposer` is correct.
5. Each peer calls `validate_proposal` → `is_proposal_init_valid` — this passes because `builder` is not checked.
6. `initiate_validation` calls `convert_to_sn_api_block_info(init)`, which sets `sequencer_address = ATTACKER_ADDRESS`.
7. The batcher executes all transactions with `sequencer_address = ATTACKER_ADDRESS`. All fee transfers credit `ATTACKER_ADDRESS`.
8. `validate_proposal` returns `Ok(commitment)`. Consensus reaches decision. `decision_reached` commits the block.
9. The committed state diff contains fee token balance increases at `ATTACKER_ADDRESS` instead of the legitimate sequencer. All `get_execution_info` calls during that block returned `ATTACKER_ADDRESS` as the sequencer. [8](#0-7) [9](#0-8)

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L106-108)
```rust
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
    /// L1 data availability mode.
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L173-174)
```rust
        proposer: args.build_param.proposer,
        builder: args.builder_address,
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-419)
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
        l1_gas_price_provider,
        init_proposed.timestamp,
        proposal_init_validation.previous_proposal_init.as_ref(),
        gas_price_params,
    )
    .await;
    let l1_gas_price_margin_percent =
        VersionedConstants::latest_constants().l1_gas_price_margin_percent.into();
    debug!("L1 price info: fri={l1_gas_prices_fri:?}, wei={l1_gas_prices_wei:?}");

    let l1_gas_price_fri = l1_gas_prices_fri.l1_gas_price;
    let l1_data_gas_price_fri = l1_gas_prices_fri.l1_data_gas_price;
    let l1_gas_price_wei = l1_gas_prices_wei.l1_gas_price;
    let l1_data_gas_price_wei = l1_gas_prices_wei.l1_data_gas_price;
    let l1_gas_price_fri_proposed = init_proposed.l1_gas_price_fri;
    let l1_data_gas_price_fri_proposed = init_proposed.l1_data_gas_price_fri;
    let l1_gas_price_wei_proposed = init_proposed.l1_gas_price_wei;
    let l1_data_gas_price_wei_proposed = init_proposed.l1_data_gas_price_wei;

    if !(within_margin(l1_gas_price_fri_proposed, l1_gas_price_fri, l1_gas_price_margin_percent)
        && within_margin(
            l1_data_gas_price_fri_proposed,
            l1_data_gas_price_fri,
            l1_gas_price_margin_percent,
        )
        && within_margin(l1_gas_price_wei_proposed, l1_gas_price_wei, l1_gas_price_margin_percent)
        && within_margin(
            l1_data_gas_price_wei_proposed,
            l1_data_gas_price_wei,
            l1_gas_price_margin_percent,
        ))
    {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "L1 gas price mismatch: expected L1 gas price FRI={l1_gas_price_fri}, \
                 proposed={l1_gas_price_fri_proposed}, expected L1 data gas price \
                 FRI={l1_data_gas_price_fri}, proposed={l1_data_gas_price_fri_proposed}, expected \
                 L1 gas price WEI={l1_gas_price_wei}, proposed={l1_gas_price_wei_proposed}, \
                 expected L1 data gas price WEI={l1_data_gas_price_wei}, \
                 proposed={l1_data_gas_price_wei_proposed}, \
                 l1_gas_price_margin_percent={l1_gas_price_margin_percent}"
            ),
        ));
    }

    // fee_proposal is required iff Starknet version >= V0_14_3.
    let fee_proposal_required = init_proposed.starknet_version >= StarknetVersion::V0_14_3;
    match (init_proposed.fee_proposal_fri, fee_proposal_required) {
        (Some(_), false) => {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "fee_proposal must be absent before V0_14_3, got Some at version {}",
                    init_proposed.starknet_version
                ),
            ));
        }
        (None, true) => {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "fee_proposal is required at V0_14_3+, got None at version {}",
                    init_proposed.starknet_version
                ),
            ));
        }
        _ => {}
    }

    // Validate fee_proposal is within the configured margin of fee_actual.
    // During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
    if let (Some(fee_actual), Some(fee_proposal)) =
        (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
    {
        let (lower_bound, upper_bound) = fee_proposal_bounds(
            fee_actual,
            VersionedConstants::latest_constants().fee_proposal_margin_ppt,
        );
        if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "Fee proposal out of bounds: fee_actual={}, fee_proposal={}, allowed \
                     range=[{lower_bound}, {upper_bound}]",
                    fee_actual.0, fee_proposal.0
                ),
            ));
        }
    }

    Ok(())
}
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

**File:** crates/blockifier/src/concurrency/fee_utils.rs (L40-62)
```rust
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
