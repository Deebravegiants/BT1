## Verdict: Valid vulnerability (residual, not fully fixed by the u64::MAX cap)

### Title
Gas-ratio starvation of nested calls under large `deposit_limit` is only partially fixed — non-maximal gas requests still round to ~0 weight - (File: `substrate/frame/revive/src/metering/math.rs`)

### Summary
`substrate_execution::new_nested_meter` computes a `FixedU128` ratio `gas_limit / remaining_gas` to proportionally split leftover weight/deposit to a nested EVM call. PR #10924 capped `remaining_gas` to `u64::MAX` to fix the case where a contract requests `gas: u64::MAX` (ratio collapses to `1.0`), but this cap does **not** fix the general case: when `deposit_left` is large (e.g. a caller sets `storage_deposit_limit` near `u128::MAX`, a common defensive pattern), `remaining_gas` is still forced to the huge constant `u64::MAX`, so *any* smaller, realistic `gas` request (e.g. `21000`, `100000`) still produces a near-zero ratio and starves the nested frame of weight, causing a spurious `OutOfGas` trap.

### Finding Description
In `substrate_execution::new_nested_meter` [1](#0-0) :

1. `deposit_left` is converted to a gas-equivalent via `SignedGas::from_adjusted_deposit_charge`, which scales linearly with the deposit amount [2](#0-1) . If `deposit_left` is large (e.g. a user sets `storage_deposit_limit` close to `u128::MAX`, which is a legal, unprivileged parameter of `pallet_revive::Call::call`/`instantiate` and requires no pre-reserved balance, only checked against actual charges as they accrue), `deposit_gas_left` becomes astronomically large (far beyond `u64::MAX`).
2. `remaining_gas` (`weight_gas_left + deposit_gas_left`) is capped to `u64::MAX` [3](#0-2) . This cap only fixes the exact edge case where the contract requests `gas == u64::MAX` (then `ratio = gas_limit/remaining_gas = 1`, as verified by the added regression test `substrate_nesting_with_large_deposit_and_max_gas_request` [4](#0-3) ).
3. For any smaller/realistic `gas` request (the vastly more common Solidity pattern of `.call{gas: <fixed amount>}(...)` rather than forwarding all gas), `ratio = gas_limit / u64::MAX` is still minuscule (e.g. `100000 / 1.8e19 ≈ 5.5e-15`). This ratio is then multiplied into `weight_left` [5](#0-4) , which truncates (`saturating_mul_int`) to effectively `0` weight for the nested frame even though `weight_left` in absolute terms is perfectly sufficient for the call.
4. This is reachable from an unprivileged, real extrinsic path: a signed `pallet_revive::Pallet::call`/`instantiate` (Substrate-native dispatch, which uses `TransactionLimits::WeightAndDeposit` → `substrate_execution::new_nested_meter`, as opposed to `eth_transact` which uses the separate, unaffected `ethereum_execution` module) targeting an EVM contract that internally performs a `CALL`/`STATICCALL`/`DELEGATECALL` opcode with an explicit, non-maximal gas value. That EVM opcode handling constructs `CallResources::from_ethereum_gas(gas_limit, add_stipend)` directly from the interpreter stack value [6](#0-5) , so any contract-supplied (or attacker-supplied, via calldata to a contract that forwards a caller-chosen gas amount) gas value triggers the vulnerable ratio path.
5. The regression test added for the original bug only asserts correctness at `gas = u64::MAX` and does not test smaller `gas` amounts, so this residual starvation is not covered by existing protections.

### Impact Explanation
A legitimate, unprivileged caller who sets a generous `storage_deposit_limit` (a very common practice to avoid unrelated deposit-related failures) and calls any contract that internally forwards a fixed, non-maximal gas amount to a sub-call (a standard Solidity pattern, e.g. safe-transfer callbacks, gas-limited reentrancy-guard calls, etc.) will have that nested call starved of weight and immediately trap with `OutOfGas`, regardless of how large a `weight_limit` is supplied for the overall extrinsic. This makes such contract calls "permanently un-executable" via the Substrate-native `call`/`instantiate` extrinsics whenever `deposit_limit` is large — matching the scoped impact in the question, just not limited to `gas == u64::MAX`.

### Likelihood Explanation
Highly feasible and repeatable: no special privileges are needed, only a normal signed extrinsic call to `pallet_revive::Pallet::call`/`instantiate` with a large `storage_deposit_limit` targeting a contract using typical explicit-gas sub-calls. It reproduces deterministically for any deposit_limit large enough to dominate `weight_gas_left`, which includes many realistic (not just `u128::MAX`) deposit-limit choices.

### Recommendation
Instead of capping `remaining_gas` to a fixed constant (`u64::MAX`), derive the cap from the *actual* convertible resources (e.g., only cap the portion of `deposit_gas_left`/`weight_gas_left` that would otherwise overflow the `u64` Ethereum gas representation used by `to_ethereum_gas`, and/or restructure the calculation so the ratio is computed against the true convertible gas capacity of the available weight/deposit rather than an artificial ceiling). Alternatively, avoid deriving nested weight via a fee-based gas ratio at all and directly bound `nested_weight_limit` by converting the requested `gas` to a weight amount (clamped by `weight_left`), rather than scaling `weight_left` by a fraction of an artificially capped total.

### Proof of Concept
Extend the existing regression test to iterate over multiple `(deposit_limit, weight_limit, gas)` combinations, generalizing `substrate_nesting_with_large_deposit_and_max_gas_request` [7](#0-6) :

```rust
#[test]
fn substrate_nesting_scales_with_requested_gas_under_large_deposit() {
    use super::math::substrate_execution;

    ExtBuilder::default()
        .with_next_fee_multiplier(FixedU128::from_rational(1, 5))
        .build()
        .execute_with(|| {
            let weight_limit = Weight::from_parts(1_000_000_000, 10_000);
            let deposit_limit: u128 = u128::MAX; // realistic "unlimited" deposit choice

            let root_meter =
                substrate_execution::new_root::<Test>(weight_limit, deposit_limit).unwrap();

            // A normal, non-maximal Ethereum gas request (e.g. 100_000, a typical
            // fixed-gas sub-call value used by Solidity contracts).
            let nested = root_meter
                .new_nested(&CallResources::Ethereum { gas: 100_000, add_stipend: false })
                .unwrap();

            let nested_weight_left = nested.weight_left().unwrap();

            // Assert the nested frame gets a *meaningful, non-negligible* share of
            // weight proportional to the request, not a value that truncates to ~0.
            assert!(
                nested_weight_left.ref_time() > 0,
                "nested frame starved of weight: got {:?} for gas=100_000 with deposit_limit=u128::MAX",
                nested_weight_left
            );
        });
}
```

Expected (buggy) result: `nested_weight_left.ref_time()` truncates to `0`, causing the assertion to fail and demonstrating that any subsequent execution in that nested frame will immediately trap with `Error::OutOfGas`.

### Citations

**File:** substrate/frame/revive/src/metering/math.rs (L111-141)
```rust
				CallResources::Ethereum { gas, add_stipend } => {
					// Convert leftover weight and deposit to an ethereum-gas equivalent,
					// then cap that gas by the requested `gas`. Distribute the capped gas
					// back into weight and deposit portions using the same ratio so that
					// the nested frame receives proportional limits.
					let weight_gas_left = SignedGas::<T>::from_weight_fee(
						T::FeeInfo::weight_to_fee_average(&weight_left),
					);
					let deposit_gas_left = SignedGas::<T>::from_adjusted_deposit_charge(
						&StorageDeposit::Charge(deposit_left),
					);
					let Some(remaining_gas) =
						(weight_gas_left.saturating_add(&deposit_gas_left)).to_ethereum_gas()
					else {
						return Err(<Error<T>>::OutOfGas.into());
					};

					// Cap to u64::MAX since Ethereum gas is u64. Without this, large deposit_left
					// (e.g., u128::MAX) causes ratio ≈ 0, giving nested calls almost no weight.
					let remaining_gas = remaining_gas.min(u64::MAX.saturated_into());

					let gas_limit = remaining_gas.min(*gas);

					let ratio = if remaining_gas.is_zero() {
						FixedU128::one()
					} else {
						FixedU128::from_rational(
							gas_limit.saturated_into(),
							remaining_gas.saturated_into(),
						)
					};
```

**File:** substrate/frame/revive/src/metering/math.rs (L143-146)
```rust
					let mut weight_limit = Weight::from_parts(
						ratio.saturating_mul_int(weight_left.ref_time()),
						ratio.saturating_mul_int(weight_left.proof_size()),
					);
```

**File:** substrate/frame/revive/src/metering/gas.rs (L67-79)
```rust
	/// Transform a storage deposit into a gas value. The value will be adjusted by dividing it
	/// through the next fee multiplier. Charges are treated as a positive numbers and refunds as
	/// negative numbers.
	pub fn from_adjusted_deposit_charge(deposit: &StorageDeposit<BalanceOf<T>>) -> Self {
		let multiplier = T::FeeInfo::next_fee_multiplier_reciprocal();

		match deposit {
			StorageDeposit::Charge(amount) => Positive(multiplier.saturating_mul_int(*amount)),
			StorageDeposit::Refund(amount) => {
				Self::safe_new_negative(multiplier.saturating_mul_int(*amount))
			},
		}
	}
```

**File:** substrate/frame/revive/src/metering/tests.rs (L1032-1061)
```rust
/// Regression test for proxy contract delegatecall with large deposit limits.
///
/// When deposit_left is very large (u128::MAX in production), remaining_gas becomes huge,
/// causing ratio = gas_limit / remaining_gas ≈ 0. This resulted in nested calls receiving
/// almost no weight. The fix caps remaining_gas to u64::MAX since Ethereum gas is u64.
#[test]
fn substrate_nesting_with_large_deposit_and_max_gas_request() {
	use super::math::substrate_execution;

	ExtBuilder::default()
		.with_next_fee_multiplier(FixedU128::from_rational(1, 5))
		.build()
		.execute_with(|| {
			let weight_limit = Weight::from_parts(1_000_000_000, 10_000);
			let deposit_limit: u128 = u64::MAX as _;

			let mut root_meter =
				substrate_execution::new_root::<Test>(weight_limit, deposit_limit).unwrap();

			root_meter.charge_weight_token(TestToken(1000, 100)).unwrap();
			root_meter.charge_deposit(&StorageDeposit::Charge(1000)).unwrap();

			let weight_left_before = root_meter.weight_left().unwrap();
			let nested = root_meter
				.new_nested(&CallResources::Ethereum { gas: u64::MAX as _, add_stipend: false })
				.unwrap();

			let nested_weight_left = nested.weight_left().unwrap();
			assert!(nested_weight_left.eq(&weight_left_before));
		});
```

**File:** substrate/frame/revive/src/vm/evm/instructions/contract.rs (L205-219)
```rust
	let call_result = match scheme {
		CallScheme::Call | CallScheme::StaticCall => interpreter.ext.call(
			&CallResources::from_ethereum_gas(gas_limit, add_stipend),
			&callee,
			value,
			input,
			// protect against rex-entrancy when we grant the stipend
			reentracy,
			scheme.is_static_call(),
		),
		CallScheme::DelegateCall => interpreter.ext.delegate_call(
			&CallResources::from_ethereum_gas(gas_limit, add_stipend),
			callee,
			input,
		),
```
