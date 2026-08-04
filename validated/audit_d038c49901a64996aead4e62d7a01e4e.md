## Finding

The Sudoswap-style bug — trusting an ERC20 token transfer without checking the actual balance received — has a direct analog in the `ERC20Transactor` used by Asset Hub Westend's XCM configuration.

### Title
Missing balance verification when transferring ERC20 tokens in `ERC20Transactor` - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `ERC20Transactor::deposit_asset_with_surplus` move ERC20 tokens between a user account and a shared `TransfersCheckingAccount` by calling the token's `transfer()` function and trusting only its revert status / boolean return value. Neither function verifies that the checking/beneficiary account's balance actually changed by the requested `amount`, exactly mirroring the LSSVMPairERC20 flaw where the "direct transfer" branch skipped a before/after balance check.

### Finding Description
In `withdraw_asset_with_surplus`, the transactor calls `IERC20::transferCall` from the user to `TransfersCheckingAccount`, and on a non-reverted `true` return it unconditionally credits the XCM holding register with the full requested `amount` via `AssetsInHolding::new_from_fungible_credit`, without checking the checking account's actual balance delta. [1](#0-0) 

Symmetrically, `deposit_asset_with_surplus` transfers `amount` from `TransfersCheckingAccount` to the beneficiary and, again, only inspects the revert flag and the boolean ABI return value of `transfer()` before treating the deposit as fully successful — with no check that the beneficiary's balance increased by `amount`. [2](#0-1) 

This is configured live in the `AssetTransactors` tuple for Asset Hub Westend's `xcm_executor::Config`, so it is reachable by any account able to submit `WithdrawAsset`/`DepositAsset` XCM instructions referencing an `AccountKey20`-addressed ERC20 asset (e.g. via `PolkadotXcm::execute` or an incoming XCM program), as demonstrated by the existing test that exercises this exact path. [3](#0-2) [4](#0-3) 

If a pallet-revive ERC20 contract implements fee-on-transfer, rebasing, or other non-standard `transfer()` semantics (returning `true` while moving a different amount than requested — the same class of token behavior called out in the Sudoswap report and the Qubit Finance hack), the transactor's holding-register accounting (`amount`) will diverge from the checking account's real token balance.

### Impact Explanation
Because `TransfersCheckingAccount` is a single shared pot for all ERC20 XCM transfers on the chain, a repeated mismatch between credited holding amounts and real balances can drain or desynchronize the checking account relative to what the runtime believes it holds, potentially allowing a user to withdraw more real tokens than they deposited (or vice versa) across multiple XCM messages using a non-standard ERC20 contract they control. This is a shared-resource accounting bug, not merely a self-inflicted loss for the token deployer.

### Likelihood Explanation
Requires only that an unprivileged user register/use a non-standard (fee-on-transfer or rebasing) ERC20 contract as the asset in an XCM message — no privileged role is needed, matching Sudoswap's acknowledged threat model ("pair creators would have to willingly deploy... a token using non-standard ERC20 behavior"). Likelihood is therefore comparable to the original finding: low-to-medium, gated on the existence/adoption of such tokens, but the code path itself is reachable without any trust assumption beyond controlling the ERC20 contract.

### Recommendation
In both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus`, read the relevant account's ERC20 balance (via a `balanceOf` call) before and after the `transfer()` call, and use the observed delta — rather than the caller-supplied `amount` — when constructing the `AssetsInHolding` credit or when deciding the deposit succeeded. Reject/short-transact if the observed delta does not match the requested amount, similar to what Spearbit recommended for `LSSVMPairERC20::_validateTokenInput()`.

### Proof of Concept
1. Deploy (or point the asset id at) an ERC20 contract on pallet-revive whose `transfer()` deducts a fee, e.g. transferring `amount * 99 / 100` while still returning `true`.
2. Submit an XCM message via `PolkadotXcm::execute` with `WithdrawAsset` for that ERC20 asset with `amount = 100`.
3. `withdraw_asset_with_surplus` calls `transfer(checking_account, 100)`; the checking account actually receives `99`, but the code checks only `is_success == true` and credits `AssetsInHolding` with the full `100`.
4. Follow with `DepositAsset` to a beneficiary; `deposit_asset_with_surplus` will attempt to move `100` out of the checking account for this and other pending transfers, progressively depleting the checking account of real tokens relative to what the runtime's holding-register accounting believes was deposited.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L185-204)
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

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L221-246)
```rust
/// Transactor for ERC20 tokens.
pub type ERC20Transactor = assets_common::ERC20Transactor<
	// We need this for accessing pallet-revive.
	Runtime,
	// The matcher for smart contracts.
	assets_common::ERC20Matcher,
	// How to convert from a location to an account id.
	LocationToAccountId,
	// The maximum gas that can be used by a standard ERC20 transfer.
	ERC20TransferGasLimit,
	// The maximum storage deposit that can be used by a standard ERC20 transfer.
	ERC20TransferStorageDepositLimit,
	// We're generic over this so we can't escape specifying it.
	AccountId,
	// Checking account for ERC20 transfers.
	ERC20TransfersCheckingAccount,
>;

/// Means for transacting assets on this chain.
pub type AssetTransactors = (
	FungibleTransactor,
	FungiblesTransactor,
	ForeignFungiblesTransactor,
	UniquesTransactor,
	ERC20Transactor,
);
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs (L1931-1968)
```rust
#[test]
fn non_existent_erc20_will_error() {
	let sender: AccountId = ALICE.into();
	let beneficiary: AccountId = BOB.into();
	let revive_account = pallet_revive::Pallet::<Runtime>::account_id();
	let checking_account =
		asset_hub_westend_runtime::xcm_config::ERC20TransfersCheckingAccount::get();
	let initial_wnd_amount = 10_000_000_000_000u128;
	// We try to withdraw an ERC20 token but the address doesn't exist.
	let non_existent_contract_address = [1u8; 20];

	ExtBuilder::<Runtime>::default().build().execute_with(|| {
		// Bring the revive account to life.
		assert_ok!(Balances::mint_into(&revive_account, initial_wnd_amount));
		// Fund all accounts involved.
		assert_ok!(Balances::mint_into(&sender, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&beneficiary, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&checking_account, initial_wnd_amount));

		let wnd_amount_for_fees = 1_000_000_000_000u128;
		let erc20_transfer_amount = 100u128;
		let message = Xcm::<RuntimeCall>::builder()
			.withdraw_asset((Parent, wnd_amount_for_fees))
			.pay_fees((Parent, wnd_amount_for_fees))
			.withdraw_asset((
				AccountKey20 { key: non_existent_contract_address, network: None },
				erc20_transfer_amount,
			))
			.deposit_asset(AllCounted(1), beneficiary.clone())
			.build();
		// Execution fails but doesn't panic.
		assert!(PolkadotXcm::execute(
			RuntimeOrigin::signed(sender.clone()),
			Box::new(VersionedXcm::V5(message)),
			Weight::from_parts(2_500_000_000, 120_000),
		)
		.is_err());
	});
```
