A valid analog of this vulnerability class exists in the Polkadot SDK's ERC20 XCM asset transactor.

### Title
Fee-on-transfer / non-standard ERC20 tokens cause accounting mismatch in `ERC20Transactor` - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

### Summary
`ERC20Transactor` is the XCM `TransactAsset` implementation that lets any ERC20 contract deployed on `pallet-revive` be moved via XCM by routing tokens through a shared `TransfersCheckingAccount`. Like the reported `BaseJackpot` bug, the transactor trusts the ERC20 contract's boolean return value as proof that the *exact* `amount` requested was moved, and credits/debits the XCM holding register with that same unadjusted `amount`. It never verifies the checking account's actual balance delta. Fee-on-transfer, rebasing, or otherwise non-conforming ERC20 tokens will silently desynchronize the on-chain checking-account balance from the amount the XCM executor believes it is holding.

### Finding Description
In `withdraw_asset_with_surplus`, the transactor calls `IERC20::transfer(checking_account, amount)` from the user, decodes the boolean return, and if `true`, unconditionally mints an `AssetsInHolding` credit of the full requested `amount`: [1](#0-0) 

Symmetrically, `deposit_asset_with_surplus` instructs the checking account to `transfer(beneficiary, amount)` for the full holding amount, again only checking the boolean return, never checking pre/post balances: [2](#0-1) 

If the token contract deducts a fee on transfer (or applies any transformation reducing the amount actually received), the checking account receives less than `amount`, but the XCM executor's internal holding register is credited with the full `amount` anyway. This is the exact "fee-on-transfer" root cause identified in the report: no pre-balance/post-balance comparison is performed to determine the amount actually received; the code only trusts the token's own success flag.

The transactor is generic over *any* contract address supplied as an `AccountKey20` junction in the XCM `Asset` location — it is not restricted to a pre-vetted allowlist of "safe" ERC20s in the code shown; the associated test deploys an arbitrary user-supplied contract and interacts with it purely via its address: [3](#0-2) 

(Note: I was not able to fully retrieve the `ERC20Matcher` implementation in `cumulus/parachains/runtimes/assets/common/src/lib.rs` before running out of search budget, so I cannot definitively confirm whether an allowlist/registration step exists at the runtime-config level that would restrict which ERC20 contracts can be used through this transactor. This is an open question that should be verified before treating the issue as fully unprivileged/permissionless.)

The related test `smart_contract_does_not_return_bool_fails` confirms the code path only guards against the "no bool returned" USDT-style problem (which causes a decode error and a safe XCM failure), but this does **not** address the fee-on-transfer / short-transfer class of issue, which is silent and does not revert: [4](#0-3) 

### Impact Explanation
Because the checking account is a shared pool serving every user's ERC20 withdraw/deposit operations for a given contract, an under-collection caused by a fee-on-transfer token creates a structural shortfall between the token balance actually held in the checking account and the aggregate amount the XCM executor's holding/accounting logic believes has been deposited over time. This can lead to:
- Later legitimate `deposit_asset` calls for that same token failing once the checking account balance is exhausted (denial of funds for other users of the same ERC20), or
- If the checking account happens to be over-funded from other flows, some users effectively receive value while others cannot later be paid out — an accounting insolvency for that specific ERC20 asset.

This is a real accounting bug in fund custody logic, analogous in root cause to the reported issue, though the concrete blast radius depends on whether arbitrary ERC20 contracts (attacker-deployable) can be routed through this transactor without allowlisting.

### Likelihood Explanation
Likelihood is contingent on the unresolved question above. If `ERC20Matcher`/registry restricts eligible contracts to a curated, pre-audited list of tokens (unlikely to include fee-on-transfer tokens), likelihood is low/trusted-role-gated, similar to the original report's "low risk" rating for BaseJackpot. If, as the test in `tests.rs` suggests, any deployed contract address can be targeted directly via `AccountKey20`, an unprivileged user could deploy a fee-on-transfer ERC20 and immediately exercise this path, making exploitation straightforward and self-triggerable.

### Recommendation
- In `withdraw_asset_with_surplus`, measure the checking account's ERC20 balance before and after the `transfer` call and credit `AssetsInHolding` with the actual delta rather than the requested `amount`.
- In `deposit_asset_with_surplus`, similarly verify the beneficiary's (or checking account's) balance delta matches the intended transfer, and propagate any shortfall back into holding rather than assuming full success.
- If not already present, ensure `ERC20Matcher` enforces an explicit registry/allowlist of vetted ERC20 contracts (rejecting fee-on-transfer, rebasing, or otherwise non-standard tokens) before they can be routed through `ERC20Transactor`.

### Proof of Concept
A full PoC requires confirming whether arbitrary contracts can be targeted (unresolved above). Conceptually:
1. Deploy an ERC20 contract on `pallet-revive` that returns `true` from `transfer`/`transferFrom` but deducts a fee (e.g., burns 5%) from the transferred amount, sending only 95% to the recipient.
2. Submit an XCM message with `withdraw_asset` for this token via `PolkadotXcm::execute`, mirroring the pattern in `withdraw_and_deposit_erc20s`.
3. Observe that `AssetsInHolding` is credited with the full requested `amount`, while the `TransfersCheckingAccount`'s actual ERC20 balance only increased by 95% of `amount` — confirmed via `Revive as fungibles::Inspect::balance(erc20_address, &checking_account)` before/after, as done in the existing test at lines 1896–1927.
4. Repeat/chain such withdrawals to demonstrate the checking account's real balance falls persistently behind the sum of holding-register credits issued for that asset. [5](#0-4)

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L185-207)
```rust
		if let Ok(return_value) = result {
			tracing::trace!(target: "xcm::transactor::erc20::withdraw", ?return_value, "Return value by withdraw_asset");
			if return_value.did_revert() {
				tracing::debug!(target: "xcm::transactor::erc20::withdraw", "ERC20 contract reverted");
				Err(XcmError::FailedToTransactAsset("ERC20 contract reverted"))
			} else {
				let is_success = IERC20::transferCall::abi_decode_returns_validate(&return_value.data).map_err(|error| {
					tracing::debug!(target: "xcm::transactor::erc20::withdraw", ?error, "ERC20 contract result couldn't decode");
					XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")
				})?;
				if is_success {
					tracing::trace!(target: "xcm::transactor::erc20::withdraw", "ERC20 contract was successful");
					Ok((
						AssetsInHolding::new_from_fungible_credit(
							what.id.clone(),
							Box::new(Erc20Credit(amount)),
						),
						surplus,
					))
				} else {
					tracing::debug!(target: "xcm::transactor::erc20::withdraw", "contract transfer failed");
					Err(XcmError::FailedToTransactAsset("ERC20 contract transfer failed"))
				}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L253-298)
```rust
		let data = IERC20::transferCall { to: address, value: EU256::from(amount) }.abi_encode();
		let weight_limit = WeightLimit::get();
		let ContractResult { result, weight_consumed, storage_deposit, .. } =
			pallet_revive::Pallet::<T>::bare_call(
				OriginFor::<T>::signed(TransfersCheckingAccount::get()),
				asset_contract_id,
				U256::zero(),
				TransactionLimits::WeightAndDeposit {
					weight_limit,
					deposit_limit: StorageDepositLimit::get(),
				},
				data,
				&ExecConfig::new_substrate_tx(),
			);
		// We need to return this surplus for the executor to allow refunding it.
		let surplus = weight_limit.saturating_sub(weight_consumed);
		tracing::trace!(target: "xcm::transactor::erc20::deposit", ?weight_consumed, ?surplus, ?storage_deposit);
		if let Ok(return_value) = result {
			tracing::trace!(target: "xcm::transactor::erc20::deposit", ?return_value, "Return value");
			if return_value.did_revert() {
				tracing::debug!(target: "xcm::transactor::erc20::deposit", "Contract reverted");
				Err((what, XcmError::FailedToTransactAsset("ERC20 contract reverted")))
			} else {
				match IERC20::transferCall::abi_decode_returns_validate(&return_value.data) {
					Ok(true) => {
						tracing::trace!(target: "xcm::transactor::erc20::deposit", "ERC20 contract was successful");
						Ok(surplus)
					},
					Ok(false) => {
						tracing::debug!(target: "xcm::transactor::erc20::deposit", "contract transfer failed");
						Err((
							what,
							XcmError::FailedToTransactAsset("ERC20 contract transfer failed"),
						))
					},
					Err(error) => {
						tracing::debug!(target: "xcm::transactor::erc20::deposit", ?error, "ERC20 contract result couldn't decode");
						Err((
							what,
							XcmError::FailedToTransactAsset(
								"ERC20 contract result couldn't decode",
							),
						))
					},
				}
			}
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs (L1864-1929)
```rust
#[test]
fn withdraw_and_deposit_erc20s() {
	let sender: AccountId = ALICE.into();
	let beneficiary: AccountId = BOB.into();
	let revive_account = pallet_revive::Pallet::<Runtime>::account_id();
	let checking_account =
		asset_hub_westend_runtime::xcm_config::ERC20TransfersCheckingAccount::get();
	let initial_wnd_amount = 100_000_000_000_000_000u128;
	sp_tracing::init_for_tests();

	ExtBuilder::<Runtime>::default().build().execute_with(|| {
		// Bring the revive account to life.
		assert_ok!(Balances::mint_into(&revive_account, initial_wnd_amount));
		// Fund all accounts involved.
		assert_ok!(Balances::mint_into(&sender, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&beneficiary, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&checking_account, initial_wnd_amount));

		let code = compile_module_with_type("MyToken", FixtureType::Resolc)
			.expect("compile ERC20")
			.0;

		let initial_amount_u256 = U256::from(1_000_000_000_000u128);
		let constructor_data = sol_data::Uint::<256>::abi_encode(&initial_amount_u256);
		let Contract { addr: erc20_address, .. } = bare_instantiate(&sender, code)
			.transaction_limits(TransactionLimits::WeightAndDeposit {
				weight_limit: Weight::from_parts(500_000_000_000, 10 * 1024 * 1024),
				deposit_limit: Balance::MAX,
			})
			.data(constructor_data)
			.build_and_unwrap_contract();

		let sender_balance_before = <Balances as fungible::Inspect<_>>::balance(&sender);

		let erc20_transfer_amount = 100u128;
		let wnd_amount_for_fees = 10_000_000_000_000u128;
		// Actual XCM to execute locally.
		let message = Xcm::<RuntimeCall>::builder()
			.withdraw_asset((Parent, wnd_amount_for_fees))
			.pay_fees((Parent, wnd_amount_for_fees))
			.withdraw_asset((
				AccountKey20 { key: erc20_address.into(), network: None },
				erc20_transfer_amount,
			))
			.deposit_asset(AllCounted(1), beneficiary.clone())
			.refund_surplus()
			.deposit_asset(AllCounted(1), sender.clone())
			.build();
		assert_ok!(PolkadotXcm::execute(
			RuntimeOrigin::signed(sender.clone()),
			Box::new(VersionedXcm::V5(message)),
			Weight::from_parts(600_000_000_000, 15 * 1024 * 1024),
		));

		// Revive is not taking any fees.
		let sender_balance_after = <Balances as fungible::Inspect<_>>::balance(&sender);
		// Balance after is larger than the difference between balance before and transferred
		// amount because of the refund.
		assert!(sender_balance_after > sender_balance_before - wnd_amount_for_fees);

		// Beneficiary receives the ERC20.
		let beneficiary_amount =
			<Revive as fungibles::Inspect<_>>::balance(erc20_address, &beneficiary);
		assert_eq!(beneficiary_amount, erc20_transfer_amount);
	});
}
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs (L2019-2073)
```rust
// Here the contract returns a number but because it can be cast to true
// it still succeeds.
#[test]
fn smart_contract_does_not_return_bool_fails() {
	let sender: AccountId = ALICE.into();
	let beneficiary: AccountId = BOB.into();
	let revive_account = pallet_revive::Pallet::<Runtime>::account_id();
	let checking_account =
		asset_hub_westend_runtime::xcm_config::ERC20TransfersCheckingAccount::get();
	let initial_wnd_amount = 10_000_000_000_000u128;

	ExtBuilder::<Runtime>::default().build().execute_with(|| {
		// Bring the revive account to life.
		assert_ok!(Balances::mint_into(&revive_account, initial_wnd_amount));

		// Fund all accounts involved.
		assert_ok!(Balances::mint_into(&sender, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&beneficiary, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&checking_account, initial_wnd_amount));

		// This contract implements the ERC20 interface for `transfer` except it returns a uint256.
		let code = compile_module_with_type("MyTokenFake", FixtureType::Resolc)
			.expect("compile ERC20")
			.0;

		let initial_amount_u256 = U256::from(1_000_000_000_000u128);
		let constructor_data = sol_data::Uint::<256>::abi_encode(&initial_amount_u256);

		let Contract { addr: non_erc20_address, .. } = bare_instantiate(&sender, code)
			.transaction_limits(TransactionLimits::WeightAndDeposit {
				weight_limit: Weight::from_parts(500_000_000_000, 10 * 1024 * 1024),
				deposit_limit: Balance::MAX,
			})
			.data(constructor_data)
			.build_and_unwrap_contract();

		let wnd_amount_for_fees = 1_000_000_000_000u128;
		let erc20_transfer_amount = 100u128;
		let message = Xcm::<RuntimeCall>::builder()
			.withdraw_asset((Parent, wnd_amount_for_fees))
			.pay_fees((Parent, wnd_amount_for_fees))
			.withdraw_asset((
				AccountKey20 { key: non_erc20_address.into(), network: None },
				erc20_transfer_amount,
			))
			.deposit_asset(AllCounted(1), beneficiary.clone())
			.build();
		// Execution fails but doesn't panic.
		assert!(PolkadotXcm::execute(
			RuntimeOrigin::signed(sender.clone()),
			Box::new(VersionedXcm::V5(message)),
			Weight::from_parts(2_500_000_000, 220_000),
		)
		.is_err());
	});
```
