### Title
Stale `NativeDepositOf` entries survive contract termination and are not cleared before same-address redeployment, breaking the "no more refund than deposited" invariant - ([File: substrate/frame/revive/src/lib.rs])

### Summary
`NativeDepositOf` is keyed by `(contract_account, contributor)`, and the contract account is derived deterministically from the H160 address, which is reusable via CREATE2-style salt after termination. `do_terminate`'s `refund_all` already pays out the *entire* native hold to the termination beneficiary, bypassing the per-contributor cap, but it does not clear the `NativeDepositOf` rows for that contract account — those rows are removed only lazily by `on_idle` when the deletion queue drains. If the same address is redeployed before that lazy cleanup runs, the stale entry is still readable/writable under the same storage key as the new contract, corrupting refund accounting.

### Finding Description
`NativeDepositOf` tracks how much native currency a `contributor` put into a `holder` (contract) account so refunds are capped at what was actually contributed: [1](#0-0) 

The pallet's own doc comment on the deletion queue confirms this is *not* cleared synchronously at termination, but only later, lazily, by `on_idle`: [2](#0-1) 

`do_terminate` (`substrate/frame/revive/src/exec.rs:1793-1866`) calls `T::Deposit::refund_all(&contract_account, ...)`, which sends the **entire** native hold to the termination beneficiary immediately, explicitly bypassing the per-contributor `NativeDepositOf` cap ("the native cap only makes sense for partial refunds on a live contract; at termination there is one recipient and the contract is gone"): [3](#0-2) 

Crucially, `refund_all`/`do_terminate` never removes the `NativeDepositOf[contract_account][contributor]` row itself — that only happens via `on_idle`'s deletion-queue drain, which is explicitly lazy and not guaranteed to run before the next block/transaction. This is confirmed directly by the test suite: `destroy_contract_reaps_account_and_clears_native_deposit_map` documents "`NativeDepositOf` rows survive termination; they're cleared lazily by `on_idle`" and asserts the rows are still non-zero immediately after termination: [4](#0-3) 

Because the H160 address (and therefore its mapped `T::AccountId`, which is the `NativeDepositOf` key) is reusable at will via a CREATE2-style deterministic salt, an attacker (or ordinary contributor) can:
1. Instantiate contract `X` at address `A` with `salt = S`; a contributor `ALICE` accrues `NativeDepositOf[A][ALICE] = D`.
2. Terminate `X`. `refund_all` pays out the full hold to the beneficiary immediately; `AccountInfoOf` is removed synchronously (allowing immediate re-instantiation), but `NativeDepositOf[A][ALICE] = D` is left untouched in storage.
3. Before `on_idle` drains the deletion queue (attacker fully controls this — they can redeploy in the very next block, and `on_idle` weight/scheduling is not guaranteed to run first), redeploy at the same address `A` with `salt = S` again.
4. The new contract's storage-deposit refund path (`refund_on_hold` in `deposit_payment.rs:384-412`) reads `NativeDepositOf::<T>::get(from, to)` using the *same* `(A, ALICE)` key, which still contains the stale, already-paid-out `D`. Any refund now triggered against the new contract's hold is capped by this stale value rather than by what was actually deposited into the *new* incarnation, letting a caller claim a refund attributable to a deposit that was already fully paid out at the prior termination.

The test authors are aware of this exact hazard — `instantiate_unique_trie_id` in `pvm.rs` explicitly calls `Contracts::on_idle(...)` "to drain `NativeDepositOf` rows before re-instantiating at the same address," sidestepping the unsafe window rather than proving it's safe to skip: [5](#0-4) 

No code path enforces that `on_idle` must run, or that `NativeDepositOf` rows are cleared, before a contract can be redeployed at the same address; the invariant "a contributor cannot receive more native refund than they deposited" is not upheld across a terminate→redeploy cycle at a reused address.

### Impact Explanation
A contributor's already-refunded native deposit can be counted again as refundable credit against a newly redeployed contract at the same address, allowing an attacker to drain native balance from the new contract's storage-deposit hold (funded by unrelated depositors of the new incarnation) up to the stale leftover amount — a direct violation of storage-deposit accounting and a path to over-crediting a contributor's native balance beyond what they actually deposited into the live contract.

### Likelihood Explanation
Preconditions are fully attacker/user-controlled and require no privilege: any signed account can instantiate with a deterministic salt, terminate, and immediately re-instantiate with the same salt in a subsequent transaction/block, well before `on_idle`'s lazy queue drain is guaranteed to execute (especially under block-weight pressure, a large deletion queue backlog, or if the attacker times the redeploy to occur in the very next block). This is a realistic, repeatable window rather than a theoretical race.

### Recommendation
Clear all `NativeDepositOf` rows for a contract account synchronously as part of `do_terminate` (or otherwise block re-instantiation at the same address until the deletion queue entry, including its `NativeDepositOf` rows, has been fully drained), rather than relying on the lazy `on_idle` cleanup which has no ordering guarantee relative to redeployment.

### Proof of Concept
Rust integration test in `substrate/frame/revive/src/tests/deposit_payment.rs`:
1. Instantiate `MultiContributorStorage` at address `A` with a fixed salt; have `ALICE` call `growStorage` so `NativeDepositOf[A][ALICE] = D > 0` and the native hold on `A` equals `D`.
2. Call `terminate` on the contract (beneficiary = some other account); assert the contract is gone (`get_contract_checked(&addr).is_none()`) but, without calling `on_idle`, assert `NativeDepositOf::<Test>::get(&account_id, &ALICE) == D` (still present).
3. Re-instantiate a fresh `MultiContributorStorage` at the same address/salt (skip `on_idle`); have a different funder `CHARLIE` grow storage so the new contract's hold is funded entirely by `CHARLIE`.
4. Trigger a refund path attributable to `ALICE` against the new contract (e.g., a storage-shrink operation crediting `ALICE`) and assert that `ALICE` receives a refund `> 0` even though `ALICE` contributed nothing to the new incarnation, and that cumulative refunds paid out across `A`'s lifetime (termination payout + this new refund) exceed cumulative deposits actually held by the live contracts — violating the "no refund without matching deposit" invariant.

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

**File:** substrate/frame/revive/src/lib.rs (L736-740)
```rust
	/// Terminated contracts that await lazy cleanup.
	///
	/// Each entry pairs a child trie ID with the contract account so that `on_idle` can
	/// drain both the child trie and any [`NativeDepositOf`] entries that named the contract
	/// as `holder`. Both can be arbitrarily large, so cleanup runs lazily in `on_idle`.
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

**File:** substrate/frame/revive/src/tests/deposit_payment.rs (L529-595)
```rust
/// Terminating a contract reaps its system account (native and PGAS EDs are burned by
/// `destroy_contract`, the manual consumer is decremented), and the `on_idle` deletion-queue
/// drain clears its [`NativeDepositOf`] rows. We charge a multi-contributor native deposit
/// first so the double map is genuinely populated and we can observe both rows disappear.
#[test_case(FixtureType::Solc)]
#[test_case(FixtureType::Resolc)]
fn destroy_contract_reaps_account_and_clears_native_deposit_map(fixture_type: FixtureType) {
	let (code, _) = compile_module_with_type("MultiContributorStorage", fixture_type).unwrap();
	ExtBuilder::default().build().execute_with(|| {
		Balances::set_balance(&ALICE, 100_000_000_000);
		Balances::set_balance(&CHARLIE, 100_000_000_000);

		let Contract { addr, account_id } =
			builder::bare_instantiate(Code::Upload(code)).build_and_unwrap_contract();

		// Two distinct payers grow distinct slots so that `NativeDepositOf[contract][_]` has
		// two rows once the deletion queue starts draining.
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

		assert!(NativeDepositOf::<Test>::get(&account_id, &ALICE) > 0);
		assert!(NativeDepositOf::<Test>::get(&account_id, &CHARLIE) > 0);
		assert!(System::account_exists(&account_id), "contract account is alive pre-terminate");

		assert_ok!(
			builder::bare_call(addr)
				.data(
					MultiContributorStorage::terminateCall { beneficiary: DJANGO_ADDR.0.into() }
						.abi_encode(),
				)
				.build()
				.result,
		);

		assert!(get_contract_checked(&addr).is_none(), "contract info should be gone");
		assert!(
			!System::account_exists(&account_id),
			"system account should be reaped once destroy_contract burns the EDs",
		);
		assert_eq!(Balances::balance(&account_id), 0);
		assert_eq!(Assets::balance(PGAS_ASSET_ID, &account_id), 0);

		// `NativeDepositOf` rows survive termination; they're cleared lazily by `on_idle`.
		assert!(NativeDepositOf::<Test>::get(&account_id, &ALICE) > 0);
		assert!(NativeDepositOf::<Test>::get(&account_id, &CHARLIE) > 0);
		assert_eq!(DeletionQueue::<Test>::iter().count(), 1, "contract is queued for deletion");

		Contracts::on_idle(System::block_number(), Weight::MAX);

		assert_eq!(
			DeletionQueue::<Test>::iter().count(),
			0,
			"deletion queue drained to completion",
		);
		assert_eq!(NativeDepositOf::<Test>::iter_prefix(&account_id).count(), 0);
	});
}
```

**File:** substrate/frame/revive/src/tests/pvm.rs (L445-486)
```rust
/// Check that contracts with the same account id have different trie ids.
/// Check the `Nonce` storage item for more information.
#[test]
fn instantiate_unique_trie_id() {
	let (binary, code_hash) = compile_module("self_destruct_by_precompile").unwrap();

	ExtBuilder::default().existential_deposit(500).build().execute_with(|| {
		let _ = <Test as Config>::Currency::set_balance(&ALICE, 1_000_000);
		Contracts::upload_code(
			RuntimeOrigin::signed(ALICE),
			binary.clone(),
			deposit_limit::<Test>(),
		)
		.unwrap();

		// Instantiate the contract and store its trie id for later comparison.
		let Contract { addr, .. } =
			builder::bare_instantiate(Code::Existing(code_hash)).build_and_unwrap_contract();
		let trie_id = get_contract(&addr).trie_id;

		// Try to instantiate it again without termination should yield an error.
		assert_err_ignore_postinfo!(
			builder::instantiate(code_hash).build(),
			<Error<Test>>::DuplicateContract,
		);

		// Terminate the contract.
		assert_ok!(builder::call(addr).build());

		// Drain `NativeDepositOf` rows before re-instantiating at the same address.
		Contracts::on_idle(System::block_number(), Weight::MAX);

		// Re-Instantiate after termination.
		Contracts::upload_code(RuntimeOrigin::signed(ALICE), binary, deposit_limit::<Test>())
			.unwrap();
		assert_ok!(builder::instantiate(code_hash).build());

		// Trie ids shouldn't match or we might have a collision
		assert_ne!(trie_id, get_contract(&addr).trie_id);
	});
}

```
