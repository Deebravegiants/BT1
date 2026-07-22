### Title
Validator Accepts Arbitrary `ProposalInit.builder` Without Verification, Enabling Proposer to Redirect Transaction Fees — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

The `is_proposal_init_valid` function validates many fields of a received `ProposalInit` (height, `l1_da_mode`, `l2_gas_price_fri`, timestamp, `starknet_version`, `version_constant_commitment`, all four L1 gas prices, and `fee_proposal_fri`), but it never checks the `builder` field. The `builder` address is passed directly into block execution as the sequencer/fee-recipient address. A malicious proposer can set `builder` to any arbitrary address; validators will accept the proposal, execute the block with the attacker-controlled sequencer address, and commit a block that directs all transaction fees to the attacker.

---

### Finding Description

`ProposalInit` carries a `builder` field described as "Address of the one who builds/sequences the block." [1](#0-0) 

On the proposer side, `builder` is populated from `self.config.static_config.builder_address`, with a TODO acknowledging it should eventually come from the committee: [2](#0-1) 

The proposer embeds this value into `ProposalInit` and sends it over the network: [3](#0-2) 

On the validator side, `is_proposal_init_valid` checks height, `l1_da_mode`, `l2_gas_price_fri`, timestamp, `starknet_version`, `version_constant_commitment`, all four L1 gas prices, and `fee_proposal_fri` — but **never checks `builder`**: [4](#0-3) 

The unchecked `init` (including its `builder` field) is then forwarded to `initiate_validation`, which calls `convert_to_sn_api_block_info(init)` to construct the `BlockInfo` passed to the batcher/blockifier for execution: [5](#0-4) 

Because both the proposer and the validator execute the block using the same `builder` value from `ProposalInit`, both sides compute the same `PartialBlockHash` and the same `ProposalCommitment`. The final commitment check: [6](#0-5) 

passes without detecting the tampered `builder`. The block is committed with the attacker-controlled sequencer address.

---

### Impact Explanation

The `builder` address maps to the sequencer address in the block context. In Starknet, the sequencer address is the fee recipient for all transactions in the block. A malicious proposer can set `builder` to any address — including their own wallet or a contract they control — and redirect all transaction fees from the legitimate builder to themselves. Every validator in the network will execute the block with the attacker-supplied sequencer address and vote to commit it, because the `ProposalCommitment` is consistent (both sides used the same `builder`). The on-chain state will reflect the wrong fee recipient.

This matches the allowed impact: **"Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact."**

---

### Likelihood Explanation

Any committee member who wins the proposer slot for a round can trigger this. No special privilege beyond being the elected proposer is required. The attack is silent — it produces no validation error, no log warning, and no commitment mismatch. It can be repeated every round the attacker is proposer.

---

### Recommendation

Add a `builder` field to `ProposalInitValidation` (populated from the committee or from local config, mirroring how `l2_gas_price_fri` is validated), and enforce equality in `is_proposal_init_valid`:

```rust
// In is_proposal_init_valid:
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

The `expected_builder` should be derived from the committee (resolving the existing TODO) or, until then, from the validator's own `static_config.builder_address`. [7](#0-6) 

---

### Proof of Concept

1. Attacker is elected proposer for height H, round R.
2. Attacker constructs `ProposalInit` with `builder = attacker_wallet_address` (any address).
3. Attacker calls `build_proposal` normally; the batcher executes the block with `builder = attacker_wallet_address` and returns `PartialBlockHash`.
4. `proposal_commitment_from(partial, fee_proposal_fri)` produces commitment `C`.
5. Attacker streams `ProposalPart::Init(init)`, transaction batches, and `ProposalPart::Fin { proposal_commitment: C, ... }`.
6. Each validator calls `is_proposal_init_valid` — no check on `builder` — and then `initiate_validation` with `convert_to_sn_api_block_info(init)`, executing the block with `builder = attacker_wallet_address`.
7. Validators compute the same `C`; `built_block == received_fin.proposal_commitment` passes.
8. `decision_reached` commits the block. All transaction fees for height H are credited to `attacker_wallet_address`. [8](#0-7) [9](#0-8)

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L106-108)
```rust
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
    /// L1 data availability mode.
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L806-808)
```rust
            // TODO(Asmaa): Get it from committee once we have it.
            builder_address: self.config.static_config.builder_address,
            cancel_token,
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L73-85)
```rust
// Contains parameters required for validating ProposalInit.
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L396-419)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L443-476)
```rust
async fn initiate_validation(
    batcher: Arc<dyn BatcherClient>,
    state_sync_client: SharedStateSyncClient,
    init: &ProposalInit,
    proposal_id: ProposalId,
    timeout_plus_margin: Duration,
    clock: &dyn Clock,
    compare_retrospective_block_hash: bool,
) -> ValidateProposalResult<()> {
    let chrono_timeout = chrono::Duration::from_std(timeout_plus_margin)
        .expect("Can't convert timeout to chrono::Duration");

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
}
```
