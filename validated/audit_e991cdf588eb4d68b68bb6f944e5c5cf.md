### Title
Modexp precompile gas cost is derived from a generic EVM-gas-per-second conversion factor instead of a real benchmark, allowing charged weight to systematically underestimate actual big-integer computation cost - ([File: substrate/frame/revive/src/precompiles/builtin/modexp.rs])

### Summary
The `Modexp<T>` precompile computes a Solidity/EIP-2565 "gas" number from input lengths and then converts it to `Weight` using a hard-coded constant `WEIGHT_PER_GAS` derived from an average, opcode-agnostic assumption ("~40M EVM-gas/sec on compiled WASM"), rather than from an actual FRAME benchmark of the `num-bigint` `modpow` computation performed by this precompile. Every other CPU-heavy precompile in the same file (`Bn128Pairing`, `Bn128Add/Mul`, `Blake2F`) is charged via `T::WeightInfo::*`, i.e. a value produced by the `#[benchmark]` macro that measures actual wall-clock execution time of the specific computation on reference hardware — `Modexp` is not.

### Finding Description
`Modexp::call` reads attacker-controlled `base_len`/`exp_len`/`mod_len` (bounded to 1024 bytes each) and computes an EIP-2565 gas cost via `calculate_gas_cost`, then charges it with: [1](#0-0) 

That gas value is converted to `Weight` in `RuntimeCosts::weight`: [2](#0-1) 

using the constant: [3](#0-2) 

This `WEIGHT_PER_GAS` is explicitly documented as an *approximation of average EVM gas/sec for generic EVM execution over compiled WASM* — a number meant to characterize typical opcode-level EVM interpretation cost, not the cost of an arbitrary-precision modular-exponentiation big-integer routine. By contrast, `Bn128Pairing`, `Bn128Add`, `Bn128Mul`, and `Blake2F` are charged through `T::WeightInfo::bn128_pairing(n)` / `bn128_add()` / `bn128_mul()` / `blake2f(n)`, each of which is populated by an actual `#[benchmark]` function in `benchmarking.rs` that runs the real computation (e.g. `pairing_batch`) and records measured execution time on the reference machine: [4](#0-3) 

There is no equivalent `#[benchmark] fn modexp(...)` in `benchmarking.rs` for the Modexp precompile (confirmed absent by search), and no `T::WeightInfo::modexp(...)` entry in the `WeightInfo` trait. Instead, the only "validation" test is `test_long_exp_gas_cost_matches_specs`, which asserts that the charged weight matches the **EIP-2565 gas formula times a hard-coded constant** — i.e. it only checks internal consistency of the formula-to-weight conversion, never that the conversion tracks the real Rust `BigUint::modpow` execution time on the reference hardware: [5](#0-4) 

The EIP-2565 gas formula itself was calibrated by Ethereum's authors against go-ethereum's Go `big.Int` implementation running on specific reference machines to characterize *that* library's asymptotic and constant-factor behavior. Substrate's `Modexp` uses the general-purpose `num-bigint` crate's `modpow`, which has different internal algorithms/constant factors (windowed exponentiation, Barrett/Montgomery reduction choices, allocation patterns) than Go's implementation. Multiplying the EIP-2565 gas number by a generic "EVM-gas-to-weight" ratio (`WEIGHT_PER_GAS`, itself derived from an average over *all* EVM opcodes, not from big-integer arithmetic) provides no rigorous upper bound on the wall-clock cost of `num_bigint::BigUint::modpow` for near-maximal 1024-byte base/exponent/modulus values. Because the multiplication/iteration-count formula and the constant conversion factor were never validated against a real benchmark of this specific code path, there is no evidence — and structurally no mechanism — ensuring the charged weight is an upper bound of the actual CPU cost for adversarially chosen large inputs (e.g. maximal 1024-byte odd modulus, exponent crafted to maximize `iteration_count`, and repeated calls within a single block to accumulate CPU time while nominally staying within the declared weight budget).

### Impact Explanation
If the real cost of `num_bigint::BigUint::modpow` for worst-case 1024-byte operands exceeds what `gas_cost * WEIGHT_PER_GAS` charges, an unprivileged contract caller can invoke the precompile (address `0x5`) repeatedly with near-maximal, adversarially crafted inputs within a block's weight budget while the node actually spends more wall-clock CPU time than budgeted. This degrades block production/import throughput — a weight-metering-bypass DoS vector, matching the scoped impact (gas-cost/complexity mismatch DoS via block production stall), without requiring any privileged access: any signed account can deploy a trivial contract that `call`s the precompile address directly.

### Likelihood Explanation
Preconditions are trivially met: any account can deploy or call a contract, and the precompile call data length limits (1024 bytes per field) are attacker-controllable within the specified bound — no additional permission or state setup is required. The `Modexp` precompile is reachable via a standard contract `call` to address `0x5` (`BuiltinAddressMatcher::Fixed(0x5)`), which is a normal, unprivileged, user-triggered code path. The gap is structural (no calibrated benchmark exists for this specific code path, only a formula-consistency test), so the likelihood of a real underestimate existing for some worst-case input in the 1024-byte space is plausible, though the exact magnitude of any discrepancy (and whether it is severe enough to matter in absolute terms, since MIN_GAS_COST and the quadratic term already provide some margin) is not established in the code, since no actual benchmark data comparing measured wall-clock time to charged weight is present in the repository for this precompile.

### Recommendation
Add a dedicated FRAME `#[benchmark]` for `Modexp` (analogous to `bn128_pairing`) that exercises worst-case `base_len`/`exp_len`/`mod_len` combinations (including maximal 1024-byte odd/even moduli and adversarial exponent bit patterns) and derive `T::WeightInfo::modexp(...)` from measured wall-clock execution time on the reference hardware, replacing the generic `WEIGHT_PER_GAS` conversion. Cross-check that the resulting weight-per-input-length curve is a genuine upper bound over the full 1024-byte input space (fuzz across base/exp/mod length combinations), and add a regression test asserting `measured_time <= charged_weight` with a safety margin, not merely that charged weight matches the EIP-2565 gas formula.

### Proof of Concept
Add a Rust benchmark/test in `substrate/frame/revive/src/precompiles/builtin/modexp.rs` (or `benchmarking.rs`) that:
1. Constructs worst-case inputs: `base_len = exp_len = mod_len = 1024`, modulus even (to trigger the `*20` multiplier) and odd (baseline), with the exponent's highest bit set to maximize `iteration_count`.
2. Measures wall-clock time of `Modexp::<T>::call(...)` on the reference benchmarking hardware using `frame_benchmarking`'s timing harness (as done for `bn128_pairing`), and converts the measured time to `Weight`.
3. Compares `measured_weight` against `Token::<T>::weight(&RuntimeCosts::Modexp(calculated_gas_cost))` — the weight actually charged.
4. Asserts `measured_weight <= charged_weight` (with the standard benchmarking safety margin), across a sweep of `(base_len, exp_len, mod_len)` combinations up to 1024 bytes each and both even/odd moduli.
5. If the assertion fails for any input combination, it demonstrates that `WEIGHT_PER_GAS` under-charges relative to actual `num_bigint::modpow` cost, confirming the mismatch as a concrete, reproducible discrepancy rather than a purely theoretical concern.

### Citations

**File:** substrate/frame/revive/src/precompiles/builtin/modexp.rs (L119-128)
```rust
			// do our gas accounting
			let gas_cost = calculate_gas_cost(
				base_len as u64,
				mod_len as u64,
				&exponent,
				&exp_buf,
				modulus.is_even(),
			);

			env.frame_meter_mut().charge_weight_token(RuntimeCosts::Modexp(gas_cost))?;
```

**File:** substrate/frame/revive/src/precompiles/builtin/modexp.rs (L367-399)
```rust
	#[test]
	fn test_long_exp_gas_cost_matches_specs() {
		use crate::{call_builder::CallSetup, metering::Token, tests::ExtBuilder};

		let input = vec![
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			16, 0, 0, 0, 255, 255, 255, 2, 0, 0, 179, 0, 0, 2, 0, 0, 122, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 255, 251, 0, 0, 0, 0, 4, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 255, 255, 255, 2, 0, 0, 179, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255,
			255, 255, 255, 249,
		];

		ExtBuilder::default().build().execute_with(|| {
			let mut call_setup = CallSetup::<Test>::default();
			let (mut ext, _) = call_setup.ext();

			let before = ext.frame_meter().weight_consumed();
			<Modexp<Test>>::call(&<Modexp<Test>>::MATCHER.base_address(), input, &mut ext).unwrap();
			let after = ext.frame_meter().weight_consumed();

			// 7104 * 20 gas used when ran in geth (x20)
			assert_eq!(after - before, Token::<Test>::weight(&RuntimeCosts::Modexp(7104 * 20)));
		})
	}
```

**File:** substrate/frame/revive/src/vm/runtime_costs.rs (L28-37)
```rust
/// Current approximation of the gas/s consumption considering
/// EVM execution over compiled WASM (on 4.4Ghz CPU).
/// Given the 2000ms Weight, from which 75% only are used for transactions,
/// the total EVM execution gas limit is: GAS_PER_SECOND * 2 * 0.75 ~= 60_000_000.
const GAS_PER_SECOND: u64 = 40_000_000;

/// Approximate ratio of the amount of Weight per Gas.
/// u64 works for approximations because Weight is a very small unit compared to
/// gas.
const WEIGHT_PER_GAS: u64 = WEIGHT_REF_TIME_PER_SECOND / GAS_PER_SECOND;
```

**File:** substrate/frame/revive/src/vm/runtime_costs.rs (L381-381)
```rust
			Modexp(gas) => Weight::from_parts(gas.saturating_mul(WEIGHT_PER_GAS), 0),
```

**File:** substrate/frame/revive/src/benchmarking.rs (L2877-2923)
```rust
	#[benchmark(pov_mode = Measured)]
	fn bn128_pairing(n: Linear<0, { 20 }>) {
		fn generate_random_ecpairs(n: usize) -> Vec<u8> {
			use bn::{AffineG1, AffineG2, Fr, G1, G2, Group};
			use rand::SeedableRng;
			use rand_pcg::Pcg64;
			let mut rng = Pcg64::seed_from_u64(1);

			let mut buffer = vec![0u8; n * 192];

			let mut write = |element: &bn::Fq, offset: &mut usize| {
				element.to_big_endian(&mut buffer[*offset..*offset + 32]).unwrap();
				*offset += 32
			};

			for i in 0..n {
				let mut offset = i * 192;
				let scalar = Fr::random(&mut rng);

				let g1 = G1::one() * scalar;
				let g2 = G2::one() * scalar;
				let a = AffineG1::from_jacobian(g1).expect("G1 point should be on curve");
				let b = AffineG2::from_jacobian(g2).expect("G2 point should be on curve");

				write(&a.x(), &mut offset);
				write(&a.y(), &mut offset);
				write(&b.x().imaginary(), &mut offset);
				write(&b.x().real(), &mut offset);
				write(&b.y().imaginary(), &mut offset);
				write(&b.y().real(), &mut offset);
			}

			buffer
		}

		let input = generate_random_ecpairs(n as usize);
		let mut call_setup = CallSetup::<T>::default();
		let (mut ext, _) = call_setup.ext();

		let result;
		#[block]
		{
			result =
				run_builtin_precompile(&mut ext, H160::from_low_u64_be(8).as_fixed_bytes(), input);
		}
		assert_ok!(result);
	}
```
