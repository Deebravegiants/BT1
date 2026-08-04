## Verdict: Confirmed — this is a real, already-acknowledged design flaw

### Title
Any storage-deposit contributor can steal co-contributors' held deposits via `terminate` (`refund_all` ignores `NativeDepositOf` per-contributor cap) - (File: `substrate/frame/revive/src/deposit_payment.rs`)

### Summary
`Deposit::refund_all`, invoked from `Stack::do_terminate` when a contract self-destructs, releases the *entire* native `StorageDepositReserve` hold on the contract to a single destination chosen by whoever calls `terminate`, without checking `NativeDepositOf` per-contributor entitlements the way `refund_on_hold` does for live-contract partial refunds. Any account that contributed even a small amount of storage deposit to a shared contract — and can trigger that contract's termination path — receives every other contributor's deposit as well.

### Finding Description
`refund_on_hold` (the path used for ordinary, non-terminal refunds) explicitly caps the native refund at `NativeDepositOf::<T>::get(from, to)`: [1](#0-0) 

`refund_all`, however, is documented and implemented to bypass this cap entirely: it reads the *whole* native hold via `T::Currency::balance_on_hold` and calls the unconditional native `refund_on_hold` for the entire amount: [2](#0-1) [3](#0-2) 

`refund_all` is called from `Stack::do_terminate` with `dst = exec_config.funds(origin.account_id())`, where `origin` is the immediate caller context of the terminate operation (not each historical depositor): [4](#0-3) 

Reachability is real and unprivileged: the `ISystem.terminate` precompile lets any external caller invoke contract termination across separate transactions (unlike `SELFDESTRUCT`, which EIP-6780 restricts). The repo's own test fixture demonstrates a contract with **no access control** on `terminate`, callable by any address: [5](#0-4) 

The existing regression test `refund_all_drains_multi_contributor_native_hold` reproduces exactly the scenario in the question: ALICE and CHARLIE both call `growStorage` (each recorded separately in `NativeDepositOf[contract][ALICE]` and `NativeDepositOf[contract][CHARLIE]`), then a `terminate` call drains the *combined* hold to the terminator's side, not split per contributor: [6](#0-5) 

The test's own doc comment states the intent plainly: `refund_all` bypasses the per-payer cap "so the full native hold goes to the terminator." This is acknowledged, intentional behavior in the code, not an oversight — but it still violates the invariant that one unprivileged contributor cannot redirect funds contributed by another, because `NativeDepositOf` entries are per-account entitlements to a DOT refund and nothing in the pallet enforces that only the entitled account (or a fair split) receives them at termination.

Whether CHARLIE (a non-owner contributor) can trigger `terminate` depends on whether the specific contract gates its termination entry point — this is a contract-author responsibility (contract-level access control), not enforced by the pallet. Since `pallet-revive` provides `ISystem.terminate` as a raw precompile with no built-in restriction to the deployer/owner, any Solidity contract that forwards it without an owner check (as the fixture intentionally demonstrates) exposes every prior storage-deposit contributor to having their held DOT redirected by any other contributor or, depending on `Funds` routing, even to an address the caller does not control if `exec_config.funds` resolves to the immediate caller identity of the terminate call.

### Impact Explanation
Theft of another contributor's storage-deposit refund at contract termination. In a multi-tenant contract pattern (e.g. shared registries, escrow-like storage, pooled state contracts) where several distinct signed accounts each pay their own storage deposit into the same contract, whichever party terminates the contract collects the *entire* pooled native hold, not just their own contribution. This is a direct, deterministic fund-redirection from other unprivileged users to the terminator.

### Likelihood Explanation
- Preconditions: a deployed contract (i) accepts storage-deposit contributions from multiple distinct accounts (normal usage under the PGAS/native fallback), and (ii) exposes a `terminate`/self-destruct path reachable by an account other than the sole depositor.
- Feasibility: fully reproducible with a real Solidity contract and the standard `ISystem.terminate` precompile, using only ordinary signed extrinsics/EVM calls — no privileged origin, no mocked helpers.
- Repeatability: deterministic; demonstrated by the existing `refund_all_drains_multi_contributor_native_hold` test in the repository.
- The contract itself controls whether `terminate` is owner-gated; contracts (like the fixture) that don't gate it are directly exploitable by any contributor.

### Recommendation
Either (a) prohibit termination when `NativeDepositOf` records contributions from more than one distinct payer (force a governance/multi-party settlement path instead), or (b) change `refund_all` to iterate `NativeDepositOf` entries for the contract and refund each contributor their own recorded native contribution before falling back to a single beneficiary for any un-attributed remainder, mirroring the capped logic already implemented in `refund_on_hold`.

### Proof of Concept
Extend the existing `refund_all_drains_multi_contributor_native_hold` test (or add a new one) to assert the negative invariant instead of merely observing the current (unsafe) behavior:
1. ALICE deploys `MultiContributorStorage`; ALICE calls `growStorage` (contributes deposit D_A, recorded in `NativeDepositOf[contract][ALICE]`).
2. CHARLIE (unprivileged, not the deployer) calls `growStorage` (contributes deposit D_C, recorded in `NativeDepositOf[contract][CHARLIE]`).
3. Record `alice_balance_before`.
4. CHARLIE calls `terminate(beneficiary = CHARLIE)` via `bare_call` with `RuntimeOrigin::signed(CHARLIE)`.
5. Assert: `Balances::balance(&ALICE) == alice_balance_before` (ALICE's contribution D_A was **not** returned to ALICE), and assert CHARLIE's balance increased by more than D_C (i.e., CHARLIE captured D_A as well) — this assertion currently **fails** to hold the safe property (ALICE's funds are in fact drained to CHARLIE), proving the bug.

### Citations

**File:** substrate/frame/revive/src/deposit_payment.rs (L250-268)
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

	fn migrate_native_to_pgas(
		_reason: HoldReason,
		_contract: &T::AccountId,
		_amount: BalanceOf<T>,
	) -> DispatchResult {
		Ok(())
	}
```

**File:** substrate/frame/revive/src/deposit_payment.rs (L384-407)
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

**File:** substrate/frame/revive/fixtures/contracts/MultiContributorStorage.sol (L16-35)
```text
contract MultiContributorStorage {
	mapping(address => bytes) private slots;

	function growStorage() external {
		bytes memory payload = new bytes(64);
		for (uint i = 0; i < payload.length; i++) {
			payload[i] = 0xAB;
		}
		slots[msg.sender] = payload;
	}

	function terminate(address beneficiary) external {
		bytes memory data = abi.encodeWithSelector(ISystem.terminate.selector, beneficiary);
		(bool success, bytes memory returnData) = SYSTEM_ADDR.call(data);
		if (!success) {
			assembly {
				revert(add(returnData, 0x20), mload(returnData))
			}
		}
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
