### Title
Stale `effective_weight_limit` after `bank_pending_storage_changes` deposit charge allows weight to be spent past the true Ethereum gas budget - (File: substrate/frame/revive/src/metering/mod.rs)

### Summary
`FrameMeter::bank_pending_storage_changes` records a new storage deposit charge via `RawMeter::bank_pending_changes` -> `RawMeter::charge_deposit` -> `record_charge`, which increases `total_deposit`, but unlike its sibling methods it never calls `adjust_effective_weight_limit()` afterward. In `TransactionLimits::EthereumGas` mode, `effective_weight_limit` is a function of both weight and deposit consumption, so any deposit charge that is not followed by a re-adjustment leaves `WeightMeter::effective_weight_limit` stale (too high), letting a subsequent `charge_weight_token`/`WeightMeter::charge` accept weight that the real remaining eth-gas budget would not allow.

### Finding Description
In `substrate/frame/revive/src/metering/mod.rs`, deposit-mutating APIs are expected to re-derive `effective_weight_limit` immediately afterward because `adjust_effective_weight_limit` is documented as needing to be "called whenever there is a change in the deposit meter" [1](#0-0) . Both `charge_deposit` and `record_contract_storage_changes` / `charge_contract_deposit_and_transfer` correctly follow this pattern, calling `self.adjust_effective_weight_limit()` right after mutating `self.deposit` [2](#0-1) .

However, `bank_pending_storage_changes` does not:
```
pub fn bank_pending_storage_changes(
	&mut self,
	contract: T::AccountId,
	info: &mut ContractInfo<T>,
) {
	self.deposit.bank_pending_changes(contract, info);
}
``` [3](#0-2) 

`RawMeter::bank_pending_changes` (in `storage.rs`) applies the pending diff to `ContractInfo` and, if the resulting deposit is non-zero, calls `self.charge_deposit(contract, deposit)`, which internally calls `record_charge(&amount)` and increases `total_deposit` [4](#0-3) . This is the exact call used to commit a parent frame's pending storage changes before entering a same-contract reentrant nested call (per the doc-comment referencing contract-issues#213) [5](#0-4) .

Since `total_deposit` increases but `WeightMeter::effective_weight_limit` is not recomputed, `WeightMeter::charge` continues to check `new_consumed.any_gt(self.effective_weight_limit)` against the old (larger) `effective_weight_limit` [6](#0-5) . In Ethereum gas mode, `effective_weight_limit` should reflect `weight_consumed + weight_left()`, where `weight_left()` is derived from the combined gas/weight/deposit accounting via `math::ethereum_execution::weight_left` [7](#0-6) . Skipping the re-adjustment means subsequent `charge_weight_token` calls (which call `self.weight.charge(token)` directly, bypassing any deposit-triggered recompute) can succeed while the true remaining eth-gas-derived weight budget has already been exhausted by the deposit charge [8](#0-7) .

### Impact Explanation
In Ethereum execution mode, a contract call sequence that triggers a same-contract reentrant call (which invokes `bank_pending_storage_changes` to commit the parent frame's pending storage diff before spawning the nested frame) followed by weight-consuming host calls can let the transaction consume more weight than its `max_total_gas`-derived budget permits, because the weight ceiling used by `WeightMeter::charge` was never lowered to reflect the additional deposit consumed. This is a bypass of the shared gas/weight/storage limit enforced by the `ResourceMeter` in Ethereum gas mode, as scoped.

### Likelihood Explanation
This requires an unprivileged contract caller to trigger a call path that performs same-contract reentrancy (a contract calling back into itself), causing `bank_pending_storage_changes` to run mid-execution while operating under `TransactionLimits::EthereumGas`. This is a normal, attacker-reachable contract execution pattern (self-reentrant calls are commonly exercised, e.g. regression tests `same_contract_reentry_does_not_double_count_storage` and `transitive_reentry_does_not_double_count_storage` in `metering/tests.rs` exercise exactly this call path) [9](#0-8) . No privileged or governance action is required; it is reproducible deterministically by any account able to deploy and call a self-reentrant contract.

### Recommendation
Add a call to `self.adjust_effective_weight_limit()?` inside `FrameMeter::bank_pending_storage_changes` immediately after `self.deposit.bank_pending_changes(...)`, mirroring `charge_contract_deposit_and_transfer` and `record_contract_storage_changes`, and propagate the `DispatchResult` (changing the function signature accordingly) so failures (e.g. `OutOfGas`) are surfaced to callers.

### Proof of Concept
Add a unit test in `substrate/frame/revive/src/metering/tests.rs` that:
1. Creates a `TransactionMeter` with `TransactionLimits::EthereumGas` with a small `eth_gas_limit`.
2. Creates a nested `FrameMeter`, records a storage `Diff` via `record_contract_storage_changes` to build up pending own-contribution.
3. Calls `apply_pending_storage_changes`/`bank_pending_storage_changes` directly (simulating same-contract reentry) to bank the deposit without an explicit `adjust_effective_weight_limit` call.
4. Immediately calls `charge_weight_token` with a token sized to be just within the *old* `effective_weight_limit` but that would exceed the correctly recomputed `weight_left()` after the deposit charge.
5. Assert the charge succeeds (demonstrating the bug) and then assert `eth_gas_consumed_signed()` translated to `BalanceOf<T>` exceeds `max_total_gas`/`eth_gas_limit`, proving the transaction consumed more resource than its Ethereum gas budget allowed.

### Citations

**File:** substrate/frame/revive/src/metering/mod.rs (L284-290)
```rust
	#[inline]
	pub fn charge_weight_token<Tok: Token<T>>(
		&mut self,
		token: Tok,
	) -> Result<ChargedAmount, DispatchError> {
		self.weight.charge(token)
	}
```

**File:** substrate/frame/revive/src/metering/mod.rs (L381-390)
```rust
	pub fn weight_left(&self) -> Option<Weight> {
		match &self.transaction_limits {
			TransactionLimits::EthereumGas { eth_tx_info, .. } => {
				math::ethereum_execution::weight_left(self, eth_tx_info)
			},
			TransactionLimits::WeightAndDeposit { .. } => {
				math::substrate_execution::weight_left(self)
			},
		}
	}
```

**File:** substrate/frame/revive/src/metering/mod.rs (L498-515)
```rust
	/// Determine and set the new effective weight limit of the weight meter.
	///
	/// This function needs to be called whenever there is a change in the deposit meter. It is a
	/// function of `ResourceMeter` instead of `WeightMeter` because its outcome also depends on the
	/// consumed storage deposits.
	fn adjust_effective_weight_limit(&mut self) -> DispatchResult {
		if matches!(self.transaction_limits, TransactionLimits::WeightAndDeposit { .. }) {
			return Ok(());
		}

		if let Some(weight_left) = self.weight_left() {
			let new_effective_limit = self.weight.weight_consumed().saturating_add(weight_left);
			self.weight.set_effective_weight_limit(new_effective_limit);
			Ok(())
		} else {
			Err(<Error<T>>::OutOfGas.into())
		}
	}
```

**File:** substrate/frame/revive/src/metering/mod.rs (L611-650)
```rust
	pub fn charge_contract_deposit_and_transfer(
		&mut self,
		contract: T::AccountId,
		amount: DepositOf<T>,
	) -> DispatchResult {
		log::trace!(
			target: LOG_TARGET,
			"Charge deposit and transfer: \
				amount={:?}, \
				deposit_left={:?}, \
				deposit_consumed={:?}, \
				max_charged={:?}",
			amount,
			self.deposit_left(),
			self.deposit_consumed(),
			self.deposit.max_charged(),
		);

		self.deposit.charge_deposit(contract, amount);
		self.adjust_effective_weight_limit()
	}

	/// Record storage changes of a contract.
	pub fn record_contract_storage_changes(&mut self, diff: &Diff) -> DispatchResult {
		log::trace!(
			target: LOG_TARGET,
			"Charge contract storage: \
				diff={:?}, \
				deposit_left={:?}, \
				deposit_consumed={:?}, \
				max_charged={:?}",
			diff,
			self.deposit_left(),
			self.deposit_consumed(),
			self.deposit.max_charged(),
		);

		self.deposit.charge(diff);
		self.adjust_effective_weight_limit()
	}
```

**File:** substrate/frame/revive/src/metering/mod.rs (L665-675)
```rust
	/// Apply pending storage changes to a ContractInfo without finalizing the meter.
	///
	/// This is used before creating a nested frame to ensure the child frame can see
	/// the parent's pending storage changes when calculating refunds. This fixes the issue
	/// where storage deposit refunds fail in subframes because the parent's pending
	/// charges haven't been committed to ContractInfo yet.
	///
	/// See: <https://github.com/paritytech/contract-issues/issues/213>
	pub fn apply_pending_storage_changes(&self, info: &mut ContractInfo<T>) {
		self.deposit.apply_pending_changes_to_contract(info);
	}
```

**File:** substrate/frame/revive/src/metering/mod.rs (L677-684)
```rust
	/// See [`storage::RawMeter::bank_pending_changes`].
	pub fn bank_pending_storage_changes(
		&mut self,
		contract: T::AccountId,
		info: &mut ContractInfo<T>,
	) {
		self.deposit.bank_pending_changes(contract, info);
	}
```

**File:** substrate/frame/revive/src/metering/storage.rs (L512-528)
```rust
	/// Apply the pending diff to `info` and push its deposit as a final charge, then reset
	/// `own_contribution` so finalize does not apply it a second time.
	pub fn bank_pending_changes(&mut self, contract: T::AccountId, info: &mut ContractInfo<T>) {
		if let Contribution::Alive(_) = &self.own_contribution {
			let deposit = self.own_contribution.update_contract(Some(info));
			self.own_contribution = Contribution::Alive(Default::default());
			if !deposit.is_zero() {
				self.charge_deposit(contract, deposit);
			}
		} else {
			debug_assert!(
				false,
				"on-stack ancestor frames have not finalized yet, so own_contribution \
				 should be Alive when banked; qed",
			);
		}
	}
```

**File:** substrate/frame/revive/src/metering/weight.rs (L187-207)
```rust
	#[inline]
	pub fn charge<Tok: Token<T>>(&mut self, token: Tok) -> Result<ChargedAmount, DispatchError> {
		#[cfg(test)]
		{
			// Unconditionally add the token to the storage.
			let erased_tok =
				ErasedToken { description: format!("{:?}", token), token: Box::new(token) };
			self.tokens.push(erased_tok);
		}

		let amount = token.weight();
		// It is OK to not charge anything on failure because we always charge _before_ we perform
		// any action
		let new_consumed = self.weight_consumed.saturating_add(amount);
		if new_consumed.any_gt(self.effective_weight_limit) {
			return Err(<Error<T>>::OutOfGas.into());
		}

		self.weight_consumed = new_consumed;
		Ok(ChargedAmount(amount))
	}
```

**File:** substrate/frame/revive/src/metering/tests.rs (L166-224)
```rust
/// Direct same-contract reentry (X -> X): a write, a self-reenter, then another write
/// must not double-count the pre-reentry write in the persisted `ContractInfo`. The
/// reentrant run must match a non-reentrant baseline exactly (both persisted accounting
/// and the net deposit charged to the origin). Regression repro for contract-issues#213.
#[test_case(FixtureType::Solc   ; "solc")]
#[test_case(FixtureType::Resolc ; "resolc")]
fn same_contract_reentry_does_not_double_count_storage(fixture_type: FixtureType) {
	let (code, _) = compile_module_with_type("ReentryStorage", fixture_type).unwrap();

	ExtBuilder::default().build().execute_with(|| {
		let _ = <Test as Config>::Currency::set_balance(&ALICE, 100_000_000_000);

		// Baseline: two writes, no reentry.
		let Contract { addr: baseline_addr, .. } =
			builder::bare_instantiate(Code::Upload(code.clone()))
				.salt(Some([1; 32]))
				.build_and_unwrap_contract();
		let baseline = builder::bare_call(baseline_addr)
			.data(ReentryStorage::writeTwiceCall {}.abi_encode())
			.build();
		let baseline_info = AccountInfo::<Test>::load_contract(&baseline_addr).unwrap();

		// Reentrant: write, reenter self (an empty frame), write. Same end state.
		let Contract { addr: reentrant_addr, .. } = builder::bare_instantiate(Code::Upload(code))
			.salt(Some([2; 32]))
			.build_and_unwrap_contract();
		let reentrant = builder::bare_call(reentrant_addr)
			.data(ReentryStorage::writeReenterWriteCall {}.abi_encode())
			.build();
		let reentrant_info = AccountInfo::<Test>::load_contract(&reentrant_addr).unwrap();

		assert!(baseline.result.is_ok(), "baseline call failed: {:?}", baseline.result);
		assert!(reentrant.result.is_ok(), "reentrant call failed: {:?}", reentrant.result);

		// Without the bank-pending-changes fix the pre-reentry write is applied to the
		// persisted ContractInfo twice, inflating every storage field and over-charging
		// the origin. Assert the full set so a partial regression still fails.
		assert_eq!(
			reentrant_info.storage_items, baseline_info.storage_items,
			"storage_items inflated by double-applied pending diff under same-contract reentry",
		);
		assert_eq!(
			reentrant_info.storage_bytes, baseline_info.storage_bytes,
			"storage_bytes inflated under same-contract reentry",
		);
		assert_eq!(
			reentrant_info.storage_item_deposit, baseline_info.storage_item_deposit,
			"storage_item_deposit inflated under same-contract reentry",
		);
		assert_eq!(
			reentrant_info.storage_byte_deposit, baseline_info.storage_byte_deposit,
			"storage_byte_deposit inflated under same-contract reentry",
		);
		assert_eq!(
			reentrant.storage_deposit, baseline.storage_deposit,
			"net storage deposit charged to origin inflated under same-contract reentry",
		);
	});
}
```
