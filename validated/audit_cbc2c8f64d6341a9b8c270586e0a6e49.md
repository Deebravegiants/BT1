### Title
Unvalidated `ProposalInit.builder` Field Allows Proposer to Redirect All Block Fee Income to an Arbitrary Address — (`crates/apollo_consensus_orchestrator/src/utils.rs`, `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`ProposalInit.builder` is the self-reported address that becomes `sequencer_address` in the executed `BlockInfo`. Every transaction fee in the block is transferred to `sequencer_address`. `is_proposal_init_valid` validates timestamp, starknet version, version-constant commitment, height, L1-DA mode, L2 gas price, all four L1 gas prices, and `fee_proposal_fri` — but it never checks `builder`. A legitimate proposer can therefore set `builder` to any address and have all block fees credited there, with full consensus acceptance.

---

### Finding Description

**Step 1 — `builder` becomes `sequencer_address`.**

`convert_to_sn_api_block_info` maps `ProposalInit` to the `BlockInfo` that is handed to the batcher for both proposal building and validation:

```rust
// crates/apollo_consensus_orchestrator/src/utils.rs:329-332
Ok(starknet_api::block::BlockInfo {
    block_number: init.height,
    block_timestamp: BlockTimestamp(init.timestamp),
    sequencer_address: init.builder,   // ← builder is the fee recipient
    ...
})
``` [1](#0-0) 

**Step 2 — `builder` is never validated.**

`is_proposal_init_valid` exhaustively checks every other field of `ProposalInit` but contains no check on `builder`: [2](#0-1) 

The `ProposalInitValidation` struct that carries the validator's reference values also has no `builder` field: [3](#0-2) 

**Step 3 — `sequencer_address` is the fee recipient in every transaction.**

In `execute_fee_transfer`, the calldata recipient is `block_context.block_info.sequencer_address`:

```rust
// crates/blockifier/src/transaction/account_transaction.rs:571-573
calldata![
    *block_context.block_info.sequencer_address.0.key(), // Recipient.
    lsb_amount,
    msb_amount
],
``` [4](#0-3) 

The same address is used in `add_fee_to_sequencer_balance` (concurrency path) and in the Cairo OS `charge_fee` hint: [5](#0-4) [6](#0-5) 

**Step 4 — The proposer sets `builder` freely.**

In `initiate_build`, `builder` is taken directly from `args.builder_address`, a node-local config value. Nothing prevents a malicious proposer from configuring it to any address: [7](#0-6) 

**Step 5 — Validators accept the tampered `ProposalInit`.**

`validate_proposal` calls `is_proposal_init_valid` and then `initiate_validation`, which passes the full `init` (including the attacker-chosen `builder`) to the batcher as `block_info`: [8](#0-7) [9](#0-8) 

Because `builder` is absent from `ProposalInitValidation`, every validator independently re-derives the same wrong `sequencer_address` and produces the same `partial_block_hash`, so the `ProposalFin` commitment matches and consensus proceeds normally.

---

### Impact Explanation

Every account transaction in the block executes a fee-token `transfer(recipient=sequencer_address, amount=actual_fee)`. With `builder` pointing to an attacker-controlled address, the entire block's fee income is credited to that address in the state diff. The legitimate sequencer receives nothing. The committed state is wrong: fee-token storage slots for the attacker address are inflated, and those for the real sequencer are not updated. This is a **Critical** impact: incorrect fee/balance effect with direct economic impact, and wrong storage values in the committed state.

---

### Likelihood Explanation

The attacker must be the scheduled proposer for the target height/round, which is a normal, non-privileged role in the staking rotation. No external oracle manipulation, no mempool race, and no cryptographic break is required. The proposer simply sets `builder_address` in its node configuration to an arbitrary address before its turn. The attack is silent: the `ProposalFin` commitment is identical to what an honest proposer would produce (because `builder` does not enter the `partial_block_hash` computation), so no validator raises an alarm.

---

### Recommendation

Add `builder` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid`. The expected value should be derived from the same committee/staking source that supplies `proposer` — either they must be equal, or `builder` must match a pre-registered sequencer address for the epoch. Concretely:

1. Add `expected_builder: ContractAddress` to `ProposalInitValidation`.
2. In `is_proposal_init_valid`, reject any `init` where `init.builder != proposal_init_validation.expected_builder`.
3. Populate `expected_builder` in `validate_proposal` from the same source used to verify `proposer` in `handle_proposal` (`get_proposer_for_height`), or from a separate on-chain builder registry.

---

### Proof of Concept

1. Attacker controls a validator node that is the scheduled proposer for block N, round 0.
2. Attacker sets `builder_address` in `consensus_manager_config.json` to `0xDEAD` (attacker wallet).
3. Node calls `build_proposal` → `initiate_build` constructs `ProposalInit { builder: 0xDEAD, ... }` and broadcasts it.
4. Every peer calls `validate_proposal` → `is_proposal_init_valid` — passes (no `builder` check).
5. `initiate_validation` calls `convert_to_sn_api_block_info(init)` → `BlockInfo { sequencer_address: 0xDEAD, ... }` is handed to the batcher.
6. Batcher executes all transactions; each fee transfer sends tokens to `0xDEAD`.
7. `ProposalFin.proposal_commitment` matches on all validators (commitment does not cover `builder`).
8. Consensus reaches decision; block is committed with all fee income at `0xDEAD`.
9. Legitimate sequencer balance: unchanged. Attacker balance: increased by the sum of all fees in block N.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-332)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
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

**File:** crates/blockifier/src/transaction/account_transaction.rs (L571-574)
```rust
            calldata: calldata![
                *block_context.block_info.sequencer_address.0.key(), // Recipient.
                lsb_amount,
                msb_amount
```

**File:** crates/blockifier/src/concurrency/fee_utils.rs (L105-117)
```rust
pub fn add_fee_to_sequencer_balance(
    fee_token_address: ContractAddress,
    state: &mut impl UpdatableState,
    actual_fee: Fee,
    block_context: &BlockContext,
    sequencer_balance: (Felt, Felt),
    sender_address: ContractAddress,
    state_diff: &mut StateMaps,
) {
    assert_ne!(
        sender_address, block_context.block_info.sequencer_address,
        "The sender cannot be the sequencer."
    );
```

**File:** crates/apollo_starknet_os_program/src/cairo/starkware/starknet/core/os/execution/transaction_impls.cairo (L129-131)
```text
    local calldata: TransferCallData = TransferCallData(
        recipient=block_context.block_info_for_execute.sequencer_address,
        amount=Uint256(low=low_actual_fee, high=0),
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
