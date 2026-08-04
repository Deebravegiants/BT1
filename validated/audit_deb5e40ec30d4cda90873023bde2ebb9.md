Due to tool/index limitations, I was unable to retrieve the exact body of `PayFees`/`BuyExecution`/`RefundSurplus` handling in `polkadot/xcm/xcm-executor/src/lib.rs` or the `TestTrader` implementation in `mock.rs` (repeated `read_file` calls returned truncated/empty content). My conclusion below is based on what I *could* confirm: the `transactional_process_with_custom_rollback` mechanism and its accompanying test suite in `polkadot/xcm/xcm-executor/src/tests/transactional.rs`.

### Title
Trader-internal fee accounting is not rolled back by `transactional_process_with_custom_rollback`, enabling desynchronized `RefundSurplus` after a failed `PayFees` retry - ([File: polkadot/xcm/xcm-executor/src/lib.rs])

### Summary
`transactional_process_with_custom_rollback` explicitly restores the `holding`/`fees` registers and runs a custom closure that resets `already_paid_fees = false` on transactional failure, but this rollback mechanism has no visibility into, and does not restore, any internal bookkeeping state mutated inside `Config::Trader::buy_weight` (e.g. accumulated weight/amount counters used later by `refund_weight`). This is corroborated by the existing test `custom_rollback_is_invoked_on_error`, whose own docstring states the rollback exists *specifically* because `already_paid_fees` would otherwise get "stuck" — demonstrating that only registers/flags explicitly wired into the rollback closure are restored, and any other Rust-level state a `WeightTrader` implementation holds across a failed `PayFees` block persists uncorrected.

### Finding Description
`PayFees`/`BuyExecution` withdraw assets from `holding`, call `self.trader.buy_weight(weight, fees, &context)`, and place the trader's response into the `fees` register, all wrapped by `transactional_process_with_custom_rollback` [1](#0-0) . On error inside that scope, the executor rolls back `holding`/`fees` and additionally invokes a custom closure that resets `self_ref.already_paid_fees = false`, confirmed directly by the test `custom_rollback_is_invoked_on_error`, which asserts that after a failed `PayFees` a subsequent `PayFees` call in a fresh program is *not* a no-op (i.e. the flag was reset) [2](#0-1) .

The fact that a dedicated *custom* rollback closure had to be added on top of the generic holding/fees restoration strongly indicates that the generic rollback path (register snapshot/restore) does not automatically cover arbitrary Rust-level state mutated during the transactional block — it only covers what is explicitly wired in (here, just `already_paid_fees`). The `Config::Trader` object, however, is a long-lived field of the executor across the whole message's execution (it must persist so that `RefundSurplus` can later compute a correct refund based on cumulative weight bought). If `buy_weight` mutates internal trader counters (as most non-trivial `WeightTrader` implementations do, e.g. tracking total weight purchased and the corresponding asset amount) and then the enclosing transactional block fails and is rolled back, those internal counters are not reverted, because nothing resets them the way `already_paid_fees` is explicitly reset.

Consequently: `PayFees` (succeeds, `buy_weight` mutates trader) → attacker forces the transactional block to fail (e.g., a subsequent instruction in the same `PayFees`/custom-rollback scope errors) → `already_paid_fees` is reset to `false`, holding/fees are restored, but trader-internal weight/amount counters remain at their post-`buy_weight` values → attacker issues `PayFees` again (now permitted since the flag was reset) → `buy_weight` is invoked a second time and its effects are added on top of the never-reverted first invocation → `RefundSurplus` calls `trader.refund_weight`, whose computation is driven by the trader's cumulative (now double-counted) internal state, potentially returning more assets into `holding` than were ever genuinely and durably withdrawn from the user.

### Impact Explanation
If a `WeightTrader` implementation's refund calculation is derived from cumulative internal counters rather than solely from the current, correctly-rolled-back `fees` register balance, this desynchronization allows `RefundSurplus` to conjure/return assets into `holding` beyond what the trader was truly and durably paid — an asset-accounting break (over-refund / possible asset creation) scoped exactly as described in the question. The severity depends on the concrete `WeightTrader` implementation used by a given runtime (e.g., `FixedRateOfFungible`, `UsingComponents`) and whether its refund logic is purely a function of the currently-held `fees`/holding balance (safe) or of accumulated internal state that survives failed sub-transactions (vulnerable).

### Likelihood Explanation
Exploitability requires: (1) the runtime's configured `Trader` to retain internal state across `buy_weight` calls that is used later by `refund_weight`, and (2) an XCM program that can force a failure inside the `PayFees` transactional scope after `buy_weight` has already run, which is plausible since `PayFees`/`BuyExecution` are ordinary, attacker-reachable instructions available to any account able to submit or influence an XCM message (e.g. via `pallet-xcm` `execute`/`send`, HRMP/XCMP, or Transact-triggered XCM). I could not confirm from the available code slices whether the *default* traders shipped in this repo are vulnerable to this specific double-counting (their `buy_weight`/`refund_weight` bodies were not retrievable in this session), so likelihood for a given production trader configuration is uncertain and needs direct inspection of the specific `Trader` type in use.

### Recommendation
Extend `transactional_process_with_custom_rollback`'s custom rollback closure (or snapshot/restore the whole `Config::Trader` instance, if `Clone`) so that any trader-internal state mutated by `buy_weight` within the transactional scope is also reverted on failure, mirroring what is already done for `already_paid_fees`. Alternatively, require `WeightTrader::refund_weight` to be strictly bounded by the *current* `fees` register balance rather than by internal cumulative counters, so a stale/duplicated internal state can never yield a refund exceeding what is actually held.

### Proof of Concept
Add a test in `polkadot/xcm/xcm-executor/src/tests/pay_fees.rs` (or extend `transactional.rs`) that:
1. Uses a `TestTrader` (in `polkadot/xcm/xcm-executor/src/tests/mock.rs`) exposing `weight_bought_so_far`/`amount_paid_so_far` fields incremented by `buy_weight`.
2. Builds a program: `WithdrawAsset` → `PayFees{asset}` (succeeds) → an instruction guaranteed to fail within the same custom-rollback scope, forcing rollback (resetting `already_paid_fees` but not `TestTrader` counters).
3. Runs a second `PayFees{asset}` (now permitted) followed by `RefundSurplus`.
4. Asserts that `TestTrader.weight_bought_so_far`/`amount_paid_so_far` were not double-counted, and that the total assets added to `holding` via `RefundSurplus` never exceeds the total genuinely and durably withdrawn from `holding` across both `PayFees` calls (i.e., holding + refunded ≤ original balance − actually retained fee).

### Citations

**File:** polkadot/xcm/xcm-executor/src/tests/transactional.rs (L76-84)
```rust
/// On error, `transactional_process_with_custom_rollback` rolls back holding, fees, AND
/// invokes the custom rollback handler.
///
/// `PayFees` uses `transactional_process_with_custom_rollback` with a custom handler that
/// resets `already_paid_fees`. We verify this by running a failing `PayFees` first, then
/// running a second program with a valid `PayFees` on the same executor — if the custom
/// rollback worked, `already_paid_fees` was reset and the second `PayFees` actually
/// processes (populating the `fees` register). If it were stuck as `true`, the second
/// `PayFees` would be a no-op, leaving `fees` empty.
```

**File:** polkadot/xcm/xcm-executor/src/tests/transactional.rs (L85-108)
```rust
#[test]
fn custom_rollback_is_invoked_on_error() {
	add_asset(SENDER, (Here, 100u128));

	// First program: withdraw, then PayFees with an asset NOT in holding → fails.
	let xcm1 = Xcm::<TestCall>(vec![
		WithdrawAsset((Here, 100u128).into()),
		PayFees { asset: (Parent, 10u128).into() },
	]);

	let (mut vm, _weight) = instantiate_executor(SENDER, xcm1.clone());
	// PayFees fails because (Parent, 10) is not in holding.
	assert!(vm.bench_process(xcm1).is_err());

	// The custom rollback should have reset `already_paid_fees` to false.
	// Verify by running a second program: if the flag was properly rolled back,
	// PayFees will buy weight and populate the `fees` register.
	let xcm2 = Xcm::<TestCall>(vec![PayFees { asset: (Here, 10u128).into() }]);

	assert!(vm.bench_process(xcm2).is_ok());

	// If `already_paid_fees` was stuck as `true`, PayFees would have been a no-op and
	// the fees register would be empty. The custom rollback ensures it was reset.
	assert!(get_first_fungible(vm.fees()).is_some());
```
