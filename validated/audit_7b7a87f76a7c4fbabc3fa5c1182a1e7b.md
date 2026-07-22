### Title
Missing Zero-Value Check on `fee_proposal_fri` in `ProposalInit` Validation Allows Permanent SNIP-35 Fee Market Corruption — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` intentionally skips the `fee_proposal_fri` bounds check during the startup window (first `window_size` blocks, when `fee_actual` is `None`), but it never checks whether the supplied value is zero. A malicious proposer can inject `fee_proposal_fri = Some(GasPrice(0))` during this window; every validator accepts it, the zero is recorded into `fee_proposals_window`, and once the window fills with zeros `fee_proposal_bounds(0, margin)` collapses to `(0, 0)`, permanently locking the SNIP-35 fee market at zero and storing wrong `fee_proposal_fri` values in committed block headers.

---

### Finding Description

`is_proposal_init_valid` enforces two checks on `fee_proposal_fri`:

1. **Presence check** — `Some` is required for `starknet_version >= V0_14_3`.
2. **Bounds check** — the value must lie within `fee_proposal_bounds(fee_actual, margin)`.

The bounds check is guarded by:

```rust
// crates/apollo_consensus_orchestrator/src/validate_proposal.rs:396-416
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    ...
}
```

When `fee_actual` is `None` (startup window), the entire bounds check is skipped. There is no zero-value guard anywhere in the validation path for `fee_proposal_fri`. A `ProposalInit` carrying `fee_proposal_fri = Some(GasPrice(0))` passes all checks:

- `(Some(GasPrice(0)), true)` falls into the `_ => {}` arm of the presence match.
- The bounds check is skipped because `fee_actual` is `None`.

After acceptance, `finalize_decision` calls:

```rust
// crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs:518
self.record_fee_proposal(height, init.fee_proposal_fri);
```

which inserts `Some(GasPrice(0))` into `fee_proposals_window`. Once `window_size` consecutive zero entries accumulate, `compute_fee_actual` returns `Some(GasPrice(0))`. At that point:

```rust
// crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs:144-151
pub(crate) fn fee_proposal_bounds(fee_actual: GasPrice, margin_ppt: u128) -> (u128, u128) {
    ...
    let upper = u128::try_from(fee_actual_u256 * scaled / denom).unwrap_or(u128::MAX);
    let lower = u128::try_from(fee_actual_u256 * denom / scaled).unwrap_or(0);
    (lower, upper)  // → (0, 0) when fee_actual = 0
}
```

`fee_proposal_bounds(GasPrice(0), margin) = (0, 0)`. The validator now rejects any `fee_proposal_fri != 0`, and `compute_fee_proposal(fee_target, GasPrice(0), margin)` clamps to `GasPrice(0)` regardless of the oracle target. The SNIP-35 mechanism is permanently frozen at zero.

The zero value is also written into `BlockHeaderWithoutHash.fee_proposal_fri` and forwarded to state sync and the cende pipeline:

```rust
// crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs:409
fee_proposal_fri: init.fee_proposal_fri,  // = Some(GasPrice(0))
```

---

### Impact Explanation

**Wrong committed state**: `BlockHeaderWithoutHash.fee_proposal_fri = 0` is stored for every affected block, diverging from the honest proposer's value (`l2_gas_price`, which is non-zero).

**Incorrect fee / economic impact**: Once `fee_actual = 0`, `calculate_next_l2_gas_price_for_fin` computes `effective_min = max(config_min, 0) = config_min`, bypassing the SNIP-35 oracle-derived floor entirely. The L2 gas price reverts to pure EIP-1559 with `config_min` as the floor, ignoring the oracle target. All future `fee_proposal_fri` values are forced to zero, permanently disabling the SNIP-35 fee market.

**Wrong `ProposalCommitment`**: `proposal_commitment_from(partial, Some(GasPrice(0)))` = `Poseidon(partial.0, 0)` instead of `Poseidon(partial.0, l2_gas_price)`. The commitment that consensus signs over does not bind the correct fee signal.

---

### Likelihood Explanation

The attack window is the first `window_size` blocks of the chain (or after a restart/revert). In a decentralized consensus any validator can hold the proposer role; no special privilege beyond being a consensus participant is required. The effect is permanent: once the window fills with zeros, the self-reinforcing `(0, 0)` bounds trap prevents recovery without a chain restart or governance intervention.

---

### Recommendation

Add an explicit zero-value guard on `fee_proposal_fri` inside `is_proposal_init_valid`, applied unconditionally for V0_14_3+ blocks (before the bounds check):

```rust
// After the presence/version match, before the bounds check:
if let Some(fee_proposal) = init_proposed.fee_proposal_fri {
    if fee_proposal.0 == 0 {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "fee_proposal_fri must be non-zero for V0_14_3+, got 0 at version {}",
                init_proposed.starknet_version
            ),
        ));
    }
}
```

This mirrors the existing zero-rejection pattern used for L1/L2 gas prices in `convert_to_sn_api_block_info` via `NonzeroGasPrice::new`.

---

### Proof of Concept

1. Start the sequencer at height 0 with `starknet_version >= V0_14_3`.
2. As the proposer for the first `window_size` blocks, send `ProposalInit` with `fee_proposal_fri = Some(GasPrice(0))`.
3. `is_proposal_init_valid` accepts each proposal: presence check passes (`Some`), bounds check is skipped (`fee_actual = None`).
4. `record_fee_proposal(height, Some(GasPrice(0)))` inserts zero into `fee_proposals_window` for each block.
5. At height `window_size`, `compute_fee_actual` returns `Some(GasPrice(0))`.
6. `fee_proposal_bounds(GasPrice(0), margin) = (0, 0)`.
7. `compute_fee_proposal(fee_target, GasPrice(0), margin) = GasPrice(0)` regardless of oracle.
8. All future proposals must carry `fee_proposal_fri = 0`; any other value is rejected by validators.
9. SNIP-35 fee market is permanently frozen at zero; `BlockHeaderWithoutHash.fee_proposal_fri = 0` in all committed blocks. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L370-394)
```rust
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
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L396-416)
```rust
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
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L144-151)
```rust
pub(crate) fn fee_proposal_bounds(fee_actual: GasPrice, margin_ppt: u128) -> (u128, u128) {
    let denom = U256::from(PPT_DENOMINATOR);
    let scaled = denom + U256::from(margin_ppt);
    let fee_actual_u256 = U256::from(fee_actual.0);
    let upper = u128::try_from(fee_actual_u256 * scaled / denom).unwrap_or(u128::MAX);
    let lower = u128::try_from(fee_actual_u256 * denom / scaled).unwrap_or(0);
    (lower, upper)
}
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L163-171)
```rust
pub(crate) fn proposal_commitment_from(
    partial: PartialBlockHash,
    fee_proposal: Option<GasPrice>,
) -> ProposalCommitment {
    let Some(fee_proposal) = fee_proposal else {
        return ProposalCommitment(partial.0);
    };
    ProposalCommitment(Poseidon::hash_array(&[partial.0, Felt::from(fee_proposal.0)]))
}
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L308-310)
```rust
    fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
        self.fee_proposals_window.insert(height, fee_proposal_fri);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L399-412)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L517-518)
```rust
        self.update_l2_gas_price(height, l2_gas_used);
        self.record_fee_proposal(height, init.fee_proposal_fri);
```

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L72-76)
```rust
    let effective_min = match fee_actual {
        Some(fa) => GasPrice(max(config_min.0, fa.0)),
        None => config_min,
    };
    calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
```
