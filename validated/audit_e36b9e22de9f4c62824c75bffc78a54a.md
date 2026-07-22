### Title
Unvalidated `ProposalInit.builder` Field Allows Malicious Proposer to Commit Arbitrary Sequencer Address, Misdirecting Fees and Corrupting Block Header State — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`ProposalInit` carries a `builder` field (the sequencer/fee-recipient address). The validator's `is_proposal_init_valid` function checks many `ProposalInit` fields but **never validates `builder`**. A malicious proposer can set `builder` to any arbitrary address. All validators accept the proposal without checking this field, execute the block with the wrong `sequencer_address`, and reach consensus on a block whose header permanently records the wrong sequencer address. Transaction fees are misdirected to the attacker-controlled address, and the committed block state is wrong.

---

### Finding Description

`ProposalInit` contains two address fields with distinct roles:

- `proposer` — the consensus identity of the block proposer; validated against the committee in `manager.rs::handle_proposal` before the proposal reaches the context.
- `builder` — "Address of the one who builds/sequences the block"; used as `sequencer_address` in block execution and stored in the committed block header. [1](#0-0) 

The `builder` field flows into two critical paths:

**Path 1 — Block execution:**
`convert_to_sn_api_block_info` maps `init.builder` directly to `sequencer_address` in the `BlockInfo` passed to the batcher: [2](#0-1) 

This `BlockInfo` is passed to `batcher.validate_block` via `initiate_validation`: [3](#0-2) 

**Path 2 — Block header commitment:**
`update_state_sync_with_new_block` stores `init.builder` as the `sequencer` in the committed block header: [4](#0-3) 

**The missing validation:**
`is_proposal_init_valid` validates `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, timestamp bounds, L1 gas prices (within margin), and `fee_proposal_fri` bounds — but **`builder` is absent from every check**: [5](#0-4) 

**Why `ProposalFinMismatch` does not catch this:**
The `ProposalCommitment` is `proposal_commitment_from(partial_block_hash, fee_proposal_fri)`. The `partial_block_hash` is produced by the batcher executing the block with the proposer-supplied `builder`. Since both the proposer and all validators use the same `builder` value from the received `ProposalInit`, they all execute with the same wrong `sequencer_address` and produce the same `partial_block_hash`. The fin-mismatch check at line 244 passes: [6](#0-5) 

The legitimate proposer sets `builder` from its configured `builder_address`: [7](#0-6) 

But no validator enforces that the received `builder` matches any expected value.

---

### Impact Explanation

**Critical — Wrong state and incorrect fee accounting with economic impact.**

1. **Wrong sequencer address in committed block header**: `builder` is stored as `sequencer` in `BlockHeaderWithoutHash`, which is part of the block hash commitment. The committed state permanently records the wrong sequencer address.

2. **Transaction fees misdirected**: The `sequencer_address` in `BlockInfo` is the address to which transaction fees are paid during execution. Setting `builder` to an attacker-controlled address redirects all transaction fees for that block to the attacker.

3. **Consensus-confirmed**: Because all validators accept the wrong `builder` and execute identically, the `ProposalCommitment` matches on all sides. The wrong state is consensus-confirmed and irreversible.

---

### Likelihood Explanation

**Medium.** The attack requires the adversary to be the legitimate proposer for a given round (a privileged but rotating role in Tendermint-style consensus). In a Byzantine fault-tolerant validator set of size N, any of the up to ⌊(N−1)/3⌋ malicious validators can exploit this when scheduled as proposer. The attack is trivially executable — it requires only setting one field in the outgoing `ProposalInit` — and produces immediate, irreversible economic and state impact.

---

### Recommendation

Add `builder` to the fields validated in `is_proposal_init_valid`. The expected value should be derived from a consensus-agreed source (e.g., the staking/sequencer registry contract, or the node's own configured `builder_address` for the proposer path). At minimum, validators should reject proposals where `builder` is the zero address or does not match the expected sequencer address for the current height.

```rust
// In is_proposal_init_valid, add:
if init_proposed.builder != expected_builder_address {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!("builder mismatch: expected={:?}, proposed={:?}",
            expected_builder_address, init_proposed.builder),
    ));
}
```

`ProposalInitValidation` should carry the expected `builder` address, populated from the node's configuration or a staking contract lookup, mirroring how `l2_gas_price_fri` and `l1_da_mode` are carried.

---

### Proof of Concept

1. Malicious validator `M` is the scheduled proposer for height `H`, round `R`.
2. `M` constructs `ProposalInit` with `builder = attacker_address` (any address `M` controls).
3. `M` sends the proposal stream to all validators.
4. Each validator calls `is_proposal_init_valid` — `builder` is not checked; the proposal passes all validation.
5. Each validator calls `initiate_validation` → `convert_to_sn_api_block_info(init)` → `sequencer_address = attacker_address` → `batcher.validate_block(ValidateBlockInput { block_info: ... })`.
6. The batcher executes the block with `sequencer_address = attacker_address`; all transaction fees are credited to `attacker_address`.
7. Both `M` and all validators compute `partial_block_hash` from the same execution (same wrong `builder`), producing identical `ProposalCommitment`.
8. `built_block == received_fin.proposal_commitment` — `ProposalFinMismatch` check passes.
9. Consensus is reached; `decision_reached` is called.
10. `update_state_sync_with_new_block` stores `sequencer = SequencerContractAddress(attacker_address)` in the committed block header.
11. The block is finalized with the wrong sequencer address; fees are permanently misdirected.

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L103-107)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-418)
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L397-409)
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
