### Title
Proposer-Controlled `timestamp` Anchors Validator's L1 Gas Price Reference, Allowing Stale Prices in Committed Blocks — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` enforces only a **future** bound on `ProposalInit.timestamp` (`<= now + 1 s`) and a **monotonicity** bound (`>= last_block_timestamp`), but no **lower bound relative to `now`**. The validator then uses the proposer-supplied timestamp — not the current wall-clock time — to look up its own L1 gas price reference. Because the reference is anchored to the proposer's timestamp, a malicious proposer can pick a past timestamp (within the ring-buffer window, up to ~10 hours of L1 history), supply the matching stale L1 gas prices, and have every validator accept them. The committed block then carries incorrect L1 gas prices, corrupting fee accounting for every transaction in that block.

### Finding Description

In `is_proposal_init_valid`:

```rust
let now: u64 = clock.unix_now();
let last_block_timestamp =
    proposal_init_validation.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
if init_proposed.timestamp < last_block_timestamp {          // only monotonicity
    return Err(...);
}
if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds {
    return Err(...);                                         // only future cap (1 s in prod)
}
```

There is no check of the form `init_proposed.timestamp >= now - lower_bound`. After these checks pass, the validator fetches its own reference prices using the proposer-supplied timestamp:

```rust
let (l1_gas_prices_fri, l1_gas_prices_wei) = get_l1_prices_in_fri_and_wei(
    l1_gas_price_provider,
    init_proposed.timestamp,   // ← proposer-controlled
    proposal_init_validation.previous_proposal_init.as_ref(),
    gas_price_params,
)
.await;
```

The `within_margin` check then compares the proposed prices against this proposer-anchored reference:

```rust
if !(within_margin(l1_gas_price_fri_proposed, l1_gas_price_fri, l1_gas_price_margin_percent)
    && within_margin(l1_data_gas_price_fri_proposed, l1_data_gas_price_fri, ...)
    && within_margin(l1_gas_price_wei_proposed, l1_gas_price_wei, ...)
    && within_margin(l1_data_gas_price_wei_proposed, l1_data_gas_price_wei, ...))
```

Because the reference is derived from `init_proposed.timestamp`, the proposer can choose any timestamp in the past (bounded only by `last_block_timestamp` from below), look up what L1 gas prices were at that time, and propose those prices. Every honest validator will independently compute the same stale reference and accept the proposal.

`L1GasPriceProvider::get_price_info` has a staleness guard only for timestamps **ahead** of the last scraped block:

```rust
if timestamp.0 > (*last_timestamp + self.config.max_time_gap_seconds) {
    return Err(L1GasPriceProviderError::StaleL1GasPricesError { ... });
}
```

There is no symmetric guard for timestamps **behind** the ring buffer's oldest entry. With `storage_limit = 3000` L1 blocks at ~12 s/block, the ring buffer covers ~10 hours of L1 history. Any timestamp within that window returns real (but stale) prices without error.

### Impact Explanation

Every transaction in the affected block pays fees computed from the stale L1 gas prices embedded in `BlockInfo`. If L1 gas prices were lower in the past, users underpay, causing the sequencer to absorb L1 costs. If prices were higher, users overpay. Because the prices are committed on-chain and used by the blockifier for fee deduction and bouncer accounting, the error is permanent and affects the entire block's economic correctness. This matches the allowed impact: **incorrect fee / L1 gas price effect with economic impact**.

### Likelihood Explanation

The attacker must be a legitimately selected proposer (a staked validator). Being a proposer is a normal protocol role, not a privileged operation. The exploitable window is bounded by `now - last_block_timestamp`. In normal steady-state operation this is only a few seconds (one block time), limiting the price deviation. However, after a chain restart, a long sync gap, or a period of many failed rounds, `last_block_timestamp` can be minutes to hours behind `now`, opening a window where L1 gas prices may have changed materially.

### Recommendation

Add a lower-bound check on `init_proposed.timestamp` relative to `now` inside `is_proposal_init_valid`, symmetric to the existing upper-bound check:

```rust
// Reject timestamps too far in the past (mirror of the future cap).
if now > init_proposed.timestamp
    && now - init_proposed.timestamp > proposal_init_validation.block_timestamp_window_seconds
{
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!("Timestamp is too old: now={now}, proposed={}", init_proposed.timestamp),
    ));
}
```

Alternatively, use `now` (not `init_proposed.timestamp`) as the reference timestamp when the validator fetches its own L1 gas price reference, so the reference is always anchored to the current wall-clock time regardless of what the proposer claims.

### Proof of Concept

1. The chain has just restarted after a 30-minute outage; `last_block_timestamp = now - 1800`.
2. A malicious validator is selected as proposer for the first post-restart block.
3. The proposer sets `init.timestamp = last_block_timestamp` (1800 s in the past) — this passes both timestamp checks: `>= last_block_timestamp` and `<= now + 1`.
4. The proposer queries `get_price_info(BlockTimestamp(last_block_timestamp))` and obtains the L1 gas prices from 30 minutes ago (e.g., significantly lower than current prices during a gas spike).
5. The proposer includes those stale prices in `ProposalInit.l1_gas_price_fri / l1_gas_price_wei / ...`.
6. Every honest validator calls `is_proposal_init_valid`, which:
   - Accepts the timestamp (both bounds pass).
   - Calls `get_l1_prices_in_fri_and_wei(provider, init_proposed.timestamp, ...)` — fetching the same stale prices.
   - Calls `within_margin(proposed, stale_reference, margin%)` — passes because proposed == stale_reference.
7. The proposal is accepted; the block is committed with stale L1 gas prices.
8. All transactions in the block pay fees based on the 30-minute-old L1 gas price, not the current one.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L260-284)
```rust
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

**File:** crates/apollo_l1_gas_price/src/l1_gas_price_provider.rs (L136-142)
```rust
        // Check if the prices are stale.
        if timestamp.0 > (*last_timestamp + self.config.max_time_gap_seconds) {
            return Err(L1GasPriceProviderError::StaleL1GasPricesError {
                current_timestamp: timestamp.0,
                last_valid_price_timestamp: *last_timestamp,
            });
        }
```

**File:** crates/apollo_consensus_orchestrator_config/src/config.rs (L248-261)
```rust
impl Default for ContextStaticConfig {
    fn default() -> Self {
        Self {
            proposal_buffer_size: 100,
            chain_id: ChainId::Mainnet,
            block_timestamp_window_seconds: 1,
            l1_da_mode: true,
            builder_address: ContractAddress::default(),
            validate_proposal_margin_millis: Duration::from_millis(10_000),
            build_proposal_time_ratio_for_retrospective_block_hash: 0.7,
            retrospective_block_hash_retry_interval_millis: Duration::from_millis(500),
            behavior_mode: BehaviorMode::default(),
        }
    }
```

**File:** crates/apollo_deployments/resources/app_configs/l1_gas_price_provider_config.json (L1-12)
```json
{
  "l1_gas_price_provider_config.eth_to_strk_oracle_config.lag_interval_seconds": 900,
  "l1_gas_price_provider_config.eth_to_strk_oracle_config.max_cache_size": 100,
  "l1_gas_price_provider_config.eth_to_strk_oracle_config.query_timeout_sec": 10,
  "l1_gas_price_provider_config.strk_to_usd_oracle_config.lag_interval_seconds": 900,
  "l1_gas_price_provider_config.strk_to_usd_oracle_config.max_cache_size": 100,
  "l1_gas_price_provider_config.strk_to_usd_oracle_config.query_timeout_sec": 10,
  "l1_gas_price_provider_config.lag_margin_seconds": 600,
  "l1_gas_price_provider_config.number_of_blocks_for_mean": 300,
  "l1_gas_price_provider_config.storage_limit": 3000,
  "l1_gas_price_provider_config.max_time_gap_seconds": 900
}
```
