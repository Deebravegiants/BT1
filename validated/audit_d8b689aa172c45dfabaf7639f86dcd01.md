### Title
Integer-division truncation in `FixedRateOfFungible::buy_weight` allows underpriced XCM execution via instruction splitting - (File: polkadot/xcm/xcm-builder/src/weight.rs)

### Summary
`FixedRateOfFungible::buy_weight` computes the fee as two independent floor divisions (`units_per_second * ref_time / WEIGHT_REF_TIME_PER_SECOND` and `units_per_mb * proof_size / WEIGHT_PROOF_SIZE_PER_MB`) and returns the payment untouched whenever the result is `0`. Because `floor(a/b) + floor(c/b) ≤ floor((a+c)/b)` always holds and can be a strict inequality, splitting one `BuyExecution` of weight `W` into several smaller `BuyExecution` calls whose individual weights each fall below the per-call rounding threshold causes the aggregate charged fee to be strictly less than the fee that would be charged for a single call covering `W` — down to zero.

### Finding Description
The relevant logic is: [1](#0-0) 

`amount` is computed per invocation from the `weight` argument passed to that specific `buy_weight` call, with no state carried between calls to accumulate a fractional remainder (only `self.0`, the total *weight* bought, and `self.1`, the assets already taken, are tracked — not any leftover fractional fee). Consequently:

- For a single `buy_weight(W)` call, `amount = up*W.ref_time()/1e12 + upmb*W.proof_size()/mb`.
- For `N` calls each with weight `W/N` (assuming exact division of `W` for simplicity), `amount_i = up*(W.ref_time()/N)/1e12`. If `up*(W.ref_time()/N) < 1e12`, each `amount_i == 0`, hitting the free-pass branch at line 269-271, while the true single-call price for the same aggregate weight could be non-zero.
- Mathematically, `Σ floor(a_i/b) ≤ floor(Σa_i / b)`, so charging per-instruction can never overcharge relative to a single aggregate charge, but it can systematically undercharge whenever the split introduces per-call remainders that are individually discarded.

This is reachable by an unprivileged, signed origin: `pallet_xcm::execute` (or any XCM entry point that lets a user supply an arbitrary program, e.g. a crafted remote-execute/Transact XCM) permits constructing a program with many consecutive `BuyExecution`/`PayFees` instructions instead of one. Barriers such as `AllowTopLevelPaidExecutionFrom` only check that *some* `BuyExecution` exists near the top of the program and that the declared weight limit is sufficient — they do not validate that per-instruction fee rounding is fair across repeated `BuyExecution` calls.

### Impact Explanation
An attacker can pay strictly less than the mathematically correct fee for the aggregate weight consumed, i.e., systematically underpriced XCM execution / fee leakage from the chain's weight-pricing model, by structuring their program as many small `BuyExecution`/`PayFees` instructions rather than one large one. This does not directly steal funds from other users but breaks the "fee/weight logic must not be bypassable by normal users" invariant, letting execution happen for less than intended (in the extreme, for zero cost per truncated chunk).

### Likelihood Explanation
Exploitability depends heavily on the configured `units_per_second`/`units_per_mb` rate (a runtime/governance parameter) relative to typical per-instruction weight, and is bounded by:
- `M::get()` — the maximum number of instructions permitted in a single XCM program (`FixedWeightBounds`/`WeightInfoBounds` enforce `instructions_left`), which caps how many truncation-zero `BuyExecution` calls can be chained in one message;
- message byte-size limits on the transport queue (UMP/DMP/XCMP), which also cap instruction count;
- the executor's requirement that weight actually bought (`self.0`) must cover the weight of instructions subsequently executed, so an attacker cannot buy "0" weight and still execute unrelated arbitrarily-large-weight instructions without a later `BuyExecution`/`PayFees` covering them.

Because of these bounds, the achievable "free" aggregate weight is proportional to (rounding threshold × max instructions per message), not unbounded — so the severity is real but bounded/moderate rather than allowing arbitrarily large weight for zero cost in a single message. In production deployments, `units_per_second` is typically calibrated so this threshold is small relative to real instruction weights, further limiting practical impact, but the underlying accounting flaw is deterministic and reproducible whenever the rate/weight ratio permits per-call truncation to zero.

### Recommendation
Track and accumulate the fractional remainder of the fee calculation across `buy_weight` calls within the same `FixedRateOfFungible` instance (e.g., keep a running "owed but not yet charged" numerator and only truncate once at withdrawal, or perform the division once against `self.0.saturating_add(weight)` cumulative totals and charge the incremental difference each call) so that `Σ charged_i == floor(Σ weight_i * rate / denom)` regardless of how the weight is split across multiple `BuyExecution`/`PayFees` instructions.

### Proof of Concept
Rust unit test in `polkadot/xcm/xcm-builder/src/weight.rs` (or a new test module) using a mock `Get<(AssetId, u128, u128)>`:
1. Construct `FixedRateOfFungible` with `units_per_second = up`, `units_per_mb = 0`.
2. Compute `amount_single = buy_weight(Weight::from_parts(W, 0), payment_holding_with_enough_asset)` and record the charged amount.
3. Reset a fresh trader instance; call `buy_weight` `N` times with `Weight::from_parts(W/N, 0)` each, summing the charged amounts.
4. Assert `sum_split_charges < amount_single_charge` for `up`/`W`/`N` chosen such that `up*(W/N) < WEIGHT_REF_TIME_PER_SECOND ≤ up*W` (e.g., `up = 1_000`, `WEIGHT_REF_TIME_PER_SECOND = 1_000_000_000_000`, `W = 2_000_000_000`, `N = 10`), demonstrating `sum_split_charges == 0` while `amount_single_charge > 0`.
5. Fuzz over `up`, `W`, `N` to confirm `Σ charged_i ≤ amount_single_charge` always holds with strict inequality for a broad parameter range, violating the desired invariant "total fee for split calls must not be less than fee for the single call."

### Citations

**File:** polkadot/xcm/xcm-builder/src/weight.rs (L266-271)
```rust
		let amount = (units_per_second * (weight.ref_time() as u128) /
			(WEIGHT_REF_TIME_PER_SECOND as u128)) +
			(units_per_mb * (weight.proof_size() as u128) / (WEIGHT_PROOF_SIZE_PER_MB as u128));
		if amount == 0 {
			return Ok(payment);
		}
```
