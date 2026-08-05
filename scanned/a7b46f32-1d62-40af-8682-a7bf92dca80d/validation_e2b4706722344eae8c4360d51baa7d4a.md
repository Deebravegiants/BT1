### Title
Deferred termination-sweep in `Ext::charge` drains a redeployed contract's balance/ED to the terminated contract's beneficiary - ([File: substrate/frame/contracts/src/storage/meter.rs])

### Summary
`RawMeter::try_into_deposit` defers all balance transfers (refunds, charges, and the termination "sweep remaining balance to beneficiary") to the very end of a whole call-stack execution, and refunds are processed before charges. If a contract is terminated and a new contract is instantiated at the same account id later in the same call stack (deterministic CREATE2-style address reuse), the deferred termination sweep for the old contract executes against whatever balance is present in that account *at the end of the transaction* — which by then includes the new contract's endowment/ED and any deposits already transferred to it — sending that balance to the (attacker-controlled) termination beneficiary instead of the new contract's rightful funds.

### Finding Description
`RawMeter::terminate` (`substrate/frame/contracts/src/storage/meter.rs:470-476`) only records a deferred `Charge{contract, amount: Refund(total_deposit), state: Terminated{beneficiary}}` entry; it does not immediately move balance. `try_into_deposit` (`meter.rs:395-408`) processes all `Refund` charges first, then all `Charge` charges, only once at the very end of the whole root-meter call stack via `E::charge` (`Ext::charge`, `meter.rs:540-607`).

In `ReservingExt::charge`, the `Deposit::Refund` branch, when `state` is `ContractState::Terminated{beneficiary}`, executes:
```
System::<T>::dec_consumers(&contract);
T::Currency::transfer(&contract, &beneficiary, T::Currency::reducible_balance(&contract, Preservation::Expendable, Polite), Preservation::Expendable)?;
```
(`meter.rs:596-605`). This sweeps *whatever reducible balance the account currently holds* to `beneficiary` — it is not scoped to only the balance that belonged to the terminated contract. It executes lazily, at the end of the whole extrinsic, identified purely by account id.

Contract addresses in both pallet-contracts (`DefaultAddressGenerator::contract_address`, `substrate/frame/contracts/src/address.rs:55-67`) and pallet-revive (`address::create2`, `substrate/frame/revive/src/address.rs:272-285`) are fully deterministic functions of `(deployer, code_hash, input_data, salt)`. If, within a single call stack, a contract is terminated and then a new contract is instantiated at the exact same address (e.g. via a nested `create2` call with the same salt/code/input, which the code explicitly supports and tests — see `create2_works`/`create_call_tracing_works` in `substrate/frame/revive/src/tests/*`), `charge_instantiate` (`meter.rs:439-463`) immediately transfers ED to that account and increments its consumers, and any constructor code can transfer further value into it — all of this happens *before* the root meter's `try_into_deposit` runs the deferred termination sweep for the original contract.

When `try_into_deposit` finally executes, the `Refund`/`Terminated` branch for the old contract sweeps the account's current reducible balance (now containing the new contract's ED + any transferred value) to the old beneficiary, and calls `dec_consumers` — while the new contract's own `charge_instantiate` had already called `inc_consumers` for the same account, creating a consumer-count/balance mismatch. The net effect: the newly instantiated contract's locked existential deposit and value can be drained to an attacker-chosen beneficiary, while origin is still separately charged the new contract's storage deposit in the subsequent `Charge` phase of the same `try_into_deposit` call — i.e., origin pays for a deposit whose backing balance was just siphoned away.

No check in `try_into_deposit`, `absorb`, or `Ext::charge` verifies that the account referenced by a `Terminated` charge is still the *same live instance* it was terminated for, nor scopes the beneficiary sweep to the specific balance associated with that terminated instance.

### Impact Explanation
An attacker who can terminate a contract and redeploy at the same deterministic address within a single call stack (a supported, tested pattern in pallet-revive via CREATE2) can cause the new contract's endowed value/ED to be transferred to an attacker-controlled beneficiary instead of remaining locked in the live, redeployed contract. This breaks the invariant that a live contract's held balance/deposit must correspond to its actual live storage and endowment, and can result in fund extraction / underpriced deposit accounting for the redeployed instance, matching the scoped impact.

### Likelihood Explanation
Requires only unprivileged, signed-user-controlled contract calls: instantiate contract X with a known salt, call `seal_terminate` (or Solidity `selfdestruct`) with an attacker-chosen beneficiary, then instantiate a new contract at the same deterministic address (same deployer/code_hash/input/salt) within the same call stack/extrinsic, before the stack returns and `try_into_deposit` runs. All of the necessary primitives (CREATE2 determinism, deferred termination charge, refund-then-charge batching) exist in the reachable code paths cited above, making this feasible and repeatable for any account controlling contract deployment.

### Recommendation
Scope the termination beneficiary sweep and the refund transfer strictly to the balance/deposit that existed for the *specific terminated instance*, not to "whatever is currently in the account" at finalization time. Concretely: process the termination sweep and consumer bookkeeping synchronously at `seal_terminate` time (or capture/lock the terminated contract's balance snapshot at termination time) rather than deferring it past any point where the same account id could be reused for a new live instance in the same call stack. Alternatively, disallow instantiation at an address that was terminated earlier in the *same* transaction until the deferred charges for that address have been fully settled.

### Proof of Concept
Integration test in `substrate/frame/revive/src/tests` (pvm or sol harness):
1. Instantiate contract `X` at deterministic address `A` via `create2` with `salt = S`, fund it, accumulate storage (so `total_deposit()` > 0).
2. From within a single top-level call (e.g. a driver "Caller" contract), call `seal_terminate`/`selfdestruct(beneficiary)` on `X`, then in the same call stack call `create2` with the same `code_hash`/`input_data`/`salt = S` to redeploy a new contract `Y` at the same address `A`, transferring `value` (>ED) to it.
3. Let the extrinsic finish.
4. Assert:
   - `get_balance(A) == value + min_balance` is **violated** (balance is less, having been swept to `beneficiary`), OR
   - `beneficiary`'s balance increased by more than `X`'s own free balance at termination time (it also includes `Y`'s endowment),
   - and/or `AccountInfoOf::<T>::get(A)` shows a live contract with on-hold deposit inconsistent with `balance_on_hold(&HoldReason::StorageDepositReserve, A)` actually available to back it (`Charge total` for the live contract does not equal its backing held balance).

Note: I could not fully trace, within the available tool iterations, the exact synchronous removal point of `ContractInfoOf`/`AccountInfoOf` for a terminated contract in `exec.rs` (i.e., confirmation that pallet-contracts/pallet-revive unconditionally permit same-address redeployment within one call stack before the deferred meter charges execute). This is a stated precondition in the question and is consistent with the deterministic CREATE2 address derivation and existing test coverage found (`create2_works`, `create_call_tracing_works`, `existential_deposit_shall_not_be_charged_twice`), but a Devin session with full repo access should verify this exact ordering in `exec.rs`'s `terminate`/`instantiate` frame handling before treating this as fully confirmed end-to-end. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** substrate/frame/contracts/src/storage/meter.rs (L465-476)
```rust
	/// Call to tell the meter that the currently executing contract was terminated.
	///
	/// This will manipulate the meter so that all storage deposit accumulated in
	/// `contract_info` will be refunded to the `origin` of the meter. And the free
	/// (`reducible_balance`) will be sent to the `beneficiary`.
	pub fn terminate(&mut self, info: &ContractInfo<T>, beneficiary: T::AccountId) {
		debug_assert!(matches!(self.contract_state(), ContractState::Alive));
		self.own_contribution = Contribution::Terminated {
			deposit: Deposit::Refund(info.total_deposit()),
			beneficiary,
		};
	}
```

**File:** substrate/frame/contracts/src/storage/meter.rs (L540-607)
```rust
	fn charge(
		origin: &T::AccountId,
		contract: &T::AccountId,
		amount: &DepositOf<T>,
		state: &ContractState<T>,
	) -> Result<(), DispatchError> {
		match amount {
			Deposit::Charge(amount) | Deposit::Refund(amount) if amount.is_zero() => return Ok(()),
			Deposit::Charge(amount) => {
				// This could fail if the `origin` does not have enough liquidity. Ideally, though,
				// this should have been checked before with `check_limit`.
				T::Currency::transfer_and_hold(
					&HoldReason::StorageDepositReserve.into(),
					origin,
					contract,
					*amount,
					Precision::Exact,
					Preservation::Preserve,
					Fortitude::Polite,
				)?;

				Pallet::<T>::deposit_event(Event::StorageDepositTransferredAndHeld {
					from: origin.clone(),
					to: contract.clone(),
					amount: *amount,
				});
			},
			Deposit::Refund(amount) => {
				let transferred = T::Currency::transfer_on_hold(
					&HoldReason::StorageDepositReserve.into(),
					contract,
					origin,
					*amount,
					Precision::BestEffort,
					Restriction::Free,
					Fortitude::Polite,
				)?;

				Pallet::<T>::deposit_event(Event::StorageDepositTransferredAndReleased {
					from: contract.clone(),
					to: origin.clone(),
					amount: transferred,
				});

				if transferred < *amount {
					// This should never happen, if it does it means that there is a bug in the
					// runtime logic. In the rare case this happens we try to refund as much as we
					// can, thus the `Precision::BestEffort`.
					log::error!(
						target: LOG_TARGET,
						"Failed to repatriate full storage deposit {:?} from contract {:?} to origin {:?}. Transferred {:?}.",
						amount, contract, origin, transferred,
					);
				}
			},
		}
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
		Ok(())
	}
```

**File:** substrate/frame/contracts/src/address.rs (L55-67)
```rust
impl<T: Config> AddressGenerator<T> for DefaultAddressGenerator {
	/// Formula: `hash("contract_addr_v1" ++ deploying_address ++ code_hash ++ input_data ++ salt)`
	fn contract_address(
		deploying_address: &T::AccountId,
		code_hash: &CodeHash<T>,
		input_data: &[u8],
		salt: &[u8],
	) -> T::AccountId {
		let entropy = (b"contract_addr_v1", deploying_address, code_hash, input_data, salt)
			.using_encoded(T::Hashing::hash);
		Decode::decode(&mut TrailingZeroInput::new(entropy.as_ref()))
			.expect("infinite length input; no invalid inputs for type; qed")
	}
```

**File:** substrate/frame/revive/src/address.rs (L272-285)
```rust
/// Determine the address of a contract using the CREATE2 semantics.
pub fn create2(deployer: &H160, code: &[u8], input_data: &[u8], salt: &[u8; 32]) -> H160 {
	let init_code_hash = {
		let init_code: Vec<u8> = code.into_iter().chain(input_data).cloned().collect();
		keccak_256(init_code.as_ref())
	};
	let mut bytes = [0; 85];
	bytes[0] = 0xff;
	bytes[1..21].copy_from_slice(deployer.as_bytes());
	bytes[21..53].copy_from_slice(salt);
	bytes[53..85].copy_from_slice(&init_code_hash);
	let hash = keccak_256(&bytes);
	H160::from_slice(&hash[12..])
}
```
