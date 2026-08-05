Based on the code, `do_terminate` refunds the *entire* storage-deposit hold to `exec_config.funds(origin.account_id())` — the extrinsic's signed origin (the transaction sender / `beneficiary`'s caller), not to each `NativeDepositOf` contributor individually. This confirms the bug described.

### Title
`refund_all` at contract termination pays the entire multi-contributor storage deposit to the terminating caller instead of each contributor - ([File: substrate/frame/revive/src/deposit_payment.rs])

### Summary
When a contract's storage deposit was funded by multiple distinct signed accounts through the native fallback path (tracked per-contributor in `NativeDepositOf`), calling `terminate` causes `Deposit::refund_all` to release the *whole* combined hold to whichever account is the transaction origin of the `terminate` call, ignoring each contributor's individually tracked entitlement. Any signed account that triggers termination (e.g. via the `ISystem.terminate` precompile / `SELFDESTRUCT`-equivalent call) receives other unrelated users' storage-deposit contributions.

### Finding Description
`Pallet::do_terminate` in `substrate/frame/revive/src/exec.rs` calls: [1](#0-0) 
`T::Deposit::refund_all(&contract_account, exec_config.funds(origin.account_id()?))`, where `origin` is the caller that invoked `terminate` (the transaction's signed origin), not the storage-deposit contributor(s).

`PGasDeposit::refund_all` and the default `()` `Deposit::refund_all` in `substrate/frame/revive/src/deposit_payment.rs` explicitly bypass the per-contributor cap that `refund_on_hold` normally enforces via `NativeDepositOf`: [2](#0-1) 
The doc comment on the trait itself states this is deliberate: "ignoring the per-contributor caps that govern partial refunds. Used at contract termination", and the code comment explains "The native cap only makes sense for partial refunds on a live contract; at termination there is one recipient and the contract is gone."

However this reasoning is flawed when multiple *distinct* accounts contributed to the same contract's `StorageDepositReserve` hold via `NativeDepositOf<T>` (keyed `(holder, contributor) -> amount`, as documented at `substrate/frame/revive/src/lib.rs` lines 711-730). `refund_all` sends the entire hold to the single terminator-designated `dst`, regardless of how many contributors' funds are in that hold, and regardless of whether the caller triggering `terminate` is one of the contributors at all.

The repository's own test explicitly documents this behavior and asserts it happens: [3](#0-2) 
In this test, ALICE and CHARLIE both fund distinct storage slots (`growStorage`) via the native fallback, populating two separate `NativeDepositOf` rows. When ALICE (the tx-origin who calls `terminate`, distinct from `beneficiary` which is set to DJANGO) triggers termination, `alice_after - alice_before >= native_held` where `native_held == alice_entry + charlie_entry`. ALICE receives CHARLIE's contribution along with her own — CHARLIE gets nothing back.

No check in `do_terminate`, `refund_all`, or the calling extrinsic path verifies that the caller invoking `terminate` is a/the sole contributor to `NativeDepositOf[contract]`, nor does it split the refund across the recorded contributors. The reachable path is: `pallet-revive` dispatchable (`call`/`eth_transact`) → contract executes `SELFDESTRUCT`/`terminate` opcode or the `ISystem.terminate` precompile → `Stack::do_terminate` → `T::Deposit::refund_all`.

### Impact Explanation
An unprivileged account that never contributed any storage deposit to a contract (or contributed only a small fraction) can, by being the one to trigger the contract's `terminate` call, redirect the storage-deposit refund attributable to other, unrelated signed contributors to itself. This is a direct theft of another user's funds that were held under `HoldReason::StorageDepositReserve` on the contract, since those contributor accounts (`CHARLIE` in the test) never regain their `NativeDepositOf` entitlement — it's simply zeroed out with the balance going to the terminator's account instead.

### Likelihood Explanation
The precondition — a contract whose storage was grown by calls from more than one distinct signed account, each falling back to the native currency path recorded in `NativeDepositOf` — is a normal, unprivileged usage pattern (any dApp with multiple users writing/growing storage on a shared contract, e.g. via `growStorage`-like methods, funded by their own tx). Any signed account (including one with no prior relationship to the contract) can then call `terminate` through the contract's own logic (if the contract's ABI allows any caller to self-destruct, or if the contract itself is attacker-deployed) or via `ISystem.terminate`. This is fully reachable, repeatable, and already reproduced in the codebase's own unit test.

### Recommendation
`Deposit::refund_all` should either: (1) iterate `NativeDepositOf::iter_prefix(contract)` and pay each recorded contributor their own tracked native amount instead of sending the whole hold to a single `dst`, refunding only the unattributed/PGAS remainder to the terminator's `dst`; or (2) restrict who may trigger `terminate` (or where the refund is routed) so that the native `StorageDepositReserve` amounts always settle back to their respective `NativeDepositOf` contributors rather than the single termination-triggering account.

### Proof of Concept
The exact scenario is already implemented as `refund_all_drains_multi_contributor_native_hold` in `substrate/frame/revive/src/tests/deposit_payment.rs` (lines 460-527): ALICE and CHARLIE each call `growStorage` on the same contract (populating two `NativeDepositOf` rows), then ALICE (as `terminate`'s tx-origin, with `beneficiary` set to a third address `DJANGO`) calls `terminate`. Assertions confirm `native_held == alice_entry + charlie_entry` before termination and `alice_after - alice_before >= native_held` after — i.e., ALICE's balance increase covers both her own and CHARLIE's deposit, while CHARLIE's balance is never credited back. A stronger PoC would additionally assert `Balances::balance(&CHARLIE)` is unchanged post-termination and that a third, uninvolved signed account (not ALICE, not CHARLIE) triggering `terminate` still receives the full combined hold, proving the redirection is independent of contribution history.

### Citations

**File:** substrate/frame/revive/src/exec.rs (L1809-1813)
```rust
		let mut delete_contract = |trie_id: &TrieId, code_hash: &H256| {
			// deposit needs to be removed as it adds a consumer
			let refund =
				T::Deposit::refund_all(&contract_account, exec_config.funds(origin.account_id()?))?;

```

**File:** substrate/frame/revive/src/deposit_payment.rs (L420-440)
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

**File:** substrate/frame/revive/src/tests/deposit_payment.rs (L460-527)
```rust
/// A contract whose storage was paid for by two different signers, both via the native
/// fallback path, can still be terminated. [`Deposit::refund_all`] bypasses the per-payer
/// [`NativeDepositOf`] cap (one recipient at termination, contract gone), so the full native
/// hold goes to the terminator and any PGAS hold is settled via `settle_pgas_refund`.
#[test_case(FixtureType::Solc)]
#[test_case(FixtureType::Resolc)]
fn refund_all_drains_multi_contributor_native_hold(fixture_type: FixtureType) {
	let (code, _) = compile_module_with_type("MultiContributorStorage", fixture_type).unwrap();
	ExtBuilder::default().build().execute_with(|| {
		Balances::set_balance(&ALICE, 100_000_000_000);
		Balances::set_balance(&CHARLIE, 100_000_000_000);

		let Contract { addr, account_id } =
			builder::bare_instantiate(Code::Upload(code)).build_and_unwrap_contract();

		assert_ok!(
			builder::bare_call(addr)
				.data(MultiContributorStorage::growStorageCall {}.abi_encode())
				.build()
				.result,
		);
		assert_ok!(
			BareCallBuilder::<Test>::bare_call(RuntimeOrigin::signed(CHARLIE), addr)
				.data(MultiContributorStorage::growStorageCall {}.abi_encode())
				.build()
				.result,
		);

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
	});
}
```
