### Title
`l2_gas_price_wei` Derived from Unvalidated L1 Price Ratio Allows Proposer to Skew ETH-Denominated L2 Gas Fees and Block Hash — (`crates/apollo_consensus_orchestrator/src/utils.rs`)

---

### Summary

`l2_gas_price_wei` is absent from `ProposalInit` on the wire. It is silently derived inside `convert_to_sn_api_block_info` from the ratio `l1_gas_price_fri / l1_gas_price_wei`. `is_proposal_init_valid` validates each L1 price independently within a ±10 % margin but never validates the ratio or the derived `l2_gas_price_wei`. A proposer can therefore choose L1 prices at opposite extremes of the allowed margin to skew the implied ETH/STRK rate, producing a `l2_gas_price_wei` that deviates by up to ~18 % from the honest value. Because `l2_gas_price_wei` feeds both ETH-denominated fee collection and the `PartialBlockHashComponents.l2_gas_price.price_in_wei` field that enters the block hash, the result is incorrect fees and a wrong block hash that all validators accept.

---

### Finding Description

**Derivation path** — `convert_to_sn_api_block_info` (called by both proposer and validator via `initiate_build` / `initiate_validation`):

```rust
// crates/apollo_consensus_orchestrator/src/utils.rs  lines 318-328
let proposal_init_info = PreviousProposalInitInfo::from(init);
let eth_to_fri_rate = calculate_eth_to_fri_rate(&proposal_init_info)?;
// eth_to_fri_rate = l1_gas_price_fri * WEI_PER_ETH / l1_gas_price_wei

let l2_gas_price_wei =
    NonzeroGasPrice::new(init.l2_gas_price_fri.fri_to_wei(eth_to_fri_rate)?)?;
// l2_gas_price_wei = l2_gas_price_fri * l1_gas_price_wei / l1_gas_price_fri
``` [1](#0-0) 

**What is validated** — `is_proposal_init_valid` checks four L1 prices independently within `l1_gas_price_margin_percent` (10 %):

```rust
// crates/apollo_consensus_orchestrator/src/validate_proposal.rs  lines 342-353
if !(within_margin(l1_gas_price_fri_proposed, l1_gas_price_fri, ...)
  && within_margin(l1_data_gas_price_fri_proposed, ...)
  && within_margin(l1_gas_price_wei_proposed, ...)
  && within_margin(l1_data_gas_price_wei_proposed, ...))
``` [2](#0-1) 

`l2_gas_price_fri` is validated to be exactly equal to the local expected value:

```rust
// line 314
&& init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri
``` [3](#0-2) 

**What is never validated** — `l2_gas_price_wei` has no field in `ProposalInit` and no check in `is_proposal_init_valid`. [4](#0-3) 

**Block hash impact** — `PartialBlockHashComponents::new` copies `block_info.gas_prices.l2_gas_price_per_token()` which includes `price_in_wei`, and this feeds `calculate_block_hash`:

```rust
// crates/starknet_api/src/block_hash/block_hash_calculator.rs  lines 224-235
pub fn new(block_info: &BlockInfo, ...) -> Self {
    Self {
        l2_gas_price: block_info.gas_prices.l2_gas_price_per_token(),
        ...
    }
}
``` [5](#0-4) 

```rust
// lines 265-272
.chain_iter(gas_prices_to_hash(
    &partial_block_hash_components.l1_gas_price,
    &partial_block_hash_components.l1_data_gas_price,
    &partial_block_hash_components.l2_gas_price,   // ← includes price_in_wei
    &block_hash_version,
).iter())
``` [6](#0-5) 

---

### Impact Explanation

A malicious proposer sets:
- `l1_gas_price_fri` = reference × 1.10 (10 % above, passes `within_margin`)
- `l1_gas_price_wei` = reference × 0.90 (10 % below, passes `within_margin`)

Resulting `eth_to_fri_rate` = `1.10/0.90 × reference_rate` ≈ 1.22 × reference.

Resulting `l2_gas_price_wei` = `l2_gas_price_fri × 0.90/1.10` ≈ **0.818 × expected**.

Consequences:
1. **Incorrect fee (Critical)** — ETH-paying transactions (v1/v2) have their L2-gas component undercharged by ~18 %, reducing protocol revenue.
2. **Wrong block hash (Critical)** — `l2_gas_price.price_in_wei` enters the Poseidon block hash. Every validator recomputes the same manipulated value from the same `init`, so consensus agrees on a block hash that encodes a wrong gas price. This wrong hash propagates to `retrospective_block_hash` checks in future blocks and to L1 state commitments.

---

### Likelihood Explanation

In the current single-sequencer deployment the proposer is trusted. In the decentralized setting (the explicit design goal of this codebase) any validator can be elected proposer for a round. No special privilege beyond being a consensus participant is required. The manipulation is bounded (~18 %) but systematic and repeatable every block the attacker proposes.

---

### Recommendation

Add an explicit cross-check of the FRI/WEI ratio inside `is_proposal_init_valid`. Concretely, derive the expected `l2_gas_price_wei` from the validator's own trusted `eth_to_fri_rate` (computed from its own reference L1 prices) and verify the proposer's derived value is within the same margin:

```rust
// After computing l1_gas_prices_fri / l1_gas_prices_wei from the local oracle:
let local_eth_to_fri_rate = l1_gas_prices_fri.l1_gas_price.0
    .checked_mul(WEI_PER_ETH)? / l1_gas_prices_wei.l1_gas_price.0;
let expected_l2_gas_price_wei =
    init_proposed.l2_gas_price_fri.fri_to_wei(local_eth_to_fri_rate)?;
let proposed_l2_gas_price_wei =
    init_proposed.l2_gas_price_fri.fri_to_wei(
        calculate_eth_to_fri_rate(&PreviousProposalInitInfo::from(init_proposed))?
    )?;
require within_margin(proposed_l2_gas_price_wei, expected_l2_gas_price_wei, margin);
```

Alternatively, add `l2_gas_price_wei` as an explicit field in `ProposalInit` (mirroring the existing L1 WEI fields) and validate it directly.

---

### Proof of Concept

**Setup**: validator's oracle returns `l1_gas_price_fri = 1000`, `l1_gas_price_wei = 1`, `l2_gas_price_fri = 500` (exact match to `proposal_init_validation.l2_gas_price_fri`).

**Honest path**:
- `eth_to_fri_rate` = `1000 × 10^18 / 1` = `10^21`
- `l2_gas_price_wei` = `500 × 10^18 / 10^21` = `0.5` (rounds to 0 for small numbers; use larger values in practice)

**Attack**: proposer sends `l1_gas_price_fri = 1100`, `l1_gas_price_wei = 0.9` (both within 10 % margin):
1. `within_margin(1100, 1000, 10)` → `|1100-1000| = 100 ≤ 100` → **passes**
2. `within_margin(0.9, 1, 10)` → `|0.9-1| = 0.1 ≤ 0.1` → **passes**
3. `eth_to_fri_rate` = `1100 × 10^18 / 0.9` ≈ `1.222 × 10^21`
4. `l2_gas_price_wei` = `500 × 10^18 / 1.222×10^21` ≈ **0.409** (vs honest 0.5, an 18 % reduction)
5. All validators call `convert_to_sn_api_block_info(init)` with the same `init`, compute the same manipulated `l2_gas_price_wei`, execute transactions with undercharged ETH fees, and commit a block hash encoding `price_in_wei = 0.409` instead of `0.5`. [7](#0-6) [8](#0-7)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L318-328)
```rust
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
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L503-531)
```rust
fn calculate_eth_to_fri_rate(
    proposal_init_info: &PreviousProposalInitInfo,
) -> Result<u128, StarknetApiError> {
    let eth_to_fri_rate = proposal_init_info
        .l1_prices_fri
        .l1_gas_price
        .0
        .checked_mul(WEI_PER_ETH)
        .ok_or_else(|| {
            StarknetApiError::GasPriceConversionError(format!(
                "Gas price in Fri should be small enough to multiply by WEI_PER_ETH. Previous \
                 proposal init info: {:?}",
                proposal_init_info
            ))
        })?
        .checked_div(proposal_init_info.l1_prices_wei.l1_gas_price.0)
        .ok_or_else(|| {
            StarknetApiError::GasPriceConversionError(format!(
                "Gas price in Wei should be non-zero. Previous proposal init info: {:?}",
                proposal_init_info
            ))
        })?;
    if eth_to_fri_rate == 0 {
        return Err(StarknetApiError::GasPriceConversionError(format!(
            "Eth to fri rate is zero. Previous proposal init info: {:?}",
            proposal_init_info
        )));
    }
    Ok(eth_to_fri_rate)
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L312-314)
```rust
    if !(init_proposed.height == proposal_init_validation.height
        && init_proposed.l1_da_mode == proposal_init_validation.l1_da_mode
        && init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri)
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L342-353)
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
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L421-438)
```rust
/// Returns whether `proposed` is within `margin_percent` of the locally-trusted `reference`,
/// i.e. within the symmetric band `[reference*(1-m), reference*(1+m)]`.
///
/// The band is anchored to `reference` (the node's own L1 oracle read), not to the
/// proposer-supplied `proposed`: anchoring to `proposed` would let a malicious proposer scale the
/// band width with its own input and widen it in its favor.
fn within_margin(proposed: GasPrice, reference: GasPrice, margin_percent: u128) -> bool {
    // For small numbers (e.g., less than 10 wei, if margin is 10%), even an off-by-one
    // error might be bigger than the margin, even if it is just a rounding error.
    // We make an exception for such mismatch, and don't bother checking percentages
    // if the difference in price is only one wei.
    if proposed.0.abs_diff(reference.0) <= GAS_PRICE_ABS_DIFF_MARGIN {
        return true;
    }
    // Saturate: `reference.0 * margin_percent` can overflow u128 on large WEI prices.
    let margin = reference.0.saturating_mul(margin_percent) / 100;
    proposed.0.abs_diff(reference.0) <= margin
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L265-272)
```rust
            .chain_iter(
                gas_prices_to_hash(
                    &partial_block_hash_components.l1_gas_price,
                    &partial_block_hash_components.l1_data_gas_price,
                    &partial_block_hash_components.l2_gas_price,
                    &block_hash_version,
                )
                .iter(),
```
