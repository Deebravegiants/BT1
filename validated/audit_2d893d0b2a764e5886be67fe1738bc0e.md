### Title
Double-counted weight/deposit budget in `CallResources::WeightDeposit` branch of `ethereum_execution::new_nested_meter` allows a single call frame to consume up to ~2x its allotted Ethereum gas budget - (File: substrate/frame/revive/src/metering/math.rs)

### Summary
In `ethereum_execution::new_nested_meter`, when a nested call requests `CallResources::WeightDeposit { weight, deposit_limit }`, the frame's weight limit and deposit limit are each independently derived from the *full* remaining gas budget (`weight_left`/`deposit_left`, each computed as "how much of this resource alone would exhaust `remaining_gas`"), rather than being jointly split so their combined gas-equivalent stays within `remaining_gas`. Only the frame's forward-looking `max_total_gas` (used for further nested sub-calls) is correctly re-capped via `remaining_gas.min(&gas_limit)`; the actual `WeightMeter`/deposit-`StorageMeter` limits handed to the frame (`nested_weight_limit`, `nested_deposit_limit`) are not reduced accordingly.

### Finding Description
Look at `substrate/frame/revive/src/metering/math.rs:401-419`: [1](#0-0) 

`weight_left` and `deposit_left` (computed at lines 332-363) are each sized such that, taken *alone*, consuming all of `weight_left` as weight, or all of `deposit_left` as deposit, would exactly exhaust `remaining_gas`: [2](#0-1) 

For the `WeightDeposit` request, `nested_weight_limit = weight_left.min(*weight)` and `nested_deposit_limit = deposit_left.min(*deposit_limit)`. An attacker crafting the sub-call request can set both `weight` and `deposit_limit` to (or above) `weight_left`/`deposit_left`, causing the frame to be granted **both** the maximal weight allowance **and** the maximal deposit allowance simultaneously — each independently equal to "all of remaining_gas converted into that one resource."

The code does compute a corrective `new_max_total_gas`/`gas_limit`/`nested_gas_limit` (lines 405-414), correctly capping the value via `remaining_gas.min(&gas_limit)`, and that corrected value is used only for `nested_max_total_gas` (the child's *own* gas ledger used when the child itself spawns further nested calls, line 423, 428). However, the concrete resource meters actually enforced during the child frame's own execution are constructed with the **uncorrected** `nested_weight_limit`/`nested_deposit_limit`: [3](#0-2) 

Because the `WeightMeter` and the storage-deposit meter are independent and unaware of each other's consumption, a frame that legitimately does real work mixing computation (consuming weight/ref_time/proof_size) and storage writes (consuming deposit) can consume close to `weight_left` weight **and** close to `deposit_left` deposit *within the same frame*, without either individual meter ever tripping `OutOfGas`/`StorageDepositLimitExhausted` (each meter's own limit is satisfied). When this consumption is later converted back to gas via `eth_tx_info.gas_consumption`/`total_consumed_gas` for accounting against the top-level `max_total_gas`, the resulting total gas-equivalent can be roughly `total_gas_consumption_before + remaining_gas (from weight) + remaining_gas (from deposit)`, i.e., up to ~2x the actually intended remaining budget — violating the stated invariant that "total consumed weight+deposit gas-equivalent must never exceed `max_total_gas`."

This contrasts with the `CallResources::Ethereum` handling in `substrate_execution::new_nested_meter` (lines 111-163), which explicitly computes a `ratio` to proportionally split the combined remaining gas between weight and deposit so the two resources cannot be double-granted. The `WeightDeposit` branch in `ethereum_execution::new_nested_meter` has no equivalent joint-splitting logic — it only "fixes" the forward-looking gas ledger, not the actual per-frame meters.

Note: I was unable to inspect `EthTxInfo::gas_consumption` / `EthTxInfo::weight_remaining` (defined in `substrate/frame/revive/src/metering/mod.rs`) or the call sites in `exec.rs` that use `total_consumed_gas`/`gas_left` after a frame returns, due to tool-call limits. It is possible (but unconfirmed) that a final post-execution check compares `total_consumed_gas` against the outer `max_total_gas` and reverts the whole transaction if exceeded — in which case the practical impact would be transaction failure/DoS rather than free execution, and this would need verification via test.

### Impact Explanation
If unmitigated, an attacker driving `eth_transact`/`eth_call` execution can craft nested `CallResources::WeightDeposit` requests to obtain a frame whose actual weight and storage-deposit allowances are each computed as if they alone could consume the entire remaining Ethereum gas budget. Genuine execution mixing compute and storage writes within that frame can then consume resources whose combined gas-equivalent exceeds the transaction's `max_total_gas`, i.e., potentially getting free/unpaid execution or storage growth beyond what the caller is billed/limited for — matching the scoped impact.

### Likelihood Explanation
Requires Ethereum execution mode (`TransactionLimits::Ethereum`) which is the default gas-metering mode for `eth_call`/`eth_transact`, an unprivileged path reachable by any signed account or contract making nested calls. The attacker fully controls the `CallResources::WeightDeposit` values via a contract making a sub-call with explicit weight/deposit gas parameters (Solidity-level call gas stipulation translated to `CallResources`), so crafting boundary values near `weight_left`/`deposit_left` is feasible without special privilege. The exact severity depends on whether a downstream, unverified final check catches the discrepancy, which introduces uncertainty about whether this manifests as free execution vs. a caught-and-reverted transaction.

### Recommendation
In the `CallResources::WeightDeposit` branch of `ethereum_execution::new_nested_meter`, jointly cap `nested_weight_limit` and `nested_deposit_limit` (e.g., via a proportional split analogous to the `ratio` computation used in `substrate_execution::new_nested_meter`'s `CallResources::Ethereum` branch) so that their combined gas-equivalent, as computed by `eth_tx_info.gas_consumption`, never exceeds `remaining_gas`, rather than only re-clamping the forward-looking `nested_max_total_gas`. Additionally, add an explicit assertion/test that after applying any `CallResources::WeightDeposit` request, `gas_consumption(total_consumed_weight_before + nested_weight_limit, total_consumed_deposit_before + StorageDeposit::Charge(nested_deposit_limit)) <= meter.max_total_gas`.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/metering/math.rs` (or a fuzz/invariant test):
1. Construct a root `TransactionMeter` via `ethereum_execution::new_root` with a fixed `eth_gas_limit`.
2. Call `ethereum_execution::new_nested_meter` with `CallResources::WeightDeposit { weight: <computed weight_left>, deposit_limit: <computed deposit_left> }` (both requesting the maximum available amount independently).
3. Simulate the child frame fully consuming both its `weight` limit (via `meter.weight`) and its `deposit_limit` (via `meter.deposit`) to their maxima.
4. Assert: `ethereum_execution::total_consumed_gas(&child_meter, &eth_tx_info) <= root_meter.max_total_gas` — expect this assertion to **fail**, demonstrating the total consumed gas-equivalent exceeds the transaction's `max_total_gas`.
5. Extend to a fuzz test with randomized nested `WeightDeposit` call trees comparing summed per-frame gas-equivalents against the top-level `max_total_gas`.

### Citations

**File:** substrate/frame/revive/src/metering/math.rs (L332-363)
```rust
		let weight_left = {
			let unbounded_weight_left = eth_tx_info
				.weight_remaining(
					&meter.max_total_gas,
					&total_consumed_weight,
					&total_consumed_deposit,
				)
				.ok_or(<Error<T>>::OutOfGas)?;

			unbounded_weight_left.min(
				meter
					.weight
					.weight_limit
					.checked_sub(&self_consumed_weight)
					.ok_or(<Error<T>>::OutOfGas)?,
			)
		};

		let deposit_left = {
			let Some(unbounded_deposit_left) = remaining_gas.to_adjusted_deposit_charge() else {
				return Err(<Error<T>>::OutOfGas.into());
			};

			match meter.deposit.limit {
				Some(deposit_limit) => unbounded_deposit_left.min(
					self_consumed_deposit
						.available(&deposit_limit)
						.ok_or(<Error<T>>::StorageDepositLimitExhausted)?,
				),
				None => unbounded_deposit_left,
			}
		};
```

**File:** substrate/frame/revive/src/metering/math.rs (L401-419)
```rust
				CallResources::WeightDeposit { weight, deposit_limit } => {
					let nested_weight_limit = weight_left.min(*weight);
					let nested_deposit_limit = deposit_left.min(*deposit_limit);

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
				},
```

**File:** substrate/frame/revive/src/metering/math.rs (L423-434)
```rust
		let nested_max_total_gas = total_gas_consumption.saturating_add(&nested_gas_limit);

		Ok(FrameMeter::<T> {
			weight: WeightMeter::new(nested_weight_limit, stipend),
			deposit: meter.deposit.nested(nested_deposit_limit),
			max_total_gas: nested_max_total_gas,
			total_consumed_weight_before: total_consumed_weight,
			total_consumed_deposit_before: total_consumed_deposit,
			transaction_limits: meter.transaction_limits.clone(),
			_phantom: PhantomData,
		})
	}
```
