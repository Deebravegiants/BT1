I now have enough information to write the finding. The key chain is:

1. `ProposalInit.builder` is set by the proposer from their own config with no constraint
2. `is_proposal_init_valid` never checks `builder`
3. `convert_to_sn_api_block_info` maps `init.builder` → `sequencer_address` in `BlockInfo`
4. `PartialBlockHashComponents::new` maps `block_info.sequencer_address` → `sequencer` field committed into the block hash
5. The `get_sequencer_address` syscall returns this value to executing contracts

---

### Title
Unvalidated `ProposalInit.builder` Lets Any Proposer Commit an Arbitrary Sequencer Address into the Block Hash and Execution Context — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs` / `crates/apollo_consensus_orchestrator/src/utils.rs`)

### Summary

`ProposalInit.builder` is a proposer-supplied field that is never checked by `is_proposal_init_valid`. It flows directly into `sequencer_address` inside `BlockInfo`, which is then committed into the `PartialBlockHashComponents` (and therefore the final block hash) and exposed to every executing contract via the `get_sequencer_address` syscall. Any consensus proposer can set `builder` to an arbitrary address; validators accept it without any independent reference check, producing a wrong block hash and wrong execution results for all contracts that read the sequencer address.

### Finding Description

`ProposalInit` carries a `builder` field ("Address of the one who builds/sequences the block"). [1](#0-0) 

During proposal validation, `is_proposal_init_valid` checks `height`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices (within a margin), `starknet_version`, `version_constant_commitment`, `timestamp`, and `fee_proposal_fri`. It does **not** check `builder`. [2](#0-1) 

`ProposalInitValidation` — the struct that carries the validator's locally-derived reference values — has no `builder` field at all, so there is no reference value to compare against. [3](#0-2) 

After `is_proposal_init_valid` passes, `initiate_validation` calls `convert_to_sn_api_block_info(&init)`, which maps `init.builder` directly to `sequencer_address`: [4](#0-3) 

This `BlockInfo` (with the proposer-supplied `sequencer_address`) is passed to the batcher's `validate_block`. The batcher executes all transactions under this block context, so every `get_sequencer_address` syscall returns the proposer-controlled value. After execution, `PartialBlockHashComponents::new` commits `block_info.sequencer_address` into the partial block hash: [5](#0-4) 

`calculate_block_hash` then chains the sequencer address into the Poseidon hash that becomes the canonical block hash: [6](#0-5) 

Because both the proposer and the validator derive `sequencer_address` from the same `ProposalInit.builder`, the `ProposalCommitment` comparison at the end of `validate_proposal` passes — the mismatch is never detected: [7](#0-6) 

The proposer sets `builder` from its own static config with no protocol-level constraint: [8](#0-7) 

### Impact Explanation

A malicious or misconfigured proposer sets `ProposalInit.builder` to an arbitrary address `X`. All validators accept the proposal (the field is never checked). The batcher executes every transaction in the block with `sequencer_address = X`. Consequences:

- **Wrong block hash committed**: The canonical block hash includes `X` as the sequencer address. Every downstream consumer (L1 anchoring, proof verification, state sync) sees a block hash derived from a forged sequencer address.
- **Wrong execution results**: Every contract that calls `get_sequencer_address` during this block receives `X` instead of the legitimate sequencer address. Fee-routing logic, access-control checks, and any contract that gates behavior on the sequencer address produce incorrect results that are permanently committed to state.
- **Wrong receipt/event commitments**: Execution outputs that depend on the sequencer address are hashed into `transaction_commitment`, `event_commitment`, and `receipt_commitment`, all of which are wrong.

This matches the allowed impact: *Wrong state, receipt, event, L1 message, class hash, storage value, or revert result from blockifier/syscall/execution logic for accepted input* and *Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact* (if fee routing depends on sequencer address).

### Likelihood Explanation

The trigger requires being the elected proposer for a round, which is a normal role in the BFT protocol — not a privileged external operation. No special capability beyond being a consensus participant is needed. The field is wire-level (protobuf), so it can be set to any 252-bit felt value. There is no existing guard: `ProposalInitValidation` has no `builder` slot, and no test exercises a mismatched `builder`.

### Recommendation

Add `builder` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid`. The validator's reference value should be derived from a locally-configured or committee-agreed sequencer address, not from the proposer's message. Concretely:

1. Add `expected_builder: ContractAddress` to `ProposalInitValidation`.
2. In `is_proposal_init_valid`, reject any `init` where `init.builder != proposal_init_validation.expected_builder`.
3. Populate `expected_builder` from the same source used by the proposer (`static_config.builder_address`) so that honest nodes agree, while a malicious proposer cannot substitute a different address.

### Proof of Concept

```
1. Attacker controls a consensus node that wins a proposer slot for height H.
2. In `initiate_build`, attacker sets `builder_address` in their static config to
   ContractAddress(0xdeadbeef) instead of the legitimate sequencer address.
3. The resulting ProposalInit is broadcast with builder = 0xdeadbeef.
4. Each validator calls is_proposal_init_valid — no check on `builder` exists.
5. Each validator calls convert_to_sn_api_block_info, producing
   BlockInfo { sequencer_address: 0xdeadbeef, ... }.
6. The batcher executes all transactions; get_sequencer_address syscalls return 0xdeadbeef.
7. PartialBlockHashComponents::new commits 0xdeadbeef as the sequencer field.
8. calculate_block_hash produces a hash H' that encodes 0xdeadbeef.
9. Both proposer and validator compute the same ProposalCommitment (both used the same
   builder from ProposalInit), so the ProposalFinMismatch check passes.
10. Consensus reaches decision on H' — a block hash with a forged sequencer address,
    wrong execution results, and wrong receipt/event commitments, all permanently committed.
```

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L106-107)
```rust
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L243-247)
```rust
    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
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

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-333)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L224-235)
```rust
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-259)
```rust
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L806-808)
```rust
            // TODO(Asmaa): Get it from committee once we have it.
            builder_address: self.config.static_config.builder_address,
            cancel_token,
```
