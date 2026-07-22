### Title
Unconstrained `fee_proposal_fri` during startup window permanently corrupts fee market state - (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

In `is_proposal_init_valid`, the `fee_proposal_fri` bounds check is **entirely skipped** when `fee_actual` is `None`. `fee_actual` is `None` for the first `window_size` blocks (startup / near-genesis). A malicious proposer during that window can set `fee_proposal_fri` to any value — including `u128::MAX` — with no rejection. Those values are stored in `fee_proposals_window`, which is the sole input to `compute_fee_actual`. Once the window fills with corrupted entries, every subsequent block's `l2_gas_price` is derived from a poisoned median, causing incorrect fee accounting for all transactions from that point forward.

This is the direct sequencer analog of the external bug: just as `NormalStrategyLib` skips the `Gaussian.ppf` term at the bounds of `x`/`y` (leaving it at its zero initialization value instead of ±∞), the sequencer skips the `fee_proposal` margin check at the startup boundary, leaving the invariant (the fee market's sliding-window median) unconstrained.

---

### Finding Description

**Boundary condition — skipped check**

`is_proposal_init_valid` in `validate_proposal.rs` validates `fee_proposal_fri` in two steps:

1. **Presence check** (lines 371–394): rejects `None` for V0_14_3+ and `Some` for pre-V0_14_3.
2. **Bounds check** (lines 396–416): enforces that `fee_proposal` lies within a geometric margin of `fee_actual`.

The bounds check is guarded by a pattern match that requires **both** `fee_actual` and `fee_proposal` to be `Some`:

```rust
// During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    ...
}
``` [1](#0-0) 

`fee_actual` is computed by `compute_fee_actual`, which returns `None` whenever the sliding window does not yet contain `window_size` complete entries:

```rust
let Some(start) = height.0.checked_sub(window_size) else {
    warn!("Cannot compute fee_actual for height {height}: height is below window_size ({window_size})");
    return None;
};
``` [2](#0-1) 

It also returns `None` if any entry in the window is itself `None` (pre-V0_14_3 blocks):

```rust
Some(None) | None => {
    warn!("Cannot compute fee_actual for height {height}: ...");
    return None;
}
``` [3](#0-2) 

So for the first `window_size` blocks after genesis (or after a protocol upgrade from pre-V0_14_3), `fee_actual` is always `None`, and the bounds check is always skipped. A proposer can set `fee_proposal_fri = Some(GasPrice(u128::MAX))` and the validator will accept it.

**Corruption propagates into storage**

Every accepted `fee_proposal_fri` is recorded in the in-memory window:

```rust
fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
    self.fee_proposals_window.insert(height, fee_proposal_fri);
}
``` [4](#0-3) 

On restart, the window is re-populated from `state_sync` storage, which reads `fee_proposal_fri` from committed block headers:

```rust
self.record_fee_proposal(
    block_number,
    block.block_header_without_hash.fee_proposal_fri,
)
``` [5](#0-4) 

The corrupted values therefore survive node restarts.

**Corrupted window drives `l2_gas_price`**

Once the window fills, `compute_fee_actual` returns the median of the corrupted entries. `calculate_next_l2_gas_price_for_fin` uses `fee_actual` as a floor for `l2_gas_price`: [6](#0-5) 

Both proposer and validator derive the same corrupted `l2_gas_price` from the same corrupted window, so proposals with the inflated price pass the `l2_gas_price_fri` check in `is_proposal_init_valid` (lines 312–321). The corrupted price is then embedded in every subsequent `ProposalInit` and used for all fee calculations.

---

### Impact Explanation

**Incorrect fee / gas accounting with economic impact.**

If a malicious proposer sets `fee_proposal_fri = u128::MAX` for all `window_size` startup blocks, the median `fee_actual` becomes `u128::MAX`. The `l2_gas_price` is then set to `u128::MAX`. Every subsequent transaction's fee check computes `max_price_per_unit * gas_used` against `u128::MAX`, causing:

- All transactions whose `max_price_per_unit < u128::MAX` to fail pre-validation fee checks, effectively halting the network.
- Alternatively, if the attacker sets a large but not maximal value, they can inflate fees to extract economic rent from all users.

The corruption is **persistent** (stored in block headers) and **self-reinforcing** (each new block's `l2_gas_price` is derived from the corrupted window, and that price is recorded as the next block's `fee_proposal`).

---

### Likelihood Explanation

The startup window spans the first `window_size` blocks after genesis or after a V0_14_3 protocol upgrade. In a Tendermint-based consensus, the proposer role rotates among validators. Any validator that is scheduled to propose during the startup window can exploit this without any special privilege. The window is a fixed, predictable interval, making the attack window known in advance.

---

### Recommendation

1. **Enforce a fallback bound when `fee_actual` is `None`.** When the window is incomplete, the validator should still reject `fee_proposal_fri` values that deviate significantly from the local `l2_gas_price` (the same fallback the honest proposer uses). For example:

```rust
let reference = match proposal_init_validation.fee_actual {
    Some(fa) => fa,
    None => proposal_init_validation.l2_gas_price_fri, // honest proposer's fallback
};
// enforce bounds against `reference` unconditionally
```

2. **Alternatively**, during the startup window, require `fee_proposal_fri == l2_gas_price_fri` exactly (since both proposer and validator use the same fallback), rather than allowing any value.

3. Add a test that verifies the validator rejects an out-of-range `fee_proposal_fri` when `fee_actual` is `None`.

---

### Proof of Concept

```
1. Network starts at height 0 (or upgrades to V0_14_3).
   fee_proposals_window is empty → compute_fee_actual returns None for all heights < window_size.

2. Malicious proposer is scheduled to propose block 0.
   It sets ProposalInit.fee_proposal_fri = Some(GasPrice(u128::MAX)).

3. Validator calls is_proposal_init_valid:
   - fee_proposal_required = true (V0_14_3+) → presence check passes (Some is present).
   - proposal_init_validation.fee_actual = None → bounds check is SKIPPED.
   - Proposal is accepted.

4. decision_reached records fee_proposal_fri = u128::MAX for height 0 in fee_proposals_window.

5. Repeat for heights 1 .. window_size - 1 (attacker controls or colludes with proposers).

6. At height = window_size, compute_fee_actual returns median(u128::MAX, ...) = u128::MAX.

7. calculate_next_l2_gas_price_for_fin sets l2_gas_price = u128::MAX.

8. All subsequent ProposalInit messages carry l2_gas_price_fri = u128::MAX.
   All transactions fail fee pre-validation (max_price_per_unit < u128::MAX).
   Network is halted or fees are permanently inflated.
```

### Citations

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

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L61-67)
```rust
    let Some(start) = height.0.checked_sub(window_size) else {
        warn!(
            "Cannot compute fee_actual for height {height}: height is below window_size \
             ({window_size})"
        );
        return None;
    };
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L73-79)
```rust
            Some(None) | None => {
                warn!(
                    "Cannot compute fee_actual for height {height}: fee_proposals_window has no \
                     recorded fee_proposal for height {source_height}"
                );
                return None;
            }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L308-310)
```rust
    fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
        self.fee_proposals_window.insert(height, fee_proposal_fri);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L338-341)
```rust
                Ok(block) => self.record_fee_proposal(
                    block_number,
                    block.block_header_without_hash.fee_proposal_fri,
                ),
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L425-441)
```rust
    /// Returns the next L2 gas price without mutating context. Used when building the fin and when
    /// updating at decision time.
    fn calculate_next_l2_gas_price(&self, height: BlockNumber, l2_gas_used: GasAmount) -> GasPrice {
        let fee_actual = compute_fee_actual(
            &self.fee_proposals_window,
            height,
            VersionedConstants::latest_constants().fee_proposal_window_size,
        );
        calculate_next_l2_gas_price_for_fin(
            self.l2_gas_price,
            height,
            l2_gas_used,
            self.config.dynamic_config.override_l2_gas_price_fri,
            &self.config.dynamic_config.min_l2_gas_price_per_height,
            fee_actual,
        )
    }
```
