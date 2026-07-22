### Title
L1 Gas Price Scraper Uses Block-Count-Based "Finality" Instead of Ethereum PoS Finalized Block Tag, Enabling Reorg-Based Gas Price Manipulation - (`crates/apollo_l1_gas_price/src/l1_gas_price_scraper.rs`)

---

### Summary

The `L1GasPriceScraper` determines the "safe" L1 block ceiling by calling `get_block_number()` (the chain head) and subtracting a configurable integer `finality`. On Ethereum proof-of-stake this is not true finality: blocks can be produced indefinitely without epochs being finalized, and the head can be reorged far beyond any fixed block-count offset. The default value of `finality` in the canonical config schema is **0**, meaning the scraper ingests the absolute latest (unfinalized) block by default. The gas prices scraped from these non-finalized blocks are embedded verbatim into `ProposalInit` and ultimately into the Starknet block hash via `PartialBlockHashComponents`. A validator accepts a proposed `ProposalInit` if its L1 gas prices are within a ±10 % margin of its own oracle reading. An attacker who can cause an L1 reorg that shifts gas prices within that margin can therefore cause incorrect gas prices to be committed into finalized L2 blocks, producing incorrect fee and resource accounting with direct economic impact.

---

### Finding Description

**Root cause — `latest_l1_block_number` uses the chain head, not the finalized tag** [1](#0-0) 

```rust
async fn latest_l1_block_number(&mut self) -> L1GasPriceScraperResult<L1BlockNumber, B> {
    let latest_l1_block_number = self
        .base_layer
        .latest_l1_block_number()   // ← returns chain HEAD, not finalized
        .await
        .map_err(L1GasPriceScraperError::BaseLayerError)?;
    let latest_l1_block_number = latest_l1_block_number
        .checked_sub(self.config.finality)   // ← block-count offset only
        ...
    Ok(latest_l1_block_number)
}
```

The underlying Ethereum call is `get_block_number()`, which returns the head block: [2](#0-1) 

There is no call to `BlockNumber::Finalized` (or `eth_getBlockByNumber("finalized", …)`) anywhere in the scraper path. The `finality` field is described as "Number of blocks to wait for finality in L1" but is implemented as a simple subtraction from the head, not a query to the PoS finality checkpoint.

**Default `finality` is 0 in the production config schema** [3](#0-2) 

```json
"l1_gas_price_scraper_config.finality": {
    "description": "Number of blocks to wait for finality in L1",
    "value": 0
}
```

The deployment override sets it to 10: [4](#0-3) 

Ten confirmations is far below the ~128 blocks (~25 minutes) required for a checkpoint to be finalized on Ethereum PoS. Any node that runs with the schema default (0) or any value below ~128 is fully exposed.

**Gas prices flow directly into the block hash**

The scraped prices are stored in the `L1GasPriceProvider` ring buffer: [5](#0-4) 

They are fetched at proposal time via `get_l1_prices_in_fri_and_wei` and placed into `ProposalInit`: [6](#0-5) 

The validator accepts the proposal if all four price fields (`l1_gas_price_fri`, `l1_data_gas_price_fri`, `l1_gas_price_wei`, `l1_data_gas_price_wei`) are within ±10 % of its own oracle reading: [7](#0-6) 

These prices are then embedded into `PartialBlockHashComponents`, which feeds `PartialBlockHash` → `ProposalCommitment` → the final Starknet block hash: [8](#0-7) [9](#0-8) 

**Reorg detection does not protect against pre-existing reorged data**

The scraper's `assert_no_l1_reorgs` only checks that the *next* block's parent hash matches the *last processed* block's hash: [10](#0-9) 

If the reorg has already settled (i.e., the attacker's fork is the new canonical chain before the scraper reaches those blocks), every block the scraper processes will have consistent parent hashes within the reorged fork. The scraper will ingest the reorged gas prices without triggering `L1ReorgDetected`. The ring buffer will be populated with prices from the attacker-controlled fork, and those prices will be used in the next L2 block proposal.

---

### Impact Explanation

The L1 gas prices embedded in `ProposalInit` are used by the blockifier to compute transaction fees (`l1_gas_price_fri`, `l1_data_gas_price_fri`, `l1_gas_price_wei`, `l1_data_gas_price_wei`). If an attacker can shift these prices within the ±10 % validation margin via an L1 reorg, every transaction in the affected L2 block will be charged fees computed from the manipulated prices. Because the prices are committed into the block hash, the incorrect fees are permanent and cannot be corrected after consensus. This is a direct economic impact on users and the protocol: users may be systematically undercharged (protocol revenue loss) or overcharged (user funds loss), and the committed block hash will differ from what honest nodes would have produced with finalized L1 data.

---

### Likelihood Explanation

Ethereum PoS has experienced finality failures (e.g., the May 2023 mainnet incident referenced in the external report). During such an event, an attacker who controls a modest fraction of validators can propose alternative blocks for the non-finalized epochs. With `finality = 10` (the deployment value), only 10 blocks of buffer exist; a reorg of 11+ blocks is sufficient to inject manipulated gas prices into the scraper's ring buffer without triggering the parent-hash reorg check. With the schema default of `finality = 0`, even a single-block reorg suffices. The 10 % validation margin is wide enough to accommodate realistic gas price swings within a short reorg window.

---

### Recommendation

**Short term**: Replace the `get_block_number()` call in `latest_l1_block_number` with a query for the Ethereum PoS finalized block tag, analogous to the fix suggested in the external report for the Fortuna provider:

```rust
// Instead of:
self.contract.provider().get_block_number()
// Use:
self.contract.provider()
    .get_block(BlockId::Number(BlockNumberOrTag::Finalized))
    .await?
    .map(|b| b.header.number)
```

This ensures the scraper only ingests gas prices from blocks that have received a 2/3 supermajority vote from the validator set and cannot be reorged.

**Long term**: Audit the `L1EventsScraper` (which uses the same `finality`-subtraction pattern) for analogous exposure. Set the config schema default for `l1_gas_price_scraper_config.finality` to a value that reflects true PoS finality depth (~128 blocks) as a safe floor, and add a validation that rejects `finality < 64` when the connected chain is Ethereum mainnet or a PoS testnet.

---

### Proof of Concept

1. Deploy the sequencer with `l1_gas_price_scraper_config.finality = 10` (the production deployment value).
2. On Ethereum PoS, cause a finality stall (e.g., by taking ≥ 1/3 of validators offline). The chain continues producing blocks but no epoch is finalized.
3. After 11+ blocks have been produced on the stalled chain, introduce a reorg: propose an alternative fork starting from block `head - 11` with artificially inflated `base_fee_per_gas` values (e.g., +9 % above the honest chain's values, within the 10 % margin).
4. Allow the reorged fork to become the canonical chain. The scraper's `assert_no_l1_reorgs` check will not fire because the scraper has not yet processed the divergence point — it will simply continue processing the new canonical blocks, all of which have consistent parent hashes within the reorged fork.
5. The ring buffer now contains gas prices from the attacker-controlled fork. The next L2 block proposal will embed `l1_gas_price_fri` and `l1_data_gas_price_wei` values that are ~9 % higher than the honest values.
6. Validators accept the proposal (within the ±10 % margin). The block is committed with inflated gas prices. Every transaction in the block is charged ~9 % more in L1 gas fees than it should be, with the excess permanently committed into the block hash.

### Citations

**File:** crates/apollo_l1_gas_price/src/l1_gas_price_scraper.rs (L158-179)
```rust
    async fn assert_no_l1_reorgs(
        &self,
        new_header: &L1BlockHeader,
    ) -> L1GasPriceScraperResult<(), B> {
        // If no last block was processed, we don't need to check for reorgs.
        let Some(ref last_header) = self.last_l1_header else {
            return Ok(());
        };

        if new_header.parent_hash != last_header.hash {
            L1_GAS_PRICE_SCRAPER_REORG_DETECTED.increment(1);
            return Err(L1GasPriceScraperError::L1ReorgDetected {
                reason: format!(
                    "Last processed L1 block hash, {}, for block number {}, is different from the \
                     hash stored, {}",
                    new_header.parent_hash, last_header.number, last_header.hash,
                ),
            });
        }

        Ok(())
    }
```

**File:** crates/apollo_l1_gas_price/src/l1_gas_price_scraper.rs (L181-194)
```rust
    async fn latest_l1_block_number(&mut self) -> L1GasPriceScraperResult<L1BlockNumber, B> {
        let latest_l1_block_number = self
            .base_layer
            .latest_l1_block_number()
            .await
            .map_err(L1GasPriceScraperError::BaseLayerError)?;
        let latest_l1_block_number = latest_l1_block_number
            .checked_sub(self.config.finality)
            .ok_or(L1GasPriceScraperError::LatestBlockNumberTooLow {
                latest_l1_block_number,
                finality: self.config.finality,
            })?;
        Ok(latest_l1_block_number)
    }
```

**File:** crates/papyrus_base_layer/src/ethereum_base_layer_contract.rs (L219-227)
```rust
    #[instrument(skip(self), err)]
    async fn latest_l1_block_number(&mut self) -> EthereumBaseLayerResult<L1BlockNumber> {
        let block_number = tokio::time::timeout(
            self.config.timeout_millis,
            self.contract.provider().get_block_number(),
        )
        .await??;
        Ok(block_number)
    }
```

**File:** crates/apollo_node/resources/config_schema.json (L3412-3416)
```json
  "l1_gas_price_scraper_config.finality": {
    "description": "Number of blocks to wait for finality in L1",
    "privacy": "Public",
    "value": 0
  },
```

**File:** crates/apollo_deployments/resources/app_configs/l1_gas_price_scraper_config.json (L1-8)
```json
{
  "l1_gas_price_scraper_config.finality": 10,
  "l1_gas_price_scraper_config.number_of_blocks_for_mean": 300,
  "l1_gas_price_scraper_config.polling_interval": 120,
  "l1_gas_price_scraper_config.starting_block": 0,
  "l1_gas_price_scraper_config.starting_block.#is_none": true,
  "l1_gas_price_scraper_config.startup_num_blocks_multiplier": 2
}
```

**File:** crates/apollo_l1_gas_price/src/l1_gas_price_provider.rs (L102-121)
```rust
    pub fn add_price_info(&mut self, new_data: GasPriceData) -> L1GasPriceProviderResult<()> {
        // In case the provider has been restarted while the scraper is still running,
        // a NotInitializedError will be returned to the scraper. We expect the scraper to exit with
        // an error, and that infrastructure will restart it, leading to initialization.
        let Some(samples) = &mut self.price_samples_by_block else {
            return Err(L1GasPriceProviderError::NotInitializedError);
        };
        if let Some(data) = samples.back() {
            if new_data.block_number != data.block_number + 1 {
                return Err(L1GasPriceProviderError::UnexpectedBlockNumberError {
                    expected: data.block_number + 1,
                    found: new_data.block_number,
                });
            }
        }
        trace!("Received price sample for L1 block: {:?}", new_data);
        info_every_n_ms!(1_000, "Received price sample for L1 block: {:?}", new_data);
        samples.push(new_data);
        Ok(())
    }
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L162-188)
```rust
    let (l1_prices_fri, l1_prices_wei) = get_l1_prices_in_fri_and_wei(
        args.deps.l1_gas_price_provider.clone(),
        timestamp,
        args.previous_proposal_init.as_ref(),
        &args.gas_price_params,
    )
    .await;
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L342-368)
```rust
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
