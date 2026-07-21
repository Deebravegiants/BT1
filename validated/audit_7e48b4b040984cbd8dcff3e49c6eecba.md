Let me look at the `builder` field usage and fee collection to confirm the impact.

### Title
Unvalidated `builder` Field in `ProposalInit` Allows Malicious Proposer to Redirect All Block Fees to Arbitrary Address - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` validates most fields of `ProposalInit` but omits the `builder` field entirely. The `builder` field is passed directly to `convert_to_sn_api_block_info` as `sequencer_address` in `BlockInfo`, which the blockifier uses as the fee-transfer recipient for every transaction in the block. A malicious proposer can set `builder` to any address, causing all block fees to be credited to an attacker-controlled account while the proposal still passes consensus validation.

### Finding Description

`ProposalInit` carries a `builder` field (the address of the block builder/sequencer): [1](#0-0) 

`is_proposal_init_valid` validates `height`, `timestamp`, `starknet_version`, `version_constant_commitment`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices (within margin), and `fee_proposal_fri`. The `builder` field is absent from every check: [2](#0-1) 

`ProposalInitValidation` — the struct that carries the validator's reference values — has no `builder` field at all, so there is no expected value to compare against: [3](#0-2) 

After `is_proposal_init_valid` passes, `initiate_validation` calls `convert_to_sn_api_block_info`, which maps `init.builder` directly to `block_info.sequencer_address`: [4](#0-3) 

The resulting `BlockInfo` is forwarded to the batcher as the authoritative block context for the entire proposal: [5](#0-4) 

Inside the blockifier, `execute_fee_transfer` uses `block_context.block_info.sequencer_address` as the ERC-20 transfer recipient for every transaction fee: [6](#0-5) 

`add_fee_to_sequencer_balance` (concurrent path) also writes the fee balance update keyed on `block_context.block_info.sequencer_address`: [7](#0-6) 

The Starknet OS Cairo code confirms the same: `charge_fee` transfers to `block_context.block_info_for_execute.sequencer_address`: [8](#0-7) 

Additionally, `builder` enters the block hash via `PartialBlockHashComponents.sequencer`: [9](#0-8) 

Because both the proposer and the validator derive `sequencer_address` from the same `ProposalInit.builder`, the final `ProposalFin` commitment check still passes: [10](#0-9) 

The proposal is accepted, the block is committed, and the wrong `sequencer_address` is persisted in storage and forwarded to the cende pipeline.

### Impact Explanation

Every transaction fee in the block is transferred to the attacker-controlled `builder` address instead of the legitimate sequencer. The committed block header permanently records the wrong `sequencer_address`. The block hash is computed with the attacker's address, so the on-chain state root and all downstream commitments reflect the manipulated value. This is a **Critical** economic impact: incorrect fee/balance effect with direct financial consequence for every block the malicious proposer proposes.

### Likelihood Explanation

Any consensus participant that is selected as proposer in a given round can execute this attack. In a BFT system tolerating up to `f < n/3` Byzantine nodes, a single malicious proposer is within the explicit threat model. No special privilege beyond being selected as proposer is required. The attack is silent — no error is logged, no metric is incremented, and the proposal passes all existing validation checks.

### Recommendation

Add `builder` to `ProposalInitValidation` and validate it in `is_proposal_init_valid`:

```rust
// In ProposalInitValidation:
pub builder: ContractAddress,

// In is_proposal_init_valid, alongside the existing height/l1_da_mode/l2_gas_price_fri check:
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

The validator's expected `builder` address should be populated from the node's own configured `builder_address` when `ProposalInitValidation` is constructed, mirroring how `height`, `l1_da_mode`, and `starknet_version` are already sourced from local node state.

### Proof of Concept

1. Attacker controls one consensus node that is selected as proposer for block N.
2. Attacker constructs `ProposalInit` with `builder = attacker_wallet_address` (any valid `ContractAddress`).
3. Attacker streams the proposal to all validators.
4. Each validator calls `is_proposal_init_valid` → passes (no `builder` check).
5. Each validator calls `initiate_validation` → batcher receives `block_info.sequencer_address = attacker_wallet_address`.
6. Batcher executes all transactions; every `execute_fee_transfer` call sends fees to `attacker_wallet_address`.
7. Batcher computes `PartialBlockHashComponents` with `sequencer = attacker_wallet_address`.
8. Attacker sends `ProposalFin` with the commitment derived from `attacker_wallet_address`.
9. Validators compute the same commitment (same `builder`) → `built_block == received_fin.proposal_commitment` → proposal accepted.
10. Block is committed: `sequencer_address = attacker_wallet_address` in storage; all fees credited to attacker.

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L107-107)
```rust
    pub builder: ContractAddress,
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L75-85)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L244-247)
```rust
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L312-321)
```rust
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

**File:** crates/blockifier/src/transaction/account_transaction.rs (L571-573)
```rust
            calldata: calldata![
                *block_context.block_info.sequencer_address.0.key(), // Recipient.
                lsb_amount,
```

**File:** crates/blockifier/src/concurrency/fee_utils.rs (L113-116)
```rust
) {
    assert_ne!(
        sender_address, block_context.block_info.sequencer_address,
        "The sender cannot be the sequencer."
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
