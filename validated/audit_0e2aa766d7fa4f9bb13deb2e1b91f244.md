### Title
Unvalidated `ProposalInit.builder` Flows Into `sequencer_address`, Enabling Fee Redirection and Wrong Block Hash - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`ProposalInit.builder` is a proposer-supplied field that is never checked by `is_proposal_init_valid`. It is passed verbatim as `sequencer_address` into `BlockInfo`, which the batcher uses to execute transactions and compute `PartialBlockHashComponents`. Because the validator re-executes the block with the same proposer-supplied `builder`, the `ProposalCommitment` comparison always passes regardless of what address the proposer chose. A Byzantine proposer can therefore commit any `sequencer_address` into the canonical block, redirecting all fee transfers and corrupting the block hash.

### Finding Description

`ProposalInit` carries a `builder` field defined as "Address of the one who builds/sequences the block." [1](#0-0) 

When the proposer builds a block, `builder` is set from local configuration: [2](#0-1) 

`is_proposal_init_valid` — the sole gate that checks proposer-supplied `ProposalInit` fields — validates timestamp, `starknet_version`, `version_constant_commitment`, `height`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices, and `fee_proposal_fri`. It does **not** validate `builder`: [3](#0-2) 

`convert_to_sn_api_block_info` maps `init.builder` directly to `sequencer_address` in the `BlockInfo` that is forwarded to the batcher: [4](#0-3) 

The batcher constructs `PartialBlockHashComponents` from that `BlockInfo`, placing the proposer-supplied address into the `sequencer` slot: [5](#0-4) 

`sequencer` is then chained into the Poseidon block hash: [6](#0-5) 

Because the validator calls `initiate_validation` with the same `init` (including the attacker-chosen `builder`), the batcher on the validator side computes the same `PartialBlockHash` as the proposer, so the `ProposalCommitment` comparison at the end of `validate_proposal` always passes: [7](#0-6) 

The `proposer` field is correctly validated in `single_height_consensus.rs`: [8](#0-7) 

`builder` has no equivalent guard anywhere in the validation path.

### Impact Explanation

`sequencer_address` is the fee-transfer destination for every transaction in the block. A Byzantine proposer who sets `builder` to an attacker-controlled address causes all transaction fees in that block to be transferred to that address instead of the legitimate sequencer, producing wrong storage state. Additionally, the committed block hash encodes the wrong `sequencer_address`, making the on-chain block hash and every downstream RPC view (`starknet_getBlock`, `sequencer_address` field) permanently incorrect for that block. Contracts that call `get_sequencer_address()` during execution also receive the attacker-chosen value, enabling further manipulation of contract logic that branches on the sequencer identity.

### Likelihood Explanation

Requires a Byzantine proposer — a validator that is legitimately elected as round leader but acts maliciously. In a BFT network tolerating `f` Byzantine faults, any one of the `f` Byzantine validators that wins a proposal round can trigger this. No special network position or off-chain capability is needed beyond being the current round's proposer.

### Recommendation

Add a `builder` field to `ProposalInitValidation` (populated from the local node's configured builder address, analogous to how `l1_da_mode` and `l2_gas_price_fri` are populated), and reject proposals where `init.builder` does not match the expected value inside `is_proposal_init_valid`. If the protocol intentionally allows the proposer to nominate an arbitrary builder, the expected builder address must at minimum be derivable from the committee/validator-set data so that validators can enforce it.

### Proof of Concept

1. A Byzantine node wins the proposer slot for height H, round R.
2. It constructs `ProposalInit` with `builder = attacker_address` (any address it controls).
3. It calls `build_proposal` → `initiate_build` → `convert_to_sn_api_block_info` → batcher receives `sequencer_address = attacker_address`.
4. The batcher executes all transactions; fee transfers credit `attacker_address`.
5. The batcher computes `PartialBlockHashComponents { sequencer: attacker_address, … }` and returns `ProposalCommitment`.
6. The proposer streams `ProposalInit(builder=attacker_address)` + transactions + `ProposalFin(commitment)` to validators.
7. Each validator calls `is_proposal_init_valid` — `builder` is not checked, validation passes.
8. Each validator calls `initiate_validation` with the same `init`, so its batcher also uses `sequencer_address = attacker_address` and computes the identical `ProposalCommitment`.
9. `built_block == received_fin.proposal_commitment` → proposal accepted.
10. Block is committed with `sequencer_address = attacker_address`; all fees for height H are in the attacker's account; the block hash encodes the wrong sequencer. [9](#0-8) [10](#0-9)

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L106-107)
```rust
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L173-174)
```rust
        proposer: args.build_param.proposer,
        builder: args.builder_address,
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L141-160)
```rust
pub(crate) async fn validate_proposal(
    mut args: ProposalValidateArguments,
) -> ValidateProposalResult<ProposalCommitment> {
    let mut content = Vec::new();
    let mut verify_and_store_proof_tasks: Vec<VerifyAndStoreProofTask> = Vec::new();
    let now = args.deps.clock.now();

    let Some(deadline) = now.checked_add_signed(chrono::TimeDelta::from_std(args.timeout).unwrap())
    else {
        return Err(ValidateProposalError::CannotCalculateDeadline { timeout: args.timeout, now });
    };

    is_proposal_init_valid(
        &args.proposal_init_validation,
        &args.init,
        args.deps.clock.as_ref(),
        args.deps.l1_gas_price_provider,
        &args.gas_price_params,
    )
    .await?;
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

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-333)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-260)
```rust
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
            .chain(&block_commitments.concatenated_counts)
```

**File:** crates/apollo_consensus/src/single_height_consensus.rs (L114-120)
```rust
        let Ok(proposer_id) = self.committee.get_proposer(height, init.round) else {
            return VecDeque::new();
        };
        if init.proposer != proposer_id {
            warn!("Invalid proposer: expected {:?}, got {:?}", proposer_id, init.proposer);
            return VecDeque::new();
        }
```
