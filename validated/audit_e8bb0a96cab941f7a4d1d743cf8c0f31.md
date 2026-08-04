### Title
ERC20Transactor assumes exact requested amount is transferred by arbitrary ERC20 contracts, enabling shared-checking-account balance-shortfall DoS analogous to stETH rounding issue - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

### Summary
`ERC20Transactor` bridges XCM `TransactAsset` semantics to arbitrary `pallet-revive` ERC20 contracts by calling `IERC20::transfer` for a caller-specified `amount`, and unconditionally credits/debits that same requested `amount` into XCM holding and a shared `TransfersCheckingAccount`, without verifying how much the ERC20 contract actually moved. This mirrors the Mellow stETH finding: the code assumes `transfer(amount)` always moves exactly `amount`, when many real-world ERC20 tokens (rebasing tokens, share-accounting tokens like stETH-style wrappers, fee-on-transfer tokens) can deliver less than requested while still returning `true`.

### Finding Description
In `withdraw_asset_with_surplus` [1](#0-0) , the transactor calls the ERC20 contract's `transfer` function to move `amount` from the user to a single shared `TransfersCheckingAccount`, and if the boolean return value is `true`, it unconditionally creates `AssetsInHolding::new_from_fungible_credit(what.id.clone(), Box::new(Erc20Credit(amount)))` — i.e. it credits the *requested* amount into XCM holding, not the amount actually observed to move.

Symmetrically, `deposit_asset_with_surplus` [2](#0-1)  transfers `amount` (taken from holding, i.e. from the earlier credited/requested value) from the shared checking account to the final beneficiary — again trusting the boolean success return, not verifying the checking account's real balance change.

The `Erc20Credit` imbalance type's own doc comment concedes this design assumption explicitly: "the actual balance constraints are enforced by the ERC20 smart contract itself rather than the runtime" [3](#0-2) .

Because `TransfersCheckingAccount` is a single pooled account shared across *all* ERC20 assets and *all* users (as demonstrated by `ERC20TransfersCheckingAccount` in the asset-hub-westend runtime tests) [4](#0-3) , if any ERC20 contract used with this transactor implements share-based/rebasing accounting (transferring 1+ wei less than the nominal `value` argument while still returning `true`, exactly like stETH's documented corner case), the checking account's actual on-chain balance will progressively fall short of the sum of amounts credited into XCM holdings across transactions. Later `deposit_asset_with_surplus` calls attempting to move the full nominal `amount` out of the checking account for a *different* user's transfer of the *same* token will then fail (ERC20 `transfer` reverts due to insufficient balance), and that failure propagates as `XcmError::FailedToTransactAsset`, which per XCM semantics traps the assets and fails the whole message.

This is the direct structural analog of the Mellow M-3 finding: a queue/pool holding an asset under an assumption of exact-amount transfers, using a value recorded from before the transfer to drive later transfers out of a shared pool, without ever checking real balances before/after.

### Impact Explanation
Any XCM message (deposit, teleport-like transfer, or reserve transfer) that routes an ERC20 asset through this shared `TransfersCheckingAccount` and hits a shortfall will revert with `FailedToTransactAsset`, causing assets to be trapped and failing execution for the *affected user's* message. Because the checking account is shared across all users of the same ERC20 token (and is a single account for the whole transactor configuration), a shortfall induced by one user's transfer of a rounding/rebasing ERC20 can cause subsequent, unrelated users' transfers of that same asset to fail — a denial-of-service condition, not merely a self-inflicted loss. No funds are outright stolen (the ERC20 contract's own accounting is authoritative), but users lose access to expected transfers/deposits and messages get trapped, requiring manual recovery of trapped assets.

### Likelihood Explanation
Likelihood depends on whether any ERC20 contract routed through `ERC20Transactor` exhibits share/rebase rounding behavior. Since the matcher (`MatchesFungibles<H160, u128>`) matches based on the asset's `Location`/contract address rather than a curated allow-list validated for “exact transfer” semantics, and `pallet-revive` allows arbitrary EVM-compatible contracts to be deployed permissionlessly, an unprivileged user can deploy a contract with this rounding behavior and interact with it via XCM (as already exercised in the repo's own test `smart_contract_does_not_return_bool_fails`, which demonstrates non-standard ERC20 contracts are reachable through this exact path) [4](#0-3) . Whether this is currently exploitable in production depends on runtime configuration (which ERC20 addresses/asset kinds are actually wired into `ERC20Transactor` via the `Matcher`), which I could not fully verify from the available index — this is a genuine limitation of my analysis and would need confirmation against the live `xcm_config.rs` `Matcher` type definition.

### Recommendation
Do not trust the `amount` parameter or the boolean success return value as proof of exact transfer. Instead:
- Query the ERC20 `balanceOf` (or the checking account's/beneficiary's balance) before and after each `transfer` call and use the observed delta as the credited/debited amount in `AssetsInHolding`/`Erc20Credit`.
- Consider using a per-asset (or per-transaction) escrow/checking mechanism instead of a single shared pooled account so that a shortfall in one asset's accounting cannot cascade into DoS for other users of the same asset.
- Reject or flag ERC20 contracts whose observed transferred amount does not match the requested amount, rather than silently crediting the nominal value.

### Proof of Concept
Conceptual PoC (cannot be executed in this ask-only environment, and no on-chain reproduction was run):
1. Deploy a malicious/rebasing ERC20 contract via `pallet-revive` whose `transfer(to, value)` internally moves `value - 1` (or `value` minus rounding) wei but returns `true` (legal per ERC20 spec, and exactly the documented stETH corner case).
2. Register/use this contract as an XCM asset routed through `ERC20Transactor` (its `Location` resolves via `Matcher` to the contract's H160 address).
3. User A executes an XCM program that `WithdrawAsset`s `amount` of this token — `withdraw_asset_with_surplus` transfers `amount` to `TransfersCheckingAccount`, but the checking account actually only receives `amount - 1`. Holding is nonetheless credited with the full `amount`.
4. User A's XCM `DepositAsset`s the full `amount` to a beneficiary — `deposit_asset_with_surplus` calls `transfer(beneficiary, amount)` from the checking account, which now has an actual balance 1 wei short of what earlier holdings assumed were available.
5. Once the checking account's cumulative deficit from repeated transfers of this token exceeds its real balance, any subsequent user's attempt to withdraw/deposit `amount` of the same token via `ERC20Transactor` fails with `FailedToTransactAsset`, denying service and trapping their assets — matching the Mellow M-3 failure mode where an accounting shortfall from one action causes reverts for later, unrelated actions on a shared balance.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L73-89)
```rust
/// A minimal imbalance tracking type that holds an ERC20 token amount.
///
/// This type implements the necessary imbalance accounting traits but does not perform
/// runtime-level balance enforcement. It's used to track ERC20 token amounts within XCM
/// asset holdings, where the actual balance constraints are enforced by the ERC20 smart
/// contract itself rather than the runtime.
struct Erc20Credit(u128);
impl UnsafeConstructorDestructor<u128> for Erc20Credit {
	fn unsafe_clone(&self) -> Box<dyn ImbalanceAccounting<u128>> {
		Box::new(Erc20Credit(self.0))
	}
	fn forget_imbalance(&mut self) -> u128 {
		let amount = self.0;
		self.0 = 0;
		amount
	}
}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L150-216)
```rust
	fn withdraw_asset_with_surplus(
		what: &Asset,
		who: &Location,
		_context: Option<&XcmContext>,
	) -> Result<(AssetsInHolding, Weight), XcmError> {
		tracing::trace!(
			target: "xcm::transactor::erc20::withdraw",
			?what, ?who,
		);
		let (asset_id, amount) = Matcher::matches_fungibles(what)?;
		let who = AccountIdConverter::convert_location(who)
			.ok_or(MatchError::AccountIdConversionFailed)?;
		// We need to map the 32 byte checking account to a 20 byte account.
		let checking_account_eth = T::AddressMapper::to_address(&TransfersCheckingAccount::get());
		let checking_address = Address::from(Into::<[u8; 20]>::into(checking_account_eth));
		let weight_limit = WeightLimit::get();
		// To withdraw, we actually transfer to the checking account.
		// We do this using the solidity ERC20 interface.
		let data =
			IERC20::transferCall { to: checking_address, value: EU256::from(amount) }.abi_encode();
		let ContractResult { result, weight_consumed, storage_deposit, .. } =
			pallet_revive::Pallet::<T>::bare_call(
				OriginFor::<T>::signed(who.clone()),
				asset_id,
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
		tracing::trace!(target: "xcm::transactor::erc20::withdraw", ?weight_consumed, ?surplus, ?storage_deposit);
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
			}
		} else {
			tracing::debug!(target: "xcm::transactor::erc20::withdraw", ?result, "Error");
			// This error could've been duplicate smart contract, out of gas, etc.
			// If the issue is gas, there's nothing the user can change in the XCM
			// that will make this work since there's a hardcoded gas limit.
			Err(XcmError::FailedToTransactAsset("ERC20 contract execution errored"))
		}
	}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L218-306)
```rust
	/// Deposits assets from holding to a beneficiary account via ERC20 transfer.
	///
	/// Note: This implementation only handles a single fungible asset at a time. The
	/// `AssetsInHolding` parameter is required by the `TransactAsset` trait, but callers
	/// should ensure only one asset is passed. If multiple assets are present, only the
	/// first fungible asset will be deposited and the rest will be silently ignored.
	/// The `defensive_assert!` helps catch misuse during development.
	fn deposit_asset_with_surplus(
		what: AssetsInHolding,
		who: &Location,
		_context: Option<&XcmContext>,
	) -> Result<Weight, (AssetsInHolding, XcmError)> {
		tracing::trace!(
			target: "xcm::transactor::erc20::deposit",
			?what, ?who,
		);
		defensive_assert!(what.len() == 1, "Trying to deposit more than one asset!");
		// Check we handle this asset.
		let maybe = what
			.fungible_assets_iter()
			.next()
			.and_then(|asset| Matcher::matches_fungibles(&asset).ok());
		let (asset_contract_id, amount) = match maybe {
			Some(inner) => inner,
			None => return Err((what, MatchError::AssetNotHandled.into())),
		};
		let who = match AccountIdConverter::convert_location(who) {
			Some(inner) => inner,
			None => return Err((what, MatchError::AccountIdConversionFailed.into())),
		};
		// We need to map the 32 byte beneficiary account to a 20 byte account.
		let eth_address = T::AddressMapper::to_address(&who);
		let address = Address::from(Into::<[u8; 20]>::into(eth_address));
		// To deposit, we actually transfer from the checking account to the beneficiary.
		// We do this using the solidity ERC20 interface.
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
		} else {
			tracing::debug!(target: "xcm::transactor::erc20::deposit", ?result, "Error");
			// This error could've been duplicate smart contract, out of gas, etc.
			// If the issue is gas, there's nothing the user can change in the XCM
			// that will make this work since there's a hardcoded gas limit.
			Err((what, XcmError::FailedToTransactAsset("ERC20 contract execution errored")))
		}
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
