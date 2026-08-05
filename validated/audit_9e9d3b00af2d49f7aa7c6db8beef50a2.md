This confirms the claim precisely. The code, comments, and existing test all corroborate the described behavior exactly as stated.

Audit Report

## Title
`refund_all` sends the entire multi-contributor `NativeDepositOf` hold to whoever calls `terminate`, not to the original depositors - (File: substrate/frame/revive/src/deposit_payment.rs)

## Summary
When a contract's storage deposit has been funded in native currency by multiple distinct accounts (tracked per-contributor in `NativeDepositOf`), calling `terminate` causes `Deposit::refund_all` to release the entire native hold to the transaction's signed origin, ignoring each contributor's individual entitlement recorded in `NativeDepositOf`. Because pallet-revive imposes no access control on who may invoke a contract's `terminate` entry point, any unrelated third-party account that triggers termination as the tx origin receives other users' storage-deposit-backed native currency.

## Finding Description
`NativeDepositOf<T>` is a double map `(holder, contributor) -> amount` intended to cap how much native currency each specific contributor may reclaim from a contract's hold [1](#0-0) . This cap is correctly enforced in the partial-refund path `refund_on_hold`, which looks up `NativeDepositOf::<T>::get(from, to)` and caps the native refund accordingly [2](#0-1) .

At termination, however, `refund_all` is used instead and explicitly bypasses this cap. The default `()` backend reads the total `balance_on_hold` and refunds it all to `dst` with no per-contributor accounting [3](#0-2) . The PGAS backend's `refund_all` does the same for the native portion before settling PGAS, and its own doc comment states it "ignor[es] the per-contributor cap" [4](#0-3) .

`do_terminate` in `exec.rs` calls `T::Deposit::refund_all(&contract_account, exec_config.funds(origin.account_id()?))`, where `origin` is the transaction's signed origin — not the contract-supplied `beneficiary`, and not restricted to any prior contributor [5](#0-4) . The `beneficiary` only receives the contract's remaining free balance via `Self::transfer`; the storage-deposit hold goes exclusively to `origin`. Nothing in the pallet restricts who can call `terminate` — that is left entirely to contract-level logic, and the `MultiContributorStorage` fixture exposes it as an unrestricted public function.

This is directly acknowledged in the pallet's own test comment and reproduced by its test: ALICE and CHARLIE both fund distinct storage slots recorded separately in `NativeDepositOf`, yet when the contract is terminated by a `bare_call` whose signed origin is ALICE, she receives the full combined hold (`alice_entry + charlie_entry`) rather than only her own share [6](#0-5) [7](#0-6) . The mechanism (`dst = origin`, uncapped) is agnostic to whether the caller is a contributor at all — it applies identically to any account able to invoke `terminate`.

## Impact Explanation
An unprivileged, unrelated account can capture another user's storage-deposit-backed native currency by invoking a contract's unguarded `terminate` entry point after other users have funded that contract's storage deposit via separate transactions. The rightful contributors' `NativeDepositOf` entries are silently zeroed out while the corresponding native currency is routed entirely to the terminating caller. This is a concrete, deterministic loss of funds for other users, matching an in-scope funds-theft impact for pallet-revive.

## Likelihood Explanation
The preconditions are realistic and easy to satisfy: any contract that (a) accumulates native-fallback storage deposits from multiple distinct callers across separate transactions, and (b) exposes a `terminate`/self-destruct call without contributor-restricted access control, is exploitable by any third party who calls that function as the tx origin. No race condition, special privilege, or victim mistake beyond ordinary usage of a permissionless contract is required, and the behavior is deterministic and repeatable, as demonstrated by the existing `refund_all_drains_multi_contributor_native_hold` test.

## Recommendation
At termination, either (a) iterate and settle `NativeDepositOf` per contributor, refunding each contributor their own capped share (e.g., via `NativeDepositOf::iter_prefix(contract)`) before distributing any untracked remainder, or (b) explicitly scope and enforce that pallet-revive's storage-deposit refund model only guarantees per-contributor protection for "same live contract, partial refund" scenarios, ensuring contract authors are clearly warned that at termination the entire consolidated hold is paid to the transaction origin rather than split among contributors — and, if theft of contributor funds is considered in scope, implement per-contributor distribution at termination rather than silently discarding that accounting.

## Proof of Concept
Existing test `refund_all_drains_multi_contributor_native_hold` in `substrate/frame/revive/src/tests/deposit_payment.rs` (lines 466-527) already demonstrates the core issue: ALICE and CHARLIE independently fund a contract's storage deposit via the native fallback path, each recorded separately in `NativeDepositOf`; terminating the contract (with the signed origin being ALICE) results in ALICE receiving the full combined hold (`alice_entry + charlie_entry`) rather than only her own share. Substituting an unrelated third account (e.g., `EVE`, with zero `NativeDepositOf` entry) as the signed origin calling `terminate` would show that account receiving the entire multi-contributor hold instead of either ALICE or CHARLIE, confirming the funds are captured by the terminator regardless of contribution history.

### Citations

**File:** substrate/frame/revive/src/lib.rs (L711-730)
```rust
	/// Native currency storage deposit contributed by a user into a contract.
	///
	/// Bounds how much native value the user can receive back from that contract's
	/// storage deposit.
	///
	/// Keys: `(holder, contributor) -> amount`
	/// - `holder`: account on which the deposit is held (a contract, or the pallet's own account
	///   for code-upload deposits).
	/// - `contributor`: user that funded the deposit. Receives the native portion on refund, capped
	///   at this entry's `amount`.
	#[pallet::storage]
	pub(crate) type NativeDepositOf<T: Config> = StorageDoubleMap<
		_,
		Identity,
		T::AccountId,
		Identity,
		T::AccountId,
		BalanceOf<T>,
		ValueQuery,
	>;
```

**File:** substrate/frame/revive/src/deposit_payment.rs (L250-260)
```rust
	fn refund_all(
		from: &T::AccountId,
		dst: Funds<T::AccountId>,
	) -> Result<BalanceOf<T>, DispatchError> {
		let reason = HoldReason::StorageDepositReserve;
		let amount = T::Currency::balance_on_hold(&reason.into(), from);
		if !amount.is_zero() {
			<Self as Deposit<T>>::refund_on_hold(reason, from, dst, amount)?;
		}
		Ok(amount)
	}
```

**File:** substrate/frame/revive/src/deposit_payment.rs (L384-412)
```rust
	fn refund_on_hold(
		reason: HoldReason,
		from: &T::AccountId,
		dst: Funds<T::AccountId>,
		amount: BalanceOf<T>,
	) -> DispatchResult {
		let to = match &dst {
			Funds::Balance(to) | Funds::TxFee(to) => *to,
		};
		let contribution = NativeDepositOf::<T>::get(from, to);
		let native_requested = amount.min(contribution);

		let native_refunded = if !native_requested.is_zero() {
			<() as Deposit<T>>::refund_on_hold(reason, from, dst, native_requested)?;
			let new_val = contribution.saturating_sub(native_requested);
			if new_val.is_zero() {
				NativeDepositOf::<T>::remove(from, to);
			} else {
				NativeDepositOf::<T>::insert(from, to, new_val);
			}
			native_requested
		} else {
			BalanceOf::<T>::zero()
		};

		let pgas_needed = amount.saturating_sub(native_refunded);
		Self::settle_pgas_refund(reason, from, to, pgas_needed)?;
		Ok(())
	}
```

**File:** substrate/frame/revive/src/deposit_payment.rs (L421-440)
```rust
	/// Refunds the full native hold to `dst` ignoring the per-contributor cap, then settles the
	/// PGAS hold via [`Self::settle_pgas_refund`] (refunding `RefundPercent` to `dst` and burning
	/// the rest). The native cap only makes sense for partial refunds on a live contract; at
	/// termination there is one recipient and the contract is gone.
	///
	/// Note: callers must run inside a storage layer so partial state rolls back on error.
	fn refund_all(
		from: &T::AccountId,
		dst: Funds<T::AccountId>,
	) -> Result<BalanceOf<T>, DispatchError> {
		let to = match &dst {
			Funds::Balance(to) | Funds::TxFee(to) => *to,
		};
		let native = <() as Deposit<T>>::refund_all(from, dst)?;
		let reason = HoldReason::StorageDepositReserve;

		let pgas = Self::pgas_on_hold(reason, from);
		let pgas = Self::settle_pgas_refund(reason, from, to, pgas)?;
		Ok(native.saturating_add(pgas))
	}
```

**File:** substrate/frame/revive/src/exec.rs (L1809-1834)
```rust
		let mut delete_contract = |trie_id: &TrieId, code_hash: &H256| {
			// deposit needs to be removed as it adds a consumer
			let refund =
				T::Deposit::refund_all(&contract_account, exec_config.funds(origin.account_id()?))?;

			// we added this consumer manually when instantiating
			System::<T>::dec_consumers(&contract_account);

			// ED was minted when the account was brought into existence; burn it now.
			T::Deposit::destroy_contract(contract_account)?;

			// this is needed to:
			// 1) Send any balance that was send to the contract after termination.
			// 2) To fail termination if any locks or holds prevent to completely empty the account.
			let balance = <Contracts<T>>::convert_native_to_evm(<AccountInfo<T>>::total_balance(
				contract_address.into(),
			));
			Self::transfer(
				&origin,
				contract_account,
				&args.beneficiary,
				balance,
				Preservation::Expendable,
				transaction_meter,
				exec_config,
			)?;
```

**File:** substrate/frame/revive/src/tests/deposit_payment.rs (L460-463)
```rust
/// A contract whose storage was paid for by two different signers, both via the native
/// fallback path, can still be terminated. [`Deposit::refund_all`] bypasses the per-payer
/// [`NativeDepositOf`] cap (one recipient at termination, contract gone), so the full native
/// hold goes to the terminator and any PGAS hold is settled via `settle_pgas_refund`.
```

**File:** substrate/frame/revive/src/tests/deposit_payment.rs (L488-525)
```rust
		let alice_entry = NativeDepositOf::<Test>::get(&account_id, &ALICE);
		let charlie_entry = NativeDepositOf::<Test>::get(&account_id, &CHARLIE);
		assert!(alice_entry > 0);
		assert!(charlie_entry > 0);

		let hold: <Test as Config>::RuntimeHoldReason = HoldReason::StorageDepositReserve.into();
		let native_held = Balances::balance_on_hold(&hold, &account_id);
		let pgas_held = AssetsHolder::balance_on_hold(PGAS_ASSET_ID, &hold, &account_id);
		assert_eq!(pgas_held, 0, "every charge fell back to native");
		assert_eq!(native_held, alice_entry + charlie_entry);

		let alice_before = Balances::balance(&ALICE);
		assert_ok!(
			builder::bare_call(addr)
				.data(
					MultiContributorStorage::terminateCall { beneficiary: DJANGO_ADDR.0.into() }
						.abi_encode(),
				)
				.build()
				.result,
		);
		let alice_after = Balances::balance(&ALICE);

		assert!(get_contract_checked(&addr).is_none(), "contract should be gone");
		assert_eq!(
			Balances::balance_on_hold(&hold, &account_id),
			0,
			"the full multi-contributor native hold has been released",
		);
		// ALICE receives the full storage-deposit hold (her own + CHARLIE's). The actual delta
		// also picks up the code-upload deposit refund and any tx-level deposit accounting,
		// so it is at least `native_held`.
		assert!(
			alice_after.saturating_sub(alice_before) >= native_held,
			"expected ALICE balance delta >= {}, got {}",
			native_held,
			alice_after.saturating_sub(alice_before),
		);
```
