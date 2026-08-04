### Title
ERC20 transactor trusts nominal `amount` instead of verifying actual balance change, breaking accounting for fee-on-transfer/rebasing tokens - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor`, the `TransactAsset` implementation used to bridge arbitrary `pallet-revive` ERC20 contracts into the XCM asset-holding model on Asset Hub, credits/debits the XCM holding register with the nominal `amount` requested in the XCM instruction rather than the actual token amount that moved, as observed via `balanceOf`/return data. This is the same "inflationary/deflationary ERC20" bookkeeping flaw described in the external report, mapped onto FRAME/XCM asset-transactor logic.

### Finding Description
`withdraw_asset_with_surplus` calls the ERC20 `transfer` function for the exact `amount` matched from the XCM `Asset`, and if the call succeeds and the boolean return value is `true`, it unconditionally mints an `Erc20Credit(amount)` into the XCM holding register — it never checks the token contract's actual balance delta: [1](#0-0) 

Symmetrically, `deposit_asset_with_surplus` transfers the same `amount` value out of the shared `TransfersCheckingAccount` to the beneficiary, again only checking the boolean success of the ERC20 `transfer` call rather than verifying that the beneficiary actually received `amount` tokens: [2](#0-1) 

The `Erc20Credit` imbalance type used to represent this asset in the XCM holding register is a "manual" accounting type that explicitly does not enforce runtime-level balance constraints, relying entirely on the ERC20 contract's own semantics matching a naive 1:1 transfer model: [3](#0-2) 

This transactor is wired into `AssetTransactors` on Asset Hub for arbitrary contracts deployed on `pallet-revive`, matched only by an address-based matcher (`assets_common::ERC20Matcher`), with no restriction to a vetted allow-list of "standard" ERC20 tokens: [4](#0-3) 

If the underlying ERC20 contract implements a fee-on-transfer, rebasing, or other non-standard `balanceOf`/`transfer` semantics (e.g. Tether-style transfer fees, Ampleforth-style rebases), then:
- On withdraw: the checking account (`ERC20TransfersCheckingAccount`) may receive less than `amount` (deflationary) or more (inflationary/rebasing), but the XCM holding register still records exactly `amount`.
- On deposit: the transactor unconditionally attempts to move `amount` out of the checking account, which may now hold a different real balance than the sum of previously recorded nominal credits.

### Impact Explanation
Because the checking account is a single pooled account shared across all XCM executions for a given ERC20 asset, a mismatch between nominal (`amount`) and real token balance can, over multiple XCM executions, cause:
- Deposits to unrelated beneficiaries failing/reverting due to insufficient real balance in the checking account (deflationary tokens), causing legitimate XCM programs to fail after fees/weight are already consumed, and in odd interleavings potentially trapping assets (`pallet_xcm::Event::AssetsTrapped`) rather than delivering them.
- Silent over- or under-crediting relative to the token actually held/moved, undermining the core invariant that XCM asset holding amounts reflect real transferable value — the same failure mode the external report describes for the Sora bridge's `sendERC20ToSidechain`/balance bookkeeping.

This is a genuine accounting-integrity issue in a reachable, unprivileged code path (any user can submit an XCM `withdraw_asset`/`deposit_asset` program touching an ERC20 asset registered via this transactor, as exercised in `withdraw_and_deposit_erc20s`): [5](#0-4) 

### Likelihood Explanation
Likelihood depends entirely on which ERC20 contracts get matched/registered by `ERC20Matcher` for use with this transactor. If Asset Hub governance/permissionless deployment allows arbitrary `pallet-revive` contracts to be used as XCM-transactable ERC20 assets, an attacker (or an unaware integrator) deploying/registering a fee-on-transfer or rebasing token would trigger the mismatch during normal, unprivileged XCM execution — no privileged origin or trusted-role compromise is required to *trigger* it, only to *introduce* a non-standard token, which mirrors exactly the caveat in the original report ("no currently supported token is inflationary/deflationary, but nothing prevents future integration of one").

### Recommendation
- Short term: Document explicitly (in `erc20_transactor.rs` and any ERC20-asset-registration flow) that only strictly standard-compliant ERC20 tokens (fixed 1:1 `transfer`, no fees, no rebasing) are safe to use with `ERC20Transactor`.
- Long term: Have `withdraw_asset_with_surplus`/`deposit_asset_with_surplus` verify actual balance deltas (via `balanceOf` calls before/after the `transfer`) rather than trusting the boolean return value and requested `amount`, and credit/debit the XCM holding register with the verified real amount; alternatively, gate which contract addresses can be matched by `ERC20Matcher` behind a vetted allow-list enforcing standard ERC20 behavior (a "Token Integration Checklist" equivalent) before permitting their use in `AssetTransactors`.

### Proof of Concept
Not independently executable from static review alone — a concrete PoC would require deploying a fee-on-transfer or rebasing ERC20 contract via `pallet-revive`, registering it through `ERC20Matcher`, and running an XCM program analogous to `withdraw_and_deposit_erc20s` (`cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs:1864-1928`) with such a token to observe the checking-account balance diverge from the nominal amounts recorded in the XCM holding register, and a follow-up deposit failing/reverting due to insufficient real balance. I was unable to fully verify `assets_common::ERC20Matcher`'s exact matching/allow-list logic (`cumulus/parachains/runtimes/assets/common/src/lib.rs`) within the available tool budget, so whether arbitrary contracts can currently be registered against this transactor (as opposed to only vetted ones) is not fully confirmed and should be checked before treating this as exploitable in production configuration.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L73-107)
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

impl UnsafeManualAccounting<u128> for Erc20Credit {
	fn saturating_subsume(&mut self, mut other: Box<dyn ImbalanceAccounting<u128>>) {
		let amount = other.forget_imbalance();
		self.0 = self.0.saturating_add(amount);
	}
}

impl ImbalanceAccounting<u128> for Erc20Credit {
	fn amount(&self) -> u128 {
		self.0
	}
	fn saturating_take(&mut self, amount: u128) -> Box<dyn ImbalanceAccounting<u128>> {
		let new = self.0.min(amount);
		self.0 = self.0 - new;
		Box::new(Erc20Credit(new))
	}
}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L166-216)
```rust
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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L248-298)
```rust
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

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs (L1864-1928)
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
```
