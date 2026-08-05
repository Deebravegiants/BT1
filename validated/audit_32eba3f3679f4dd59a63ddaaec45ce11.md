Audit Report

## Title
Deferred termination-sweep in `Ext::charge` drains a redeployed contract's balance/ED to the terminated contract's beneficiary - ([File: substrate/frame/contracts/src/storage/meter.rs])

## Summary
`RawMeter::try_into_deposit` defers all balance transfers — refunds, deposit charges, and the termination "sweep remaining balance to beneficiary" — until the entire call stack for an extrinsic completes, and processes all `Refund` charges before all `Charge` charges. Because `terminate()` in `substrate/frame/contracts/src/exec.rs` removes `ContractInfoOf` synchronously (line 1372) while only queuing the balance sweep as a deferred meter charge (`meter.rs:465-476`), a contract terminated and then re-instantiated at the same deterministic address within the same call stack allows the new contract's endowment/ED to be swept to the old contract's beneficiary when the deferred charge finally executes.

## Finding Description
`RawMeter::terminate` only records a deferred charge (`Contribution::Terminated { deposit: Deposit::Refund(...), beneficiary }`) rather than moving balance immediately: [1](#0-0) 

Meanwhile, `Frame::terminate` in `exec.rs` removes the `ContractInfoOf` entry for the account synchronously and immediately, before returning control to the rest of the call stack: [2](#0-1) 

Since the address for a new contract is a deterministic function of `(deployer, code_hash, input_data, salt)`, and `ContractInfo::new` only rejects duplicate deployment if `ContractInfoOf::<T>::contains_key(account)` is true, a subsequent `instantiate` at the same account id — reachable within the same call stack once the prior entry has been removed — passes this check and proceeds: [3](#0-2) 

`charge_instantiate` then immediately (not deferred) transfers the existential deposit into the account and increments its consumer count: [4](#0-3) 

Finally, `try_into_deposit` processes all queued `Refund` charges (including the old contract's `Terminated` sweep) before any `Charge` charges, once for the entire call stack: [5](#0-4) 

The `Refund`/`Terminated` branch of `ReservingExt::charge` sweeps whatever `reducible_balance` currently sits in the account — identified only by account id, with no verification that it still belongs to the terminated instance — to the beneficiary, and decrements consumers: [6](#0-5) 

Because the new contract's ED (and any further value transferred into it during its constructor, which runs before the root meter's `try_into_deposit`) has already landed in that same account by the time this deferred sweep runs, the sweep captures and drains the new contract's balance to the old beneficiary — an account id collision that the meter's charge-processing has no mechanism to detect or scope against.

## Impact Explanation
This breaks the invariant that a live contract's held balance corresponds to its own endowment/storage deposit. An attacker who terminates a contract and redeploys a new one at the same deterministic address within the same call stack can redirect the new contract's ED/value to an attacker-controlled beneficiary, while `System::inc_consumers`/`dec_consumers` bookkeeping also becomes inconsistent (new instantiate calls `inc_consumers`, then the stale terminated-charge calls `dec_consumers` for the same account). This is a concrete fund-extraction / accounting-corruption bug in the storage-deposit meter, matching an in-scope funds-loss impact for `pallet-contracts`.

## Likelihood Explanation
The exploit path requires only unprivileged, signed contract-call actions: instantiate a contract with a known salt, terminate it via `seal_terminate` with an attacker-chosen beneficiary, then within the same top-level call/extrinsic instantiate a new contract at the identical deterministic address (same deployer/code_hash/input_data/salt) before the call stack returns and `try_into_deposit` runs. All primitives — deterministic address derivation, synchronous `ContractInfoOf` removal on terminate, and deferred refund-then-charge batching in the meter — are present and reachable in the code cited above, making this feasible and repeatable by any account capable of deploying/calling contracts.

## Recommendation
Scope the termination beneficiary sweep and consumer bookkeeping strictly to the balance/state that existed for the specific terminated contract instance, not to whatever balance is present in the account at meter finalization time. Perform the sweep and `dec_consumers` synchronously within `terminate()` (as pallet-revive's `do_terminate` already does via an immediate `Self::transfer`), or otherwise disallow instantiation at an address terminated earlier in the same call stack until its deferred meter charges have fully settled.

## Proof of Concept
1. Instantiate contract `X` at deterministic address `A` via a known `salt = S`, fund it above ED, and accumulate some storage so `total_deposit()` > 0.
2. From a driver contract within a single top-level call, invoke `seal_terminate` on `X` with an attacker-controlled `beneficiary`.
3. In the same call stack, immediately instantiate a new contract `Y` at the same address `A` using the identical `code_hash`/`input_data`/`salt = S`, transferring `value` > ED to it.
4. Let the extrinsic finish and observe that `try_into_deposit`'s deferred `Refund`/`Terminated` charge for `X` executes `T::Currency::reducible_balance(&A, ...)` and transfers it to `beneficiary` — draining `Y`'s ED/value — while `System::Account` consumer counts for `A` end up inconsistent between `X`'s `dec_consumers` and `Y`'s `inc_consumers`.
5. Assert `A`'s resulting balance is less than `Y`'s expected `value + min_balance`, and that `beneficiary`'s balance increase exceeds `X`'s own free balance at termination time.

### Citations

**File:** substrate/frame/contracts/src/storage/meter.rs (L395-408)
```rust
	pub fn try_into_deposit(self, origin: &Origin<T>) -> Result<DepositOf<T>, DispatchError> {
		// Only refund or charge deposit if the origin is not root.
		let origin = match origin {
			Origin::Root => return Ok(Deposit::Charge(Zero::zero())),
			Origin::Signed(o) => o,
		};
		for charge in self.charges.iter().filter(|c| matches!(c.amount, Deposit::Refund(_))) {
			E::charge(origin, &charge.contract, &charge.amount, &charge.state)?;
		}
		for charge in self.charges.iter().filter(|c| matches!(c.amount, Deposit::Charge(_))) {
			E::charge(origin, &charge.contract, &charge.amount, &charge.state)?;
		}
		Ok(self.total_deposit)
	}
```

**File:** substrate/frame/contracts/src/storage/meter.rs (L439-463)
```rust
	pub fn charge_instantiate(
		&mut self,
		origin: &T::AccountId,
		contract: &T::AccountId,
		contract_info: &mut ContractInfo<T>,
		code_info: &CodeInfo<T>,
	) -> Result<(), DispatchError> {
		debug_assert!(matches!(self.contract_state(), ContractState::Alive));

		// We need to make sure that the contract's account exists.
		let ed = Pallet::<T>::min_balance();
		self.total_deposit = Deposit::Charge(ed);
		T::Currency::transfer(origin, contract, ed, Preservation::Preserve)?;

		// A consumer is added at account creation and removed it on termination, otherwise the
		// runtime could remove the account. As long as a contract exists its account must exist.
		// With the consumer, a correct runtime cannot remove the account.
		System::<T>::inc_consumers(contract)?;

		let deposit = contract_info.update_base_deposit(&code_info);
		let deposit = Deposit::Charge(deposit);

		self.charge_deposit(contract.clone(), deposit);
		Ok(())
	}
```

**File:** substrate/frame/contracts/src/storage/meter.rs (L470-476)
```rust
	pub fn terminate(&mut self, info: &ContractInfo<T>, beneficiary: T::AccountId) {
		debug_assert!(matches!(self.contract_state(), ContractState::Alive));
		self.own_contribution = Contribution::Terminated {
			deposit: Deposit::Refund(info.total_deposit()),
			beneficiary,
		};
	}
```

**File:** substrate/frame/contracts/src/storage/meter.rs (L596-605)
```rust
		if let ContractState::<T>::Terminated { beneficiary } = state {
			System::<T>::dec_consumers(&contract);
			// Whatever is left in the contract is sent to the termination beneficiary.
			T::Currency::transfer(
				&contract,
				&beneficiary,
				T::Currency::reducible_balance(&contract, Preservation::Expendable, Polite),
				Preservation::Expendable,
			)?;
		}
```

**File:** substrate/frame/contracts/src/exec.rs (L866-882)
```rust
				FrameArgs::Instantiate { sender, nonce, executable, salt, input_data } => {
					let account_id = Contracts::<T>::contract_address(
						&sender,
						&executable.code_hash(),
						input_data,
						salt,
					);
					let contract = ContractInfo::new(&account_id, nonce, *executable.code_hash())?;
					(
						account_id,
						contract,
						executable,
						None,
						ExportedFunction::Constructor,
						Some(nonce),
					)
				},
```

**File:** substrate/frame/contracts/src/exec.rs (L1371-1373)
```rust
		info.queue_trie_for_deletion();
		ContractInfoOf::<T>::remove(&frame.account_id);
		Self::decrement_refcount(info.code_hash);
```
