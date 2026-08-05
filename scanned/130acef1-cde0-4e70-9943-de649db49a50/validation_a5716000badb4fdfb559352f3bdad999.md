## Analysis

The vulnerability class described in the DODO report — code that assumes every ERC20 contract's `transfer`/`transferFrom` returns a boolean, causing legitimate void-return tokens (e.g. USDT-style contracts) to be treated as failed even when the transfer succeeded — has a direct analog in this repository's `ERC20Transactor`, the XCM `TransactAsset` implementation used to bridge Solidity ERC20 tokens (deployed via `pallet_revive`) across chains.

### Title
Boolean-Return Assumption in `ERC20Transactor` Breaks Cross-Chain Transfers for Void-Return ERC20 Tokens - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` invoke a target contract's `transfer(address,uint256)` via `pallet_revive::Pallet::<T>::bare_call`, then strictly ABI-decode the return data as a `bool` using `IERC20::transferCall::abi_decode_returns_validate`. Any Solidity ERC20 contract that (like real-world USDT) returns `void` instead of `bool` on success will fail this decode step, and the transactor treats a successful transfer as a fatal error, aborting the whole XCM instruction.

### Finding Description
In `withdraw_asset_with_surplus`, after calling the token contract's `transfer`, the code does: [1](#0-0) 
and analogously in `deposit_asset_with_surplus`: [2](#0-1) 

If `return_value.data` is empty (a `void` return, as real USDT and several other production ERC20 tokens use), `abi_decode_returns_validate` fails to decode a `bool`, and the code maps this to `XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")` — even though the underlying transfer actually succeeded on-chain.

Crucially, there is no allowlist restricting which contracts can be used as ERC20 assets here — `ERC20Matcher` matches *any* `AccountKey20` location: [3](#0-2) 
So any unprivileged user can deploy a void-return-style ERC20 contract to `pallet_revive` and immediately hit this bug when attempting to use it as an XCM asset — no special/trusted role required.

The maintainers' own test suite confirms the transactor rejects any non-standard return path — including a contract that returns a non-bool type — as an unrecoverable failure rather than gracefully handling it: [4](#0-3) 
There is no equivalent handling for a `void`-return contract specifically, meaning any real-world USDT-clone deployed on `pallet_revive` cannot be bridged through this mechanism at all.

### Impact Explanation
`WithdrawAsset`/`DepositAsset` XCM instructions in this executor are wrapped in `Config::TransactionalProcessor::process`, which for FRAME runtimes rolls back all storage changes (including the pallet_revive contract's internal token-transfer state) whenever the closure returns `Err`: [5](#0-4) 
This means the practical impact mirrors the original report: **transaction failures** and **user cost** (wasted weight/fees paid for the XCM message), rather than fund loss, because the rollback undoes the underlying successful transfer. However, this makes the `ERC20Transactor` **permanently unusable** for any void-return ERC20 token — a class of tokens that includes some of the most widely used real-world tokens (USDT-style contracts) — denying legitimate cross-chain transfers indefinitely for that asset.

### Likelihood Explanation
High for the affected asset class: any unprivileged user can deploy a void-return ERC20 contract on `pallet_revive` (no permission needed, per the unrestricted `ERC20Matcher`), and any attempt to bridge such a token through `ERC20Transactor` deterministically fails on every call, both for `withdraw_asset_with_surplus` (source-side) and `deposit_asset_with_surplus` (destination-side).

### Recommendation
Do not assume a strict ABI-encoded `bool` return from `transfer`/`transferFrom`. Follow the same "safe transfer" pattern recommended in the original report: treat an empty return (`return_value.data.is_empty()`) as success (mirroring OpenZeppelin's `SafeERC20` handling), only decoding a `bool` when return data is non-empty, and only treating an explicit `false`/non-decodable-but-non-empty result as failure.

### Proof of Concept
1. Deploy (via `pallet_revive`) a minimal ERC20 contract whose `transfer(address,uint256)` mutates balances but declares `function transfer(address,uint256) external` with no return value (void), matching real USDT's ABI.
2. Register/reference this contract's `H160` address as an XCM asset (no special permission needed since `ERC20Matcher`/`IsLocalAccountKey20` accepts any `AccountKey20` location).
3. Execute an XCM program that does `WithdrawAsset`/`DepositAsset` for this asset, as in the existing test harness: [6](#0-5) 
4. Observe that `bare_call` succeeds and the transfer executes, but `abi_decode_returns_validate(&return_value.data)` fails on the empty return, causing `XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")` and `Outcome::Incomplete`/`is_err()`, exactly as the existing `smart_contract_does_not_return_bool_fails` test demonstrates for a non-bool return.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L185-194)
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-297)
```rust
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L157-160)
```rust
/// [`xcm_executor::traits::MatchesFungibles`] implementation that matches
/// ERC20 tokens.
pub type ERC20Matcher =
	MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>;
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs (L1971-2017)
```rust
#[test]
fn smart_contract_not_erc20_will_error() {
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

		let (code, _) = compile_module("dummy").unwrap();

		let Contract { addr: non_erc20_address, .. } = bare_instantiate(&sender, code)
			.transaction_limits(TransactionLimits::WeightAndDeposit {
				weight_limit: Weight::from_parts(500_000_000_000, 10 * 1024 * 1024),
				deposit_limit: Balance::MAX,
			})
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
			Weight::from_parts(2_500_000_000, 120_000),
		)
		.is_err());
	});
}
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs (L2019-2074)
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
}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L946-970)
```rust
		match instr {
			WithdrawAsset(assets) => {
				self.ensure_can_subsume_assets(assets.len())?;
				Config::TransactionalProcessor::process(|| {
					let origin = self.origin_ref().ok_or(XcmError::BadOrigin)?;
					let mut total_surplus = Weight::zero();
					let mut withdrawn = AssetsInHolding::new();
					// Take `assets` from the origin account (on-chain)...
					for asset in assets.inner() {
						let (credit, surplus) = Config::AssetTransactor::withdraw_asset_with_surplus(
							asset,
							origin,
							Some(&self.context),
						)?;
						withdrawn.subsume_assets(credit);
						// If we have some surplus, aggregate it.
						total_surplus.saturating_accrue(surplus);
					}
					// ...and place into holding.
					self.holding.subsume_assets(withdrawn);
					// Credit the total surplus.
					self.total_surplus.saturating_accrue(total_surplus);
					Ok(())
				})
			},
```
