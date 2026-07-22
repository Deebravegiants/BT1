### Title
Zero `fee_proposal_fri` Accepted During Startup Window Poisons `fee_actual` to Zero, Permanently Locking Fee Proposals — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` skips the `fee_proposal_fri` bounds check whenever `fee_actual` is `None` (the first `window_size` blocks). A malicious proposer can set `fee_proposal_fri = Some(GasPrice(0))` in `ProposalInit`, which passes all validation. Once enough zero entries fill `fee_proposals_window`, `compute_fee_actual` returns `GasPrice(0)`. At that point `fee_proposal_bounds(GasPrice(0), margin_ppt)` returns `(0, 0)`, so any honest proposer who submits a non-zero `fee_proposal_fri` is permanently rejected by every validator. The fee mechanism is irreversibly locked to zero.

---

### Finding Description

**Step 1 — Zero passes the startup-window validation.**

`is_proposal_init_valid` enforces that `fee_proposal_fri` is `Some` for V0_14_3+ blocks, but the bounds check is guarded by `fee_actual`:

```rust
// validate_proposal.rs L396-416
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    let (lower_bound, upper_bound) = fee_proposal_bounds(
        fee_actual,
        VersionedConstants::latest_constants().fee_proposal_margin_ppt,
    );
    if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
        return Err(ValidateProposalError::InvalidProposalInit(...));
    }
}
```

`fee_actual` is `None` for the first `window_size` blocks (the `if let` short-circuits), so `fee_proposal_fri = Some(GasPrice(0))` passes with no minimum check. [1](#0-0) 

**Step 2 — Zero is recorded in the sliding window.**

After a proposal is accepted, `decision_reached` calls `record_fee_proposal(height, init.fee_proposal_fri)`, inserting `Some(GasPrice(0))` into `fee_proposals_window`. [2](#0-1) 

**Step 3 — `compute_fee_actual` treats `Some(GasPrice(0))` as a valid price.**

`compute_fee_actual` returns `None` only when an entry is `None` (pre-V0_14_3) or missing. `Some(GasPrice(0))` is pushed into the median window normally:

```rust
// dynamic_gas_price/mod.rs L70-80
match fee_proposals_window.get(&source_height) {
    Some(Some(price)) => window.push(*price),   // GasPrice(0) is pushed here
    Some(None) | None => { return None; }
}
``` [3](#0-2) 

**Step 4 — `fee_proposal_bounds(GasPrice(0), margin_ppt)` returns `(0, 0)`.**

Once the median of the window is zero, `fee_actual = GasPrice(0)`. The bounds function:

```rust
// dynamic_gas_price/mod.rs L144-151
let upper = u128::try_from(fee_actual_u256 * scaled / denom).unwrap_or(u128::MAX);
// 0 * scaled / denom = 0
let lower = u128::try_from(fee_actual_u256 * denom / scaled).unwrap_or(0);
// 0 * denom / scaled = 0
```

returns `(lower=0, upper=0)`. [4](#0-3) 

**Step 5 — Every non-zero `fee_proposal_fri` is permanently rejected.**

With `lower_bound = 0` and `upper_bound = 0`, the check `fee_proposal.0 > upper_bound` is `true` for any `fee_proposal_fri ≥ 1`. Every honest proposer is rejected with `InvalidProposalInit`. The only accepted value is `fee_proposal_fri = 0`, which is also what `fee_proposal_bounds` will keep returning forever. [5](#0-4) 

An honest proposer's `compute_proposer_fee_proposal` always returns at least `l2_gas_price` (≥ `min_gas_price`), so it can never produce a zero proposal — meaning honest proposers are permanently blocked from having their proposals accepted. [6](#0-5) 

---

### Impact Explanation

**Incorrect fee/gas price with economic impact.** Once the window is poisoned, `fee_actual = 0` propagates into `calculate_next_l2_gas_price_for_fin` as a floor of zero, collapsing the SNIP-35 fee market. Transactions are processed at the bare EIP-1559 minimum (`min_gas_price`), not the oracle-derived market rate. Validators lose fee revenue and the fee-market invariant — that `fee_actual` tracks real STRK/USD cost — is permanently broken. Additionally, `proposal_commitment_from(partial, Some(GasPrice(0)))` produces a different commitment hash than any non-zero fee would, so the commitment bound to consensus signatures encodes a corrupted fee signal. [7](#0-6) 

---

### Likelihood Explanation

The attack requires a consensus proposer role. During the startup window of `window_size` blocks (default 10), a malicious proposer who controls more than half the proposals can set the median to zero. In a single-sequencer deployment this is trivially achievable. In a multi-validator BFT deployment, a coalition controlling >50% of startup-round proposals achieves the same effect. The startup window is a one-time, unrepeatable opportunity — once the window is poisoned and `fee_actual = 0` is established, the lock is self-reinforcing with no recovery path in the current code. [8](#0-7) 

---

### Recommendation

Add an absolute minimum check for `fee_proposal_fri` inside `is_proposal_init_valid`, applied unconditionally (not gated on `fee_actual`):

```rust
// After the Some/None presence check, before the bounds check:
if let Some(fee_proposal) = init_proposed.fee_proposal_fri {
    let min_fee = VersionedConstants::latest_constants().min_gas_price;
    if fee_proposal < min_fee {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!("fee_proposal_fri {fee_proposal} is below minimum {min_fee}"),
        ));
    }
}
```

This mirrors the fix in the external report (adding `minVoterPercent = 10%`): enforce a non-zero floor unconditionally so that the startup-window bypass cannot inject zeros into the sliding window. [9](#0-8) 

---

### Proof of Concept

```
Height 0..window_size (startup, fee_actual = None):
  Malicious proposer sends ProposalInit {
      starknet_version: V0_14_3,
      fee_proposal_fri: Some(GasPrice(0)),   // passes: Some(_) check OK
      ...                                     // bounds check: skipped (fee_actual=None)
  }
  → is_proposal_init_valid returns Ok(())
  → decision_reached records fee_proposals_window[h] = Some(GasPrice(0))

Height window_size (fee_actual now computed):
  compute_fee_actual([0,0,...,0]) = GasPrice(0)
  fee_proposal_bounds(GasPrice(0), margin_ppt) = (lower=0, upper=0)

Height window_size + 1 (honest proposer):
  Honest proposer sends fee_proposal_fri = Some(GasPrice(8_000_000_000))
  Validator check: 8_000_000_000 > upper_bound (0) → true
  → InvalidProposalInit("Fee proposal out of bounds: fee_actual=0, fee_proposal=8000000000, allowed range=[0, 0]")
  → Proposal rejected permanently
```

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L370-419)
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

    Ok(())
}
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L308-310)
```rust
    fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
        self.fee_proposals_window.insert(height, fee_proposal_fri);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L478-482)
```rust
        let Some(fee_actual) = fee_actual else {
            warn!("fee_actual unavailable, freezing fee_proposal at l2_gas_price");
            SNIP35_FEE_PROPOSAL_FRI.set_lossy(self.l2_gas_price.0);
            return self.l2_gas_price;
        };
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L56-92)
```rust
pub fn compute_fee_actual(
    fee_proposals_window: &BTreeMap<BlockNumber, Option<GasPrice>>,
    height: BlockNumber,
    window_size: u64,
) -> Option<GasPrice> {
    let Some(start) = height.0.checked_sub(window_size) else {
        warn!(
            "Cannot compute fee_actual for height {height}: height is below window_size \
             ({window_size})"
        );
        return None;
    };
    let window_size_usize = usize::try_from(window_size).expect("window_size fits in usize");
    let mut window = Vec::with_capacity(window_size_usize);
    for source_height in (start..height.0).map(BlockNumber) {
        match fee_proposals_window.get(&source_height) {
            Some(Some(price)) => window.push(*price),
            Some(None) | None => {
                warn!(
                    "Cannot compute fee_actual for height {height}: fee_proposals_window has no \
                     recorded fee_proposal for height {source_height}"
                );
                return None;
            }
        }
    }
    window.sort();
    let mid = window_size_usize / 2;
    let median = if window_size_usize.is_multiple_of(2) {
        // Even: average of the two middle values, rounded down.
        // Overflow-safe averaging: a + (b - a) / 2 (safe because sorted, so b >= a).
        GasPrice(window[mid - 1].0 + (window[mid].0 - window[mid - 1].0) / 2)
    } else {
        window[mid]
    };
    Some(median)
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
