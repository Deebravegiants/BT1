Looking at the key data flows, I need to check the `builder` field validation path and how it flows into block hash and execution context.### Title
Unvalidated `builder` Field in `ProposalInit` Allows Any Legitimate Proposer to Spoof `sequencer_address` in Block Execution Context and Block Hash — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`ProposalInit.builder` is accepted verbatim from the network and used directly as `sequencer_address` in the block execution context and in the `PartialBlockHashComponents` that feed the final block hash. The proposal-init validation function `is_proposal_init_valid` checks `height`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices, `starknet_version`, `version_constant_commitment`, `timestamp`, and `fee_proposal_fri` — but never `builder`. Any validator who holds a legitimate turn as proposer can set `builder` to an arbitrary address; every other validator will re-execute the block with that spoofed `sequencer_address`, producing a wrong `get_sequencer_address()` syscall result and a wrong block hash that all nodes agree on and commit.

---

### Finding Description

**Step 1 — `builder` flows into `sequencer_address` without validation.**

`convert_to_sn_api_block_info` maps `ProposalInit` to `starknet_api::block::BlockInfo`:

```rust
// crates/apollo_consensus_orchestrator/src/utils.rs  line 332
sequencer_address: init.builder,
```

This `BlockInfo` is passed to `batcher.validate_block(ValidateBlockInput { block_info, … })` (validate path) and `batcher.propose_block(ProposeBlockInput { block_info, … })` (build path). The blockifier uses `block_info.sequencer_address` as the authoritative sequencer address for every transaction executed in the block.

**Step 2 — `sequencer_address` enters the block hash.**

`PartialBlockHashComponents::new` copies `block_info.sequencer_address` into the `sequencer` field:

```rust
// crates/starknet_api/src/block_hash/block_hash_calculator.rs  line 231
sequencer: SequencerContractAddress(block_info.sequencer_address),
```

`calculate_block_hash` then chains it directly into the Poseidon hash:

```rust
// crates/starknet_api/src/block_hash/block_hash_calculator.rs  line 258
.chain(&partial_block_hash_components.sequencer.0)
```

**Step 3 — `is_proposal_init_valid` never touches `builder`.**

The complete set of fields checked in `is_proposal_init_valid` (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs` lines 252–419):

| Field checked | Present? |
|---|---|
| `height` | ✓ |
| `l1_da_mode` | ✓ |
| `l2_gas_price_fri` | ✓ |
| `l1_gas_price_fri/wei`, `l1_data_gas_price_fri/wei` | ✓ |
| `starknet_version` | ✓ |
| `version_constant_commitment` | ✓ |
| `timestamp` | ✓ |
| `fee_proposal_fri` | ✓ |
| **`builder`** | **✗ — absent** |
| **`proposer`** | **✗ — absent** |

`proposer` is validated at the consensus-manager layer (`crates/apollo_consensus/src/manager.rs` line 860, `crates/apollo_consensus/src/single_height_consensus.rs` line 117) against the committee-derived expected proposer, so it cannot be spoofed by an outsider. `builder`, however, is validated **nowhere** in the entire proposal-validation path.

**Step 4 — `builder` also enters state-sync and the cende blob.**

`update_state_sync_with_new_block` writes `SequencerContractAddress(init.builder)` into the `BlockHeaderWithoutHash` that is committed to storage and forwarded to state sync:

```rust
// crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs  line 397
let sequencer = SequencerContractAddress(init.builder);
```

---

### Impact Explanation

A legitimate proposer (any validator whose turn it is in the Tendermint committee) can set `ProposalInit.builder` to an arbitrary `ContractAddress`. Because no validator checks this field, all nodes will:

1. **Execute every transaction in the block with the wrong `sequencer_address`** — the `get_sequencer_address()` syscall returns the attacker-chosen value. Any contract that gates logic on the sequencer address (fee-token contracts, access-controlled admin functions, etc.) will observe the wrong identity and may produce wrong state, wrong events, or wrong revert decisions.

2. **Commit a wrong block hash** — `sequencer_address` is a direct input to `calculate_block_hash`. The committed `PartialBlockHash` and the final `BlockHash` written to storage will be permanently wrong for that block. This corrupts the L1-anchored block hash chain.

3. **Propagate the wrong sequencer address into state sync and the cende blob** — downstream consumers (RPC, proving, L1 anchoring) all receive the spoofed value.

These match the Critical impact categories:
- *Wrong state, receipt, event, L1 message, class hash, storage value, or revert result from blockifier/syscall/execution logic for accepted input.*
- *Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact* (if fee-token logic branches on sequencer address).

---

### Likelihood Explanation

The trigger requires holding a legitimate proposer slot in the Tendermint committee for the target height and round. In the current single-sequencer deployment this is trivially satisfied by the one operator. In any future decentralized deployment, every validator is a potential proposer. No special privilege beyond a normal proposer turn is needed; the attack is a one-line change to the `ProposalInit` message before it is streamed to peers.

---

### Recommendation

Add `builder` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid`. The expected value should be the locally-configured builder address (analogous to how `l2_gas_price_fri` is compared against the node's own oracle reading). Concretely:

```rust
// In ProposalInitValidation, add:
pub builder: ContractAddress,

// In is_proposal_init_valid, add:
if init_proposed.builder != proposal_init_validation.builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!("builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder, init_proposed.builder),
    ));
}
```

The `builder` address used when building a proposal (`args.builder_address` in `initiate_build`) should be the same value used as the reference in validation.

---

### Proof of Concept

1. A validator holds proposer rights for height H, round R.
2. It constructs `ProposalInit { builder: ContractAddress(0xdead), … }` with all other fields valid.
3. It streams the proposal to peers.
4. Each peer calls `is_proposal_init_valid` — the function returns `Ok(())` because `builder` is never read.
5. Each peer calls `convert_to_sn_api_block_info(&init)` which sets `sequencer_address = 0xdead`.
6. The batcher executes all transactions with `block_info.sequencer_address = 0xdead`; every `get_sequencer_address()` syscall returns `0xdead`.
7. `PartialBlockHashComponents::new(&block_info, …)` stores `sequencer = 0xdead`.
8. `calculate_block_hash` hashes `0xdead` into position 3 of the Poseidon chain.
9. All nodes reach consensus on this block and commit the wrong block hash and wrong sequencer address to storage permanently.

**Relevant code locations:**

- `is_proposal_init_valid` (no `builder` check): [1](#0-0) 
- `convert_to_sn_api_block_info` — `sequencer_address: init.builder`: [2](#0-1) 
- `PartialBlockHashComponents::new` — `sequencer` from `block_info.sequencer_address`: [3](#0-2) 
- `calculate_block_hash` — `sequencer` chained into Poseidon hash: [4](#0-3) 
- `ProposalInit.builder` field definition: [5](#0-4) 
- `ProposalInitValidation` — `builder` absent: [6](#0-5) 
- `update_state_sync_with_new_block` — `sequencer = init.builder` committed to storage: [7](#0-6) 
- `proposer` validated at consensus layer (contrast — `builder` has no equivalent check): [8](#0-7)

### Citations

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

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-348)
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
}
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L245-282)
```rust
pub fn calculate_block_hash(
    partial_block_hash_components: &PartialBlockHashComponents,
    state_root: GlobalRoot,
    previous_block_hash: BlockHash,
) -> StarknetApiResult<BlockHash> {
    let block_hash_version: BlockHashVersion =
        partial_block_hash_components.starknet_version.try_into()?;
    let block_commitments = &partial_block_hash_components.header_commitments;
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
}
```

**File:** crates/apollo_protobuf/src/consensus.rs (L95-128)
```rust
pub struct ProposalInit {
    /// The height of the consensus (block number).
    pub height: BlockNumber,
    /// The current round of the consensus.
    pub round: Round,
    /// The last round that was valid.
    pub valid_round: Option<Round>,
    /// Address of the one who proposed the block in consensus.
    pub proposer: ContractAddress,
    /// Block timestamp.
    pub timestamp: u64,
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
    /// L1 data availability mode.
    pub l1_da_mode: L1DataAvailabilityMode,
    /// L2 gas price in FRI.
    pub l2_gas_price_fri: GasPrice,
    /// L1 gas price in FRI.
    pub l1_gas_price_fri: GasPrice,
    /// L1 data gas price in FRI.
    pub l1_data_gas_price_fri: GasPrice,
    // Keeping the wei prices for now, to use with L1 transactions.
    /// L1 gas price in WEI.
    pub l1_gas_price_wei: GasPrice,
    /// L1 data gas price in WEI.
    pub l1_data_gas_price_wei: GasPrice,
    /// Starknet protocol version.
    pub starknet_version: starknet_api::block::StarknetVersion,
    /// Version constant commitment.
    pub version_constant_commitment: StarkHash,
    /// Proposer's oracle-derived recommended L2 gas fee. Present iff
    /// `starknet_version >= V0_14_3`.
    pub fee_proposal_fri: Option<GasPrice>,
}
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
