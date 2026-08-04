### Title
Silent partial refund on `Deposit::Refund` in `ReservingExt::charge` can strand `StorageDepositReserve` hold after `dec_consumers` and account sweep - (File: substrate/frame/contracts/src/storage/meter.rs)

### Summary
In `ReservingExt::charge`, the `Deposit::Refund` branch calls `T::Currency::transfer_on_hold(..., Precision::BestEffort, ...)` and, if the transferred amount is less than the recorded deposit, only emits a `log::error!` instead of aborting the termination. Immediately afterward, and unconditionally, the code calls `System::<T>::dec_consumers(&contract)` and sweeps the account's remaining `reducible_balance` to the beneficiary, so any shortfall silently becomes an untracked, permanently stranded hold on the (already logically dead) contract account.

### Finding Description
`ReservingExt::charge` (`substrate/frame/contracts/src/storage/meter.rs:567-605`) handles termination refunds: [1](#0-0) 

The refund uses `Precision::BestEffort`. Looking at the generic `transfer_on_hold` default implementation in `fungible::hold::Mutate`: [2](#0-1) 

`amount` is clamped to `min(liquid, have)` where `have = balance_on_hold(StorageDepositReserve, contract)` and `liquid = reducible_total_balance_on_hold(contract, Fortitude::Polite)`. Crucially, `decrease_balance_on_hold` (called with the already-clamped `amount`) only reduces the on-hold ledger entry for `HoldReason::StorageDepositReserve` by the clamped amount — the remainder `have - amount` **stays recorded as held** under that reason on the contract account.

Back in `ReservingExt::charge`, when `transferred < *amount`, execution does not stop — it falls through to: [3](#0-2) 

`dec_consumers` removes the consumer reference that was guaranteeing the account's existence, and the subsequent `transfer` moves only the currently-*reducible* balance (which, by definition, excludes anything still on hold) to the beneficiary. The `ContractInfo` storage for the contract has already been (or is about to be) removed by the caller of `terminate`, so nothing in the pallet's storage tracks that residual `StorageDepositReserve` hold anymore — it becomes permanently orphaned on an account that is no longer a tracked contract and no longer has a protecting consumer reference.

This breaks the intended invariant that `ContractInfo.total_deposit()` represents a fully recoverable hold that is either returned to `origin` or swept to `beneficiary` on termination — the `Ok(())` return with only a log message means no `DispatchError` (`StorageRefundNotEnoughFunds`/similar) is ever raised to abort the termination, unlike the parallel `Deposit::Charge` path which uses `Precision::Exact` and does propagate errors via `?`.

The realistic trigger for `transferred < *amount` is any mechanism that reduces `reducible_total_balance_on_hold` for the contract's account below the recorded `StorageDepositReserve` amount at the moment of termination — e.g., a freeze/lock placed on the contract's own account balance through another pallet the contract (or a route the contract's account participates in) interacts with, which `Fortitude::Polite` respects and therefore is not overridden by the best-effort release.

### Impact Explanation
If triggered, the contract's account retains a hold under `StorageDepositReserve` that:
- Is not refunded to `origin` (the party that originally paid the deposit and expects `try_into_deposit` bookkeeping to be exact).
- Is not swept to `beneficiary` (the sweep only moves already-free/reducible balance).
- Has no corresponding `ContractInfo` storage entry anymore (deleted on termination), so no code path exists to later release or account for it.
- Occurs on an account whose consumer reference has already been decremented, changing its reap/lifecycle semantics.

This is a concrete accounting-invariant violation: funds become permanently unreachable through normal pallet-contracts logic, and the deposit-refund guarantee silently fails without reverting the extrinsic.

### Likelihood Explanation
The code-level gap (best-effort refund + log-only error + unconditional `dec_consumers`/sweep) is unconditionally present in `ReservingExt::charge` and does not depend on any privileged action to exist. However, the concrete attacker-controlled precondition — getting `reducible_total_balance_on_hold` for the contract's own account to fall below the recorded `StorageDepositReserve` hold at termination time (e.g., via a freeze applied through another pallet) — is not directly exposed by `pallet_contracts` itself; the base pallet does not provide a standard host function letting contract code freeze/lock its own account balance via another pallet. Reaching this precondition would require a specific runtime composition (e.g., a chain extension or precompile granting the contract's account the ability to interact with a freeze-capable pallet such as vesting/staking/nomination-pools on itself) which is outside `pallet_contracts`'s own code. Given this, likelihood is configuration-dependent rather than universally reachable from `pallet_contracts` alone, but the underlying missing-error-propagation defect is real and should be fixed defensively regardless of how the precondition is reached.

### Recommendation
- In the `Deposit::Refund` branch of `ReservingExt::charge`, treat `transferred < *amount` as a hard failure: return `Err(Error::<T>::StorageRefundNotEnoughFunds.into())` (or a new dedicated error) instead of only logging, before proceeding to `dec_consumers` and the balance sweep.
- Alternatively/additionally, use `Precision::Exact` for the refund (mirroring the `Charge` branch) so `transfer_on_hold` itself returns an error on any shortfall, guaranteeing the hold is either fully released or the termination reverts.
- Ensure `dec_consumers` and the reducible-balance sweep only execute after the refund is confirmed complete, so no path exists where the consumer ref is dropped and the account is swept while a residual hold remains.

### Proof of Concept
Rust unit test in `substrate/frame/contracts/src/storage/meter.rs` (or an integration test in `substrate/frame/contracts/src/tests.rs`) plan:
1. Set up a contract account with `HoldReason::StorageDepositReserve` holding an amount `D` (via normal charge flow).
2. Independently reduce the account's `reducible_total_balance_on_hold` below `D` by placing a freeze on the contract's account for a different reason (using `fungible::MutateFreeze` directly against the test's `Currency` impl, standing in for a hypothetical intermediate-pallet interaction), such that `liquid < D`.
3. Call `Contracts::terminate` (or invoke `ReservingExt::charge` directly with `ContractState::Terminated`) for that contract.
4. Assert either:
   - The call returns `Err` (e.g. `Error::<T>::StorageRefundNotEnoughFunds`) and no state changes occurred (hold, consumers, and account balance untouched) — expected fixed behavior; or
   - Under current code, assert the bug: the call returns `Ok(())`, `balance_on_hold(&StorageDepositReserve, &contract) > 0` after termination, `System::<T>::consumers(&contract) == 0`, and `ContractInfo` for the contract no longer exists — demonstrating the stranded, untracked hold.

### Citations

**File:** substrate/frame/contracts/src/storage/meter.rs (L567-606)
```rust
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
```

**File:** substrate/frame/support/src/traits/tokens/fungible/hold.rs (L354-378)
```rust
	) -> Result<Self::Balance, DispatchError> {
		// We must check total-balance requirements if `force` is `Fortitude::Polite`.
		let have = Self::balance_on_hold(reason, source);
		let liquid = Self::reducible_total_balance_on_hold(source, force);
		if let BestEffort = precision {
			amount = amount.min(liquid).min(have);
		} else {
			ensure!(amount <= liquid, TokenError::Frozen);
			ensure!(amount <= have, TokenError::FundsUnavailable);
		}

		// We want to make sure we can deposit the amount in advance. If we can't then something is
		// very wrong.
		ensure!(Self::can_deposit(dest, amount, Extant) == Success, TokenError::CannotCreate);
		ensure!(mode == Free || Self::hold_available(reason, dest), TokenError::CannotCreateHold);

		let amount = Self::decrease_balance_on_hold(reason, source, amount, precision)?;
		let actual = if mode == OnHold {
			Self::increase_balance_on_hold(reason, dest, amount, precision)?
		} else {
			Self::increase_balance(dest, amount, precision)?
		};
		Self::done_transfer_on_hold(reason, source, dest, actual);
		Ok(actual)
	}
```
