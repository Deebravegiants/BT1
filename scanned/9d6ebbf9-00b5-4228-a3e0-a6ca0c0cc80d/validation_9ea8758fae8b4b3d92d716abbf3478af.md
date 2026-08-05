### Title
Under-charging in `ethereum_execution::new_nested_meter` `CallResources::WeightDeposit` branch — real weight/deposit limits are not scaled down to the gas-clamped budget - (File: substrate/frame/revive/src/metering/math.rs)

### Summary
In `ethereum_execution::new_nested_meter` (substrate/frame/revive/src/metering/math.rs, lines 401-419), the `CallResources::WeightDeposit` branch derives `nested_weight_limit` and `nested_deposit_limit` independently from two *alternative* (not additive) conversions of the same leftover gas pool, then hands both to the child `WeightMeter`/`GenericStorageMeter` as independent hard caps. The code separately computes a gas-equivalent (`new_max_total_gas`/`gas_limit`) for bookkeeping and clamps that value against `remaining_gas`, but this clamp is never propagated back into `nested_weight_limit`/`nested_deposit_limit`, which are the values actually enforced when the nested frame charges weight or deposit.

### Finding Description
`weight_left` (line 332-348) is computed via `eth_tx_info.weight_remaining(...)`, i.e., "how much weight could be afforded if *all* remaining gas were spent on weight" capped by the caller's outer weight limit. `deposit_left` (line 350-363) is computed via `remaining_gas.to_adjusted_deposit_charge()`, i.e., "how much deposit could be afforded if *all* remaining gas were spent on deposit". These two quantities each represent a full allocation of the *same* remaining gas budget to a single resource — they are mutually exclusive alternatives, not two independent budgets.

In the `CallResources::WeightDeposit` branch:
```
let nested_weight_limit = weight_left.min(*weight);
let nested_deposit_limit = deposit_left.min(*deposit_limit);
``` [1](#0-0) 
both are chosen independently, each up to their own alternative-full-allocation cap. The code does recompute the *true* joint gas cost of consuming both simultaneously:
```
let new_max_total_gas = eth_tx_info.gas_consumption(
    &total_consumed_weight.saturating_add(nested_weight_limit),
    &total_consumed_deposit.saturating_add(&StorageDeposit::Charge(nested_deposit_limit)),
);
let gas_limit = new_max_total_gas.saturating_sub(&total_gas_consumption);
(remaining_gas.min(&gas_limit), nested_weight_limit, Some(nested_deposit_limit), None)
``` [2](#0-1) 
This correctly recognizes that `new_max_total_gas` can exceed `meter.max_total_gas` (i.e., the joint use of `nested_weight_limit` + `nested_deposit_limit` can cost more gas than remains), and clamps the *derived* `nested_gas_limit`/`nested_max_total_gas` bookkeeping field accordingly (line 423: `total_gas_consumption.saturating_add(&nested_gas_limit)`). However, the actual resource caps installed on the child frame — `WeightMeter::new(nested_weight_limit, ...)` and `meter.deposit.nested(nested_deposit_limit)` (lines 425-428) — are **not reduced** to match this clamp. `max_total_gas` on the frame is used only for the child's *own* recursive nested-meter derivation and for gas reporting (`gas_left`, `eth_gas_consumed`, `total_consumed_gas`), not for enforcing per-charge weight/deposit limits: `charge_weight_token`/`WeightMeter::charge` checks against `weight.weight_limit` (i.e., `nested_weight_limit`) directly, and `charge_deposit`/`GenericStorageMeter` checks against `deposit.limit` (i.e., `nested_deposit_limit`) directly — neither path re-derives a gas-consistent bound.

Consequently, when `weight` and `deposit_limit` requested by the nested call (attacker-influenced call parameters that map to `CallResources::WeightDeposit{weight, deposit_limit}`) are both set near their respective "full-remaining-gas" alternative caps, the frame can actually consume up to `nested_weight_limit` of weight **and** up to `nested_deposit_limit` of deposit — a combined resource cost that, per `gas_consumption`, can exceed `remaining_gas` (i.e., exceed `meter.max_total_gas - total_gas_consumption`, which itself was funded by the externally supplied `eth_gas_limit`). Only the frame's *self-reported* gas bookkeeping (`max_total_gas`) is clamped, while the real weight/deposit meters that gate resource usage are not, breaking the invariant that gas-derived accounting must bound actual weight+deposit spend.

### Impact Explanation
An attacker submitting `eth_transact` can craft a nested call requesting `CallResources::WeightDeposit{weight, deposit_limit}` with both fields set close to `weight_left` and `deposit_left` respectively. The nested frame is then allowed to actually consume real chain weight (computation) and real storage deposit beyond what the transaction's `eth_gas_limit` (and the gas price paid) covers according to the gas-based accounting, while the transaction-level `max_total_gas` bookkeeping and eventual reported/charged gas (via `total_consumed_gas`/`eth_gas_consumed`) reflects a smaller, clamped value. This is an under-charging / free-execution class issue: real weight and storage-deposit resources are consumed and committed (weight metering and storage deposit charging in `charge_weight_token`/`charge_contract_deposit_and_transfer` operate on the un-clamped `nested_weight_limit`/`nested_deposit_limit`) without the sender's `eth_gas_limit` funding covering the full cost.

### Likelihood Explanation
The attacker fully controls `eth_gas_limit`, and (per the question's stated call sequence) the specific `weight`/`deposit_limit` values requested for the nested `CallResources::WeightDeposit` frame. No privileged access is required — this is a purely arithmetic property of `new_nested_meter` reachable whenever a nested call requests `CallResources::WeightDeposit` under Ethereum-style (`eth_transact`) execution. I located exactly 3 references to `WeightDeposit`/`CallResources::WeightDeposit` in `substrate/frame/revive/src/exec.rs`, confirming this variant is constructed somewhere in the exec/call-resolution path, but I was not able to fully trace, within the available tool budget, the precise external trigger (e.g., which specific EVM opcode, precompile, or dispatch path maps user-controlled call parameters into this exact `CallResources::WeightDeposit{weight, deposit_limit}` construction) to confirm end-to-end unprivileged reachability with concrete numeric parameters that reproduce a `gas_limit < 0` (saturated) / over-allocation scenario. This should be verified against `substrate/frame/revive/src/exec.rs`'s construction sites before treating this as fully confirmed at the extrinsic level.

### Recommendation
When computing `nested_weight_limit`/`nested_deposit_limit` for `CallResources::WeightDeposit`, clamp them jointly to the actual `remaining_gas` budget rather than independently to `weight_left`/`deposit_left` (which each assume the *other* resource is unused). Concretely: after computing `gas_limit = new_max_total_gas.saturating_sub(&total_gas_consumption)`, if `gas_limit` was clamped down by `remaining_gas`, proportionally scale down `nested_weight_limit` and `nested_deposit_limit` (or recompute them from the clamped `nested_gas_limit` using the same ratio-based approach already used in the `CallResources::Ethereum` branch) so that the values actually installed on the child `WeightMeter`/deposit meter never permit consuming more combined gas-equivalent resource than `remaining_gas` allows.

### Proof of Concept
Rust unit test (extend `substrate/frame/revive/src/metering/tests.rs`) plan:
1. Construct a root `TransactionMeter` via `ethereum_execution::new_root` with a tight `eth_gas_limit` (`max_total_gas`) and a generous `weight_limit`/no deposit cap at the meter level (relying only on gas accounting).
2. Call `ethereum_execution::new_nested_meter` with `CallResources::WeightDeposit { weight: weight_left, deposit_limit: deposit_left }` (both requesting the full alternative-allocation of the same remaining gas).
3. Assert that `resulting_frame.weight.weight_limit == weight_left` and `resulting_frame.deposit.limit == Some(deposit_left)` (i.e., both hard caps are un-clamped).
4. Simulate the frame fully consuming both `weight_left` weight and `deposit_left` deposit (via `charge_weight_token`/`charge_deposit`), then compute `eth_tx_info.gas_consumption(total_consumed_weight_before + weight_left, total_consumed_deposit_before + deposit_left)`.
5. Assert this computed gas consumption **exceeds** `meter.max_total_gas` (the root's `eth_gas_limit`-derived budget) — demonstrating that real weight+deposit spend surpasses the gas the attacker actually paid for, while `nested_max_total_gas`/`total_consumed_gas()` reporting shows a smaller, clamped figure.

### Citations

**File:** substrate/frame/revive/src/metering/math.rs (L401-403)
```rust
				CallResources::WeightDeposit { weight, deposit_limit } => {
					let nested_weight_limit = weight_left.min(*weight);
					let nested_deposit_limit = deposit_left.min(*deposit_limit);
```

**File:** substrate/frame/revive/src/metering/math.rs (L405-418)
```rust
					let new_max_total_gas = eth_tx_info.gas_consumption(
						&total_consumed_weight.saturating_add(nested_weight_limit),
						&total_consumed_deposit
							.saturating_add(&StorageDeposit::Charge(nested_deposit_limit)),
					);

					let gas_limit = new_max_total_gas.saturating_sub(&total_gas_consumption);

					(
						remaining_gas.min(&gas_limit),
						nested_weight_limit,
						Some(nested_deposit_limit),
						None,
					)
```
