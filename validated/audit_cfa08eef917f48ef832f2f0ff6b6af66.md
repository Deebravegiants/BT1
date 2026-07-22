### Title
Insufficient-History Fallback in `get_price_info` Allows Single-Block L1 Gas Price Manipulation to Corrupt `ProposalInit` Fees — (File: `crates/apollo_l1_gas_price/src/l1_gas_price_provider.rs`)

---

### Summary

`L1GasPriceProvider::get_price_info` is designed to compute a mean L1 gas price over `number_of_blocks_for_mean` blocks (default 300). When the ring buffer holds fewer samples than that threshold, the function silently falls back to averaging whatever samples are present — as few as one block. During the scraper startup window every sequencer node is in this under-populated state simultaneously. An attacker who can spike the Ethereum base fee in even a single block during that window can make every node embed a manipulated `l1_gas_price_fri` / `l1_data_gas_price_fri` / `l1_gas_price_wei` / `l1_data_gas_price_wei` into `ProposalInit`, causing all users to pay wrong L1 gas fees for the duration of the window, or causing proposer/validator disagreement that DoS-es block production.

---

### Finding Description

**Root cause — `get_price_info` insufficient-history fallback** [1](#0-0) 

```rust
let first_index = if last_index >= num_blocks {
    last_index - num_blocks
} else {
    warn!(
        "Not enough history to calculate the mean gas price. Using blocks {}-{}, inclusive.",
        samples[0].block_number,
        samples[last_index - 1].block_number,
    );
    L1_GAS_PRICE_PROVIDER_INSUFFICIENT_HISTORY.increment(1);
    0   // ← uses ALL available samples, even just 1
};
```

When `last_index < num_blocks` the code sets `first_index = 0` and averages only the blocks that happen to be present. There is no minimum-sample guard, no error return, and no rejection of the result by callers.

**When is the window under-populated?**

The scraper starts from `startup_num_blocks_multiplier × number_of_blocks_for_mean` blocks before the L1 tip (default `2 × 300 = 600`). [2](#0-1) 

During the initial catch-up scrape the provider accumulates blocks one at a time. Any call to `get_price_info` before 300 blocks are loaded returns a mean computed from fewer samples. On a new chain or after any restart the entire validator set is in this state simultaneously.

**No cross-config validation**

`L1GasPriceScraperConfig.number_of_blocks_for_mean` and `L1GasPriceProviderConfig.number_of_blocks_for_mean` are independent fields with no cross-validation. The TODO comment in the config acknowledges this: [3](#0-2) 

If `storage_limit` (the `RingBuffer` capacity) is set smaller than `number_of_blocks_for_mean`, the insufficient-history path fires on every single call — permanently. [4](#0-3) 

**How the corrupted mean reaches `ProposalInit`**

`get_price_info` feeds `get_l1_prices_in_fri_and_wei`, which is called by both `initiate_build` (proposer) and `is_proposal_init_valid` (validator): [5](#0-4) [6](#0-5) 

The validator enforces a 10 % margin between its own oracle read and the proposer's stated prices. A mean computed from one manipulated block can be an order of magnitude off from the true mean, either:

- **Both sides share the same under-populated window** → both accept the manipulated price → wrong `l1_gas_price_fri` / `l1_data_gas_price_fri` embedded in every block for the startup window duration → users pay wrong L1 gas fees.
- **Sides have different window sizes** (e.g., one node restarted later) → proposer and validator compute different means → the 10 % margin check fails → proposal rejected → DoS on block production.

---

### Impact Explanation

The corrupted value is `l1_gas_price_fri`, `l1_data_gas_price_fri`, `l1_gas_price_wei`, `l1_data_gas_price_wei` inside `ProposalInit`. These fields directly determine the L1 gas component of every transaction fee charged during the affected blocks. A single manipulated Ethereum block during the startup window is sufficient to shift the mean by an arbitrary factor, satisfying the **Critical** impact category: *Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact.*

The secondary outcome (proposer/validator disagreement) maps to the **High** impact category: *RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value* and gateway/admission-level DoS.

---

### Likelihood Explanation

- **Trigger 1 (startup

### Citations

**File:** crates/apollo_l1_gas_price/src/l1_gas_price_provider.rs (L96-99)
```rust
    pub fn initialize(&mut self) -> L1GasPriceProviderResult<()> {
        info!("Initializing L1GasPriceProvider with config: {:?}", self.config);
        self.price_samples_by_block = Some(RingBuffer::new(self.config.storage_limit));
        Ok(())
```

**File:** crates/apollo_l1_gas_price/src/l1_gas_price_provider.rs (L162-176)
```rust
        let num_blocks = usize::try_from(self.config.number_of_blocks_for_mean)
            .expect("number_of_blocks_for_mean is too large to fit into a usize");

        let first_index = if last_index >= num_blocks {
            last_index - num_blocks
        } else {
            warn!(
                "Not enough history to calculate the mean gas price. Using blocks {}-{}, \
                 inclusive.",
                samples[0].block_number,
                samples[last_index - 1].block_number,
            );
            L1_GAS_PRICE_PROVIDER_INSUFFICIENT_HISTORY.increment(1);
            0
        };
```

**File:** crates/apollo_l1_gas_price/src/l1_gas_price_scraper.rs (L82-89)
```rust
            // If no starting block is provided, the default is to start from
            // startup_num_blocks_multiplier * number_of_blocks_for_mean before the tip of
            // L1. Note that for new chains this subtraction may be
            // negative, hence the use of saturating_sub.
            let latest = latest.saturating_sub(
                self.config.number_of_blocks_for_mean * self.config.startup_num_blocks_multiplier,
            );
            return latest;
```

**File:** crates/apollo_l1_gas_price_config/src/config.rs (L173-175)
```rust
// TODO(guyn): find a way to synchronize the value of number_of_blocks_for_mean
// with the one in L1GasPriceProviderConfig. In the end they should both be loaded
// from VersionedConstants.
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L322-368)
```rust
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
```
