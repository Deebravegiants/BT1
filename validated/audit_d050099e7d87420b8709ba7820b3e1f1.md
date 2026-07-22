### Title
One-sided timestamp window in `is_proposal_init_valid` lets a proposer anchor L1 gas-price validation to a stale timestamp — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` enforces only an **upper** bound on `ProposalInit.timestamp` (`≤ now + window`). The **lower** bound is merely `≥ last_block_timestamp`, which can be arbitrarily far in the past. Because the validator then uses the **proposer-supplied** timestamp as the key for its own L1 gas-price oracle lookup, the margin check is anchored to the proposer's chosen timestamp rather than to the current time. A malicious proposer can therefore submit a proposal whose timestamp equals the previous block's timestamp, obtain old L1 gas prices that pass the margin check, and commit a block with stale (artificially low) L1 gas prices.

---

### Finding Description

**Asymmetric timestamp window in `is_proposal_init_valid`** [1](#0-0) 

The function reads `now` from the clock and then applies two checks:

| Check | Condition |
|---|---|
| Lower bound | `timestamp >= last_block_timestamp` |
| Upper bound | `timestamp <= now + block_timestamp_window_seconds` |

The config description for `block_timestamp_window_seconds` reads *"Maximum allowed deviation (seconds) of a proposed block's timestamp from the current time"*, implying a symmetric window `[now − window, now + window]`. The implementation only enforces the future half. [2](#0-1) 

The default value is **1 second**, so the upper bound is tight, but the lower bound is unbounded relative to `now`.

**Validator anchors its reference price to the proposer's timestamp**

After the timestamp check, `is_proposal_init_valid` calls: [3](#0-2) 

`get_l1_prices_in_fri_and_wei` is called with `init_proposed.timestamp` — the proposer-controlled value — as the lookup key. The validator's *reference* price is therefore derived from the same old timestamp, not from `now`.

**`get_price_info` returns historical prices for old timestamps without error** [4](#0-3) 

`get_price_info` only rejects timestamps that are **too far in the future** (`timestamp > last_scraped + max_time_gap`). For old timestamps it silently walks back through the ring buffer and returns the mean of the N L1 blocks ending at `timestamp − lag_margin`. There is no lower-bound staleness guard.

**Consequence:** proposer picks `T_old = last_block_timestamp`, looks up `P_old = prices(T_old)`, sends `ProposalInit{timestamp: T_old, l1_gas_price_*: P_old}`. Validator also calls `prices(T_old)` → gets the same `P_old` → `within_margin(P_old, P_old, ...)` is trivially true → proposal accepted with stale prices. [5](#0-4) 

The stale prices are then forwarded verbatim into `convert_to_sn_api_block_info` and committed as the block's canonical gas prices: [6](#0-5) 

---

### Impact Explanation

The committed `BlockInfo` carries the stale L1 gas prices. Every transaction in that block has its L1 fee component computed against those prices. If Ethereum gas prices have risen since `T_old`, users underpay for L1 data/execution costs, shifting the economic burden to the sequencer/protocol. This matches the impact category: *"Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact."*

---

### Likelihood Explanation

The proposer must be the designated BFT proposer for the round — a validator role. Byzantine validators are explicitly within the BFT threat model (the protocol tolerates up to `f < n/3` Byzantine nodes). No external unprivileged party is required; any single compromised or malicious validator that wins a proposer slot can trigger this. The window of exploitable staleness equals `now − last_block_timestamp`, which grows with block time and is unbounded during chain pauses.

---

### Recommendation

Add a symmetric lower-bound check in `is_proposal_init_valid`:

```rust
// existing upper-bound check
if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds {
    return Err(...);
}
// add symmetric lower-bound check
if now > proposal_init_validation.block_timestamp_window_seconds
    && init_proposed.timestamp < now - proposal_init_validation.block_timestamp_window_seconds
{
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "Timestamp is too old: now={}, block_timestamp_window_seconds={}, proposed={}",
            now,
            proposal_init_validation.block_timestamp_window_seconds,
            init_proposed.timestamp
        ),
    ));
}
```

This ensures the validator's L1 gas-price reference is always anchored to a timestamp within `±window` of the current time, making the margin check meaningful. The same fix should be applied to the `try_sync` path in `sequencer_consensus_context.rs`. [7](#0-6) 

---

### Proof of Concept

1. Validator set has `n` nodes; attacker controls one proposer slot at height `H`.
2. Previous block at `H-1` was committed with `timestamp = T_prev` (e.g., 10 seconds ago).
3. Current Ethereum gas price has spiked: `P_now >> P_prev`.
4. Attacker constructs `ProposalInit { height: H, timestamp: T_prev, l1_gas_price_*: prices(T_prev) }`.
5. Honest validators call `get_l1_prices_in_fri_and_wei(provider, T_prev, ...)` → receive `P_prev`.
6. `within_margin(P_prev, P_prev, margin)` → `true` for all four price fields.
7. `is_proposal_init_valid` returns `Ok(())`.
8. Block `H` is committed with `l1_gas_price = P_prev < P_now`.
9. All transactions in block `H` pay L1 fees computed at the stale `P_prev`, underpaying by `(P_now − P_prev) × data_bytes` per transaction.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L260-285)
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
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L322-328)
```rust
    let (l1_gas_prices_fri, l1_gas_prices_wei) = get_l1_prices_in_fri_and_wei(
        l1_gas_price_provider,
        init_proposed.timestamp,
        proposal_init_validation.previous_proposal_init.as_ref(),
        gas_price_params,
    )
    .await;
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

**File:** crates/apollo_consensus_orchestrator_config/src/config.rs (L160-161)
```rust
    /// Maximum allowed deviation (seconds) of a proposed block's timestamp from the current time.
    pub block_timestamp_window_seconds: u64,
```

**File:** crates/apollo_l1_gas_price/src/l1_gas_price_provider.rs (L136-155)
```rust
        // Check if the prices are stale.
        if timestamp.0 > (*last_timestamp + self.config.max_time_gap_seconds) {
            return Err(L1GasPriceProviderError::StaleL1GasPricesError {
                current_timestamp: timestamp.0,
                last_valid_price_timestamp: *last_timestamp,
            });
        }

        // This index is for the last block in the mean (inclusive).
        let index_last_timestamp_rev = samples.iter().rev().position(|data| {
            data.timestamp <= timestamp.saturating_sub(&self.config.lag_margin_seconds.as_secs())
        });

        // Could not find a block with the requested timestamp and lag.
        let Some(last_index_rev) = index_last_timestamp_rev else {
            return Err(L1GasPriceProviderError::MissingDataError {
                timestamp: timestamp.0,
                lag: self.config.lag_margin_seconds.as_secs(),
            });
        };
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1067-1081)
```rust
        if !(block_number == height
            && timestamp.0 >= last_block_timestamp
            && timestamp.0 <= now + self.config.static_config.block_timestamp_window_seconds)
        {
            warn!(
                "Invalid block info: expected block number {}, got {}, expected timestamp range \
                 [{}, {}], got {}",
                height,
                block_number,
                last_block_timestamp,
                now + self.config.static_config.block_timestamp_window_seconds,
                timestamp.0,
            );
            return false;
        }
```
