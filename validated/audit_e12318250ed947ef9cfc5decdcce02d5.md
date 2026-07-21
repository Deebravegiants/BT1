### Title
Unvalidated `ProposalInit.builder` Field Allows Proposer to Inject Arbitrary `sequencer_address` into Block Execution and Block Hash — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`, `crates/apollo_consensus_orchestrator/src/utils.rs`)

---

### Summary

`ProposalInit` carries a `builder` field (the address of the block-builder/sequencer). Validators check every other security-sensitive field in `is_proposal_init_valid` — height, L1/L2 gas prices, DA mode, Starknet version, timestamp, `fee_proposal_fri` — but never check `builder`. Because `convert_to_sn_api_block_info` maps `init.builder` directly to `block_info.sequencer_address`, the proposer can inject any arbitrary address as the sequencer address for the block. That address flows into transaction execution (visible to contracts via `get_block_info()`), into `PartialBlockHashComponents`, and ultimately into the committed block hash. Validators re-derive the same hash from the proposer-supplied value, so the `ProposalFin` comparison passes silently.

---

### Finding Description

**`ProposalInit.builder` is never validated by the validator path.**

`ProposalInit` has two identity fields:

```rust
pub proposer: ContractAddress,   // who proposed in consensus
pub builder: ContractAddress,    // who built/sequenced the block
``` [1](#0-0) 

`proposer` is checked against the committee-derived expected proposer in `handle_proposal`: [2](#0-1) 

`builder` is **never checked** anywhere in `is_proposal_init_valid`. The function validates `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, timestamp bounds, all four L1 gas price fields, and `fee_proposal_fri`, but `builder` is absent from every check: [3](#0-2) 

`convert_to_sn_api_block_info` then maps `init.builder` directly to `sequencer_address`:

```rust
sequencer_address: init.builder,
``` [4](#0-3) 

This `BlockInfo` is passed to the batcher via `ValidateBlockInput` in `initiate_validation`: [5](#0-4) 

The batcher executes all transactions in the block using this `BlockInfo`. Every contract that calls `get_block_info()` during execution sees the attacker-controlled `sequencer_address`. The same `block_info` is used to build `PartialBlockHashComponents`:

```rust
sequencer: SequencerContractAddress(block_info.sequencer_address),
``` [6](#0-5) 

`sequencer_address` is then chained into the block hash: [7](#0-6) 

Because validators derive `PartialBlockHash` from the same proposer-supplied `builder`, the `ProposalFin` comparison at line 244 passes: [8](#0-7) 

The block is committed with the attacker-chosen `sequencer_address` baked into both execution state and the block hash.

---

### Impact Explanation

**Critical — Wrong state/execution result from blockifier/syscall logic for accepted input.**

1. **Contract execution state corruption**: Any contract that branches on `get_block_info().sequencer_address` (e.g., fee-routing contracts, access-control guards, sequencer-tip logic) will execute against the attacker-supplied address. State changes produced by those branches are permanently committed.

2. **Block hash carries wrong sequencer address**: `sequencer_address` is a first-class input to `calculate_block_hash`. The committed block hash encodes the attacker-chosen value. L1 verifiers and external observers that independently recompute the block hash using the on-chain sequencer address will see a mismatch.

3. **Undetectable by current validation**: Validators re-derive `PartialBlockHash` from the same `init.builder` they received, so the `ProposalFin` comparison always passes regardless of what `builder` contains.

---

### Likelihood Explanation

**Medium.** The attack requires the adversary to be the designated proposer for a given height/round, which is a role assigned by the committee rotation. In a decentralized sequencer with multiple validators, any validator will eventually be the proposer. The manipulation requires only setting one field in `ProposalInit` to an arbitrary value — no cryptographic forgery, no race condition, no external dependency.

---

### Recommendation

Add a check in `is_proposal_init_valid` that enforces `init.builder` equals the expected value. The simplest invariant is `init.builder == init.proposer` (the proposer builds its own block). If proposer-builder separation is intended, the expected `builder` address must be included in `ProposalInitValidation` and checked:

```rust
if init_proposed.builder != proposal_init_validation.expected_builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.expected_builder,
            init_proposed.builder
        ),
    ));
}
``` [9](#0-8) 

---

### Proof of Concept

1. Node A is the designated proposer for height H, round 0.
2. Node A constructs `ProposalInit` with `builder = ContractAddress::from(0xdeadbeef)` (an attacker-controlled address) instead of its own configured `builder_address`.
3. Node A broadcasts the proposal. `handle_proposal` in the consensus manager checks `proposer == expected_proposer` — this passes because `proposer` is correct.
4. `validate_proposal` calls `is_proposal_init_valid`. None of the checks inspect `builder`. The function returns `Ok(())`.
5. `initiate_validation` calls `convert_to_sn_api_block_info(init)`, producing `BlockInfo { sequencer_address: 0xdeadbeef, ... }`.
6. The batcher executes all transactions with `sequencer_address = 0xdeadbeef`. Any contract calling `get_block_info()` sees `0xdeadbeef`.
7. `PartialBlockHashComponents::new(&block_info, ...)` stores `sequencer = 0xdeadbeef`.
8. `PartialBlockHash::from_partial_block_hash_components` hashes `0xdeadbeef` into the commitment.
9. The proposer sends `ProposalFin` with the commitment derived from `0xdeadbeef`. Validators compute the same commitment (they used the same `builder`). The `ProposalFin` comparison passes.
10. The block is committed. The block header records `sequencer = 0xdeadbeef`, and all execution state changes driven by that address are permanent.

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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L443-475)
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
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-347)
```rust
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-281)
```rust
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
            .chain(&block_commitments.concatenated_counts)
            .chain(&block_commitments.state_diff_commitment.0.0)
            .chain(&block_commitments.transaction_commitment.0)
            .chain(&block_commitments.event_commitment.0)
            .chain(&block_commitments.receipt_commitment.0)
            .chain_iter(
                gas_prices_to_hash(
                    &partial_block_hash_components.l1_gas_price,
                    &partial_block_hash_components.l1_data_gas_price,
                    &partial_block_hash_components.l2_gas_price,
                    &block_hash_version,
                )
                .iter(),
            )
            .chain(
                &Felt::try_from(&partial_block_hash_components.starknet_version)
                    .expect("Expect ASCII version"),
            )
            .chain(&Felt::ZERO)
            .chain(&previous_block_hash.0)
            .get_poseidon_hash(),
    ))
```
