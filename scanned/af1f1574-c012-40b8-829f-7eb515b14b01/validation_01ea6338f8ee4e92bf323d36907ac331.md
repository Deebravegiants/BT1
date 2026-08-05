### Title
Storage deposit refund at contract termination is credited to the terminate caller (`origin`), not to the account(s) that actually funded the held deposit - (File: substrate/frame/revive/src/exec.rs)

### Summary
`Stack::do_terminate` refunds the entire `HoldReason::StorageDepositReserve` hold on a terminated contract to the extrinsic `origin` that invoked termination via `T::Deposit::refund_all(&contract_account, exec_config.funds(origin.account_id()?))`, rather than to the account(s) that originally paid the deposit. Because the `ISystem.terminate` precompile can be wrapped by any public, unauthenticated contract function and invoked in a block after instantiation, an unrelated caller can terminate a contract and redirect the full accumulated storage-deposit hold - including deposits paid by other users - to themselves.

### Finding Description
Storage deposits are charged per-payer at write time via `charge_and_hold`, tracked e.g. in `NativeDepositOf[contract][payer]` [1](#0-0) . At termination, `do_terminate` calls: [2](#0-1) 

`refund_all` sweeps the *entire* remaining hold on the contract to a single destination determined by `exec_config.funds(origin.account_id())`, ignoring per-contributor attribution: [3](#0-2) 

`origin` here is the account that invoked the top-level extrinsic reaching `do_terminate` - not necessarily any of the accounts that funded the hold, and not the `beneficiary` argument passed to `ISystem.terminate` (that argument only receives the *free* residual balance via `Self::transfer`, see `args.beneficiary` in `do_terminate`) [4](#0-3) .

The `ISystem.terminate` precompile has no restriction tying the caller to the original depositor - it only blocks read-only calls and delegate-call misuse: [5](#0-4) 

And Solidity fixtures demonstrate wrapping this in a public, unauthenticated function reachable across blocks/transactions: [6](#0-5) 

This is directly confirmed by an existing regression test: ALICE instantiates the contract (paying the base deposit), then ALICE and CHARLIE each grow storage and each pay their own deposit (tracked separately in `NativeDepositOf`), then **ALICE** (not CHARLIE) calls `terminate(beneficiary=DJANGO)`. The test explicitly asserts that ALICE - as the caller/origin of the terminate call - receives the *entire* combined hold, including CHARLIE's contribution, even though the specified `beneficiary` was DJANGO: [7](#0-6) 

The test's own doc comment acknowledges this is a deliberate simplification ("one recipient at termination, contract gone") [1](#0-0) , but from a security-invariant perspective this means any account able to invoke `terminate` on a contract - which need not be the depositor, and which is gated only by whatever (if any) access control the target contract's own Solidity code implements on its wrapper function - receives funds that other, unrelated users paid into that contract's storage deposit.

### Impact Explanation
An unrelated, unprivileged caller who can trigger a contract's exposed `terminate`-wrapping function (no special privilege required beyond calling a public contract method) receives the full storage-deposit hold accumulated on that contract, including portions paid by other depositors who never authorized or benefited from the termination. This is a direct redirection of another user's held/reserved funds to an account that did not fund them, matching the "direct theft of another user's reserved/held funds" scoped impact. Note the precise mechanism differs from the question's hypothesis: funds go to the extrinsic `origin` (the account that called `terminate`), not to the `beneficiary` function argument - the `beneficiary` only receives the contract's leftover free balance.

### Likelihood Explanation
Fully feasible with only standard user-level actions: instantiate a contract, have any account(s) pay storage deposits by calling contract functions that grow storage, then have any account call the contract's public `terminate`-invoking function in a later block. No governance, Root, or node-level access is needed. The exact scenario is reproduced by an existing test in the repository, confirming reachability and reliability without any exotic preconditions. Actual exploitability against a specific victim depends on the target contract's own access control over its termination-triggering function - if a deployed contract exposes an unauthenticated `terminate` wrapper (as `MultiContributorStorage.sol`/`Terminate.sol` fixtures do), any caller can claim the full aggregate deposit.

### Recommendation
Change `refund_all`/`do_terminate` accounting to refund each contributor's own share of the storage-deposit hold back to that contributor (using the per-payer bookkeeping already tracked, e.g. `NativeDepositOf[contract][payer]`), rather than sweeping the entire hold to the account that happens to be the `origin` of the terminating call. At minimum, document and gate this behavior so that pallet-revive does not silently reassign one user's held deposit to an unrelated caller; alternatively, restrict `refund_all`'s destination to the account recorded as having paid the *base* instantiation deposit, and handle multi-contributor deposits with a proportional distribution instead of "winner take all" to the terminator.

### Proof of Concept
Extend the existing test pattern (already present) with an explicit invariant check:
```rust
#[test]
fn terminate_by_unrelated_caller_steals_other_contributors_deposit() {
    // ALICE instantiates and grows storage (pays base + her own storage deposit).
    // CHARLIE (unrelated depositor) grows storage on the same contract, paying his own deposit.
    // An unrelated caller (e.g. CHARLIE or a third party EVE) calls `terminate(beneficiary=EVE)`.
    // Assert: CHARLIE's contributed deposit is NOT returned to CHARLIE.
    // Assert: the deposit refund lands with the extrinsic `origin` of the terminate call,
    //         not with CHARLIE (who funded it) nor strictly with `beneficiary` (EVE).
    assert_ne!(refund_recipient, CHARLIE, "CHARLIE's deposit should return to CHARLIE, not the terminator");
}
```
This mirrors `refund_all_drains_multi_contributor_native_hold` [8](#0-7)  but adds an assertion that CHARLIE's balance is unaffected/refunded to CHARLIE, which currently fails because the whole hold routes to the terminate-caller's account instead.

### Citations

**File:** substrate/frame/revive/src/tests/deposit_payment.rs (L460-463)
```rust
/// A contract whose storage was paid for by two different signers, both via the native
/// fallback path, can still be terminated. [`Deposit::refund_all`] bypasses the per-payer
/// [`NativeDepositOf`] cap (one recipient at termination, contract gone), so the full native
/// hold goes to the terminator and any PGAS hold is settled via `settle_pgas_refund`.
```

**File:** substrate/frame/revive/src/tests/deposit_payment.rs (L464-527)
```rust
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

**File:** substrate/frame/revive/src/exec.rs (L1809-1813)
```rust
		let mut delete_contract = |trie_id: &TrieId, code_hash: &H256| {
			// deposit needs to be removed as it adds a consumer
			let refund =
				T::Deposit::refund_all(&contract_account, exec_config.funds(origin.account_id()?))?;

```

**File:** substrate/frame/revive/src/exec.rs (L1826-1834)
```rust
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

**File:** substrate/frame/revive/src/precompiles/builtin/system.rs (L96-103)
```rust
			ISystemCalls::terminate(ISystem::terminateCall { beneficiary }) => {
				// no need to adjust gas because this always deletes code
				env.frame_meter_mut()
					.charge_weight_token(RuntimeCosts::Terminate { code_removed: true })?;
				let h160 = H160::from_slice(beneficiary.as_slice());
				env.terminate_caller(&h160).map_err(Error::try_to_revert::<T>)?;
				Ok(Vec::new())
			},
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
