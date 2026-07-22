### Title
Unvalidated `ProposalInit.builder` Field Used as `sequencer_address` in Block Execution — (File: `crates/apollo_consensus_orchestrator/src/utils.rs`)

---

### Summary

`ProposalInit.builder` is a proposer-supplied wire field that is mapped directly to `sequencer_address` in `BlockInfo` and forwarded to the batcher for block execution. The validator's `is_proposal_init_valid` function validates every other economically-significant field in `ProposalInit` but never checks `builder`. A malicious-but-committee-eligible proposer can set `builder` to any arbitrary address; all validators will accept the proposal, execute the block with the attacker-chosen `sequencer_address`, and commit a block in which fees are credited to the wrong address and `get_sequencer_address()` returns the attacker-controlled value.

---

### Finding Description

`convert_to_sn_api_block_info` in `crates/apollo_consensus_orchestrator/src/utils.rs` converts a `ProposalInit` into a `starknet_api::block::BlockInfo` that is passed to the batcher for both the proposer path (`propose_block`) and the validator path (`validate_block`):

```rust
// utils.rs:329-347
Ok(starknet_api::block::BlockInfo {
    block_number: init.height,
    block_timestamp: BlockTimestamp(init.timestamp),
    sequencer_address: init.builder,   // ← proposer-supplied, unvalidated
    gas_prices: GasPrices { ... },
    use_kzg_da: init.l1_da_mode.is_use_kzg_da(),
    starknet_version: init.starknet_version,
})
```

`is_proposal_init_valid` in `crates/apollo_consensus_orchestrator/src/validate_proposal.rs` (lines 252–418) validates the following `ProposalInit` fields before the batcher is invoked:

| Field | Validated |
|---|---|
| `timestamp` | ✓ (monotonicity + future window) |
| `starknet_version` | ✓ (must equal LATEST) |
| `version_constant_commitment` | ✓ (must equal sentinel) |
| `height` | ✓ |
| `l1_da_mode` | ✓ |
| `l2_gas_price_fri` | ✓ |
| `l1_gas_price_fri/wei` | ✓ (within-margin) |
| `l1_data_gas_price_fri/wei` | ✓ (within-margin) |
| `fee_proposal_fri` | ✓ (presence + bounds) |
| **`builder`** | **✗ — never checked** |

The `builder` field is set by the proposer in `initiate_build` (`build_proposal.rs:174`) from `args.builder_address`, which is a local static-config value. No validator has any mechanism to know the proposer's configured `builder_address`, and no check is performed. The field travels over the wire, is deserialized from protobuf (`converters/consensus.rs:204`), and is consumed verbatim as `sequencer_address`.

---

### Impact Explanation

`sequencer_address` has three concrete effects inside block execution:

1. **Fee collection** — The blockifier credits transaction fees to `sequencer_address`. A malicious proposer who sets `builder` to an attacker-controlled address causes all fees in the block to be credited there instead of to the legitimate sequencer. This is a direct, irreversible economic loss for the honest sequencer operator and matches the "Incorrect fee … with economic impact" critical criterion.

2. **`get_sequencer_address()` syscall** — Any Cairo contract that calls `get_sequencer_address()` during execution of that block receives the attacker-chosen value. Contracts that gate logic on the sequencer address (e.g., fee-token contracts, governance contracts, or any contract that checks `caller == get_sequencer_address()`) will behave incorrectly. This matches "Wrong … revert result from blockifier/syscall/execution logic."

3. **Block header commitment** — `sequencer_address` is part of the committed block header and is included in the block hash. The committed on-chain state permanently records the attacker-chosen address as the block's sequencer, corrupting the authoritative historical view.

Because all validators use the same `builder` value from the accepted `ProposalInit`, they all compute the same (wrong) block hash and reach consensus on the corrupted block. There is no fork; the corruption is unanimous and final.

---

### Likelihood Explanation

The trigger requires the attacker to be the elected proposer for a round — i.e., a committee-eligible validator. The `proposer` field in `ProposalInit` is validated against the committee (`manager.rs:860–865`, `single_height_consensus.rs:114–119`), so an external peer cannot forge a proposal. However, any single malicious validator that wins a proposer slot can execute this attack with zero additional effort: the only change needed is to set `builder` to an arbitrary address in the `ProposalInit` struct before broadcasting. No cryptographic material needs to be forged and no other field needs to be altered.

---

### Recommendation

Add a `builder` check inside `is_proposal_init_valid`. The simplest correct fix is to include `builder` in the `ProposalInitValidation` struct (alongside `l1_da_mode`, `l2_gas_price_fri`, etc.) and populate it from the node's own `static_config.builder_address` when constructing `ProposalInitValidation` in `validate_proposal` and `set_height_and_round`. The check then mirrors the existing pattern:

```rust
// In ProposalInitValidation:
pub builder_address: ContractAddress,

// In is_proposal_init_valid:
if init_proposed.builder != proposal_init_validation.builder_address {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder_address, init_proposed.builder
        ),
    ));
}
```

This is consistent with how `l1_da_mode` and `l2_gas_price_fri` are validated: the validator compares the proposer-supplied value against its own locally-configured reference.

---

### Proof of Concept

1. A committee-eligible validator modifies its `initiate_build` path to set `builder: ContractAddress::from(0xattacker)` instead of `args.builder_address`.
2. It wins a proposer slot and broadcasts the `ProposalInit` with the modified `builder`.
3. Every honest validator calls `is_proposal_init_valid` — the function returns `Ok(())` because `builder` is never checked.
4. `initiate_validation` calls `convert_to_sn_api_block_info(&init)`, producing a `BlockInfo` with `sequencer_address = 0xattacker`.
5. The batcher executes the block; all transaction fees are credited to `0xattacker`; every `get_sequencer_address()` syscall returns `0xattacker`.
6. `finish_proposal` returns a `partial_block_hash` computed over the corrupted state; `proposal_commitment_from` wraps it; the commitment matches the proposer's `ProposalFin`; consensus decides on the corrupted block.
7. `finalize_decision` commits the block to storage with `sequencer_address = 0xattacker` permanently recorded in the block header. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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

**File:** crates/apollo_protobuf/src/consensus.rs (L94-128)
```rust
#[derive(Clone, Debug, PartialEq)]
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
