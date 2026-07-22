### Title
Unvalidated `builder` Field in `ProposalInit` Allows Arbitrary Sequencer Address in Committed Block — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` validates many fields of an incoming `ProposalInit` but never checks the `builder` field. Because `builder` is passed verbatim as `sequencer_address` into `BlockInfo`, a malicious proposer can inject an arbitrary sequencer address into every committed block. This corrupts fee collection (fees are ERC-20-transferred to `block_context.block_info.sequencer_address`), the `get_sequencer_address` syscall result, and the `sequencer` slot of the Poseidon block hash that is anchored on L1.

---

### Finding Description

`ProposalInit` carries a `builder` field — the address of the block-building node. [1](#0-0) 

`is_proposal_init_valid` is the sole gate that checks proposer-supplied metadata before the batcher begins executing transactions. It validates: `timestamp`, `starknet_version`, `version_constant_commitment`, `height`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices (within margin), and `fee_proposal_fri`. [2](#0-1) 

`builder` is **absent** from `ProposalInitValidation` and is never checked. [3](#0-2) 

After validation passes, `convert_to_sn_api_block_info` maps `init.builder` directly to `BlockInfo.sequencer_address`: [4](#0-3) 

This `BlockInfo` is forwarded to `batcher.validate_block` (and later `batcher.propose_block` on the proposer side), so both sides execute with the attacker-chosen sequencer address. Because both sides derive the same `PartialBlockHash` from the same `builder`, the `ProposalFinMismatch` guard passes: [5](#0-4) 

The tainted `init` is then stored in `valid_proposals` and retrieved at `decision_reached`, where it is used to finalize the block: [6](#0-5) 

---

### Impact Explanation

**1. Fee theft / misdirection (Critical — economic impact)**

Every fee transfer calls `execute_fee_transfer`, which uses `block_context.block_info.sequencer_address` as the ERC-20 recipient: [7](#0-6) 

The OS-level `charge_fee` Cairo function does the same: [8](#0-7) 

Setting `builder` to an attacker-controlled address redirects all transaction fees for the block to that address.

**2. Wrong `get_sequencer_address` syscall result (Critical — wrong syscall output)**

The `sequencer_address` in `BlockInfo` is the value returned to contracts by the `get_sequencer_address` syscall. Any contract that gates logic on the sequencer address (access control, fee-rebate schemes, etc.) will receive the attacker-supplied value.

**3. Wrong block hash / state commitment (Critical — wrong block hash)**

`sequencer_address` is hashed into `PartialBlockHashComponents.sequencer`, which feeds `calculate_block_hash`: [9](#0-8) [10](#0-9) 

The resulting block hash is anchored on L1 and used for proof verification. A wrong sequencer address produces a wrong block hash for every block the attacker proposes.

---

### Likelihood Explanation

The attacker must be a validator that wins a Tendermint proposer slot. In a decentralized validator set this is an expected event for every participant. No special privilege beyond being a validator is required; the attack is fully exercisable from the normal proposal flow with a single-field modification to `ProposalInit`.

---

### Recommendation

Add `builder` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid`. The expected value is the locally-configured `builder_address` (already used when building proposals in `initiate_build`): [11](#0-10) 

The check should mirror the existing exact-match checks (e.g., `height`, `l1_da_mode`):

```rust
if init_proposed.builder != proposal_init_validation.builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder, init_proposed.builder
        ),
    ));
}
```

---

### Proof of Concept

1. Attacker node is selected as Tendermint proposer for height H.
2. Attacker constructs `ProposalInit` with `builder = <attacker_wallet_address>` instead of its own configured builder address.
3. Attacker streams the proposal to all validators.
4. Each validator calls `is_proposal_init_valid` — `builder` is not checked, validation passes.
5. Each validator calls `convert_to_sn_api_block_info(init)`, producing `BlockInfo { sequencer_address: <attacker_wallet_address>, … }`.
6. Each validator's batcher executes all transactions with `sequencer_address = <attacker_wallet_address>`. Every `execute_fee_transfer` call transfers fees to the attacker's wallet.
7. Both proposer and validator batchers compute identical `PartialBlockHash` (both used the same `builder`). `ProposalFinMismatch` check passes.
8. Consensus reaches decision; block is committed with `sequencer_address = <attacker_wallet_address>`.
9. All transaction fees for block H are credited to the attacker. All `get_sequencer_address` syscall results in block H return the attacker's address. The block hash anchored on L1 encodes the attacker's address as the sequencer.

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

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-332)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L999-1024)
```rust
        let (init, transactions, proposal_id, finished_info) = {
            let mut proposals = self.valid_proposals.lock().unwrap();
            let (init, transactions, proposal_id, finished_info) =
                proposals.get_proposal(&height, &round, &commitment).clone();
            proposals.remove_proposals_below_or_at_height(&height);
            (init, transactions, proposal_id, finished_info)
        };

        let decision_reached_response =
            self.deps.batcher.decision_reached(DecisionReachedInput { proposal_id }).await?;

        // CRITICAL: The block is now committed. This function must not fail beyond this point
        // unless the state is fully reverted, otherwise the node will be left in an
        // inconsistent state.

        self.finalize_decision(
            height,
            &init,
            commitment,
            transactions,
            decision_reached_response,
            finished_info.block_header_commitments.clone(),
            finished_info.l2_gas_used,
            wait_for_last_commitment,
        )
        .await;
```

**File:** crates/blockifier/src/transaction/account_transaction.rs (L570-575)
```rust
            entry_point_selector: selector_from_name(constants::TRANSFER_ENTRY_POINT_NAME),
            calldata: calldata![
                *block_context.block_info.sequencer_address.0.key(), // Recipient.
                lsb_amount,
                msb_amount
            ],
```

**File:** crates/apollo_starknet_os_program/src/cairo/starkware/starknet/core/os/execution/transaction_impls.cairo (L129-131)
```text
    local calldata: TransferCallData = TransferCallData(
        recipient=block_context.block_info_for_execute.sequencer_address,
        amount=Uint256(low=low_actual_fee, high=0),
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

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L173-174)
```rust
        proposer: args.build_param.proposer,
        builder: args.builder_address,
```
