### Title
Unchecked ABI decode of ERC20 `transfer` return data in `pallet-revive`'s `fungibles::Mutate` impl can panic when the asset id points to an EOA/non-contract address - (File: `substrate/frame/revive/src/impl_fungibles.rs`)

### Summary
This is the FRAME/pallet-revive analog of the Solmate `safeTransfer`/`safeTransferFrom` "no codesize check" bug class. In the Solmate case, calling `transfer`/`transferFrom` on an address with no code silently "succeeds" (empty return data treated as truthy), causing the caller to believe funds moved when they didn't. In `pallet-revive`, low-level calls to a non-contract account (EOA/no code) are intentionally made to mimic EVM semantics: they return `Ok` with empty return data instead of erroring, as documented and tested for the `no-code` call path [1](#0-0) . The `fungibles::Inspect`/`Mutate` implementation for `pallet-revive` builds ERC20 "calls" (`transfer`) via `bare_call` and then does `bool::abi_decode_validate(&return_value.data).expect("Failed to ABI decode")`, without checking whether the target actually is a contract, and without gracefully handling a decode failure [2](#0-1) [3](#0-2) .

### Finding Description
`Pallet::<T>::burn_from` and `Pallet::<T>::mint_into` in `substrate/frame/revive/src/impl_fungibles.rs` are the `fungibles::Mutate` implementation intended for use by `xcm_builder::FungiblesAdapter`, as stated in the surrounding doc comment [4](#0-3) . Both functions treat the `asset_id: H160` as an ERC20 contract address, encode an `IERC20::transferCall`, and dispatch it through `Self::bare_call` [5](#0-4) [6](#0-5) .

When the returned execution did not revert, the code unconditionally decodes the return data as a `bool` and unwraps with `.expect("Failed to ABI decode")`: [7](#0-6) 

Crucially, `pallet-revive`'s call semantics for calling a plain account with no contract code (an EOA, or simply an address that was never instantiated as a contract) return `Ok(..)` with **empty** return data rather than an error — this is explicit, intentional EVM-compatibility behavior, exercised by the "no-code branch" tests [1](#0-0) , and by `prdoc/stable2503/pr_7729.prdoc`, which documents that calls to non-contract accounts are "allowed" and observed as "a successful call with empty output" (for delegate calls, with the same no-code branch shape applying to regular calls per the `sol.rs` comment). Decoding an empty byte slice as `bool` via `abi_decode_validate` fails, and the `.expect(...)` on that failure will panic rather than propagate a clean error.

This differs from the sibling implementation `ERC20Transactor` in `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`, which performs the same `bare_call` + ABI decode but correctly uses `.map_err(...)` to convert decode failures into `XcmError::FailedToTransactAsset` instead of panicking [8](#0-7) . The test suite even explicitly validates this "no contract at address" case is handled without panicking for `ERC20Transactor` (`non_existent_erc20_will_error`) [9](#0-8) . The `impl_fungibles.rs` code path has no equivalent test and no equivalent defensive handling.

### Impact Explanation
If `Pallet::<T>` (`pallet-revive`) as a `fungibles::Mutate`/`fungibles::Inspect` implementation is wired into a `FungiblesAdapter` (the pattern the doc comment explicitly calls out), an attacker-controlled or malformed `AssetId` (H160) that does not correspond to a deployed ERC20 contract (e.g., a fresh/never-instantiated address, or an EOA) would cause `bare_call` to return `Ok` with empty data. The subsequent `.expect("Failed to ABI decode")` in `burn_from`/`mint_into` would then panic. A panic during dispatch triggers a runtime-level failure of the extrinsic/XCM execution (denial of service for that message/extrinsic), rather than the clean, recoverable error path that the sibling `ERC20Transactor` implements. This is analogous to the original Solmate issue's root cause — failing to account for calls landing on addresses without code — though the manifestation here is a panic/DoS rather than silent fund loss, because `pallet-revive`'s `bare_call` doesn't return a fabricated "true"-like success value the way Solmate's raw `call` does.

### Likelihood Explanation
I was **not able to fully confirm**, within the scope of this investigation, that `pallet-revive::Pallet<T>` (via `impl_fungibles.rs`) is actually configured as the `Matcher`/`Transactor` implementation behind a live `FungiblesAdapter` in any of the shipped runtimes (asset-hub-westend, asset-hub-rococo, penpal, etc.) — those runtimes appear to use the separate, safer `ERC20Transactor` for ERC20/XCM interop instead . If `impl_fungibles.rs`'s `Mutate`/`Inspect` impl is not actually instantiated anywhere as a live `FungiblesAdapter` config in a shipped runtime, this is dead/library code with no reachable entry point, which would disqualify it under the "no reachable attacker-controlled entry path" rule. Given the time available, I could not verify a concrete config item (e.g., `type AssetTransactors = (..., FungiblesAdapter<PalletRevive, ...>, ...)`) referencing this specific `fungibles` impl in any production runtime's `xcm_config.rs`.

### Recommendation
- Replace the `.expect("Failed to ABI decode")` calls in `burn_from` and `mint_into` (`substrate/frame/revive/src/impl_fungibles.rs`) with graceful error propagation (`map_err` to a `DispatchError`), mirroring the pattern already used in `erc20_transactor.rs`.
- Additionally, explicitly check contract existence (e.g., via `AccountInfo::load_contract` or equivalent) before treating an `H160` as an ERC20 contract, so that calls to non-existent contracts fail fast with a descriptive error instead of relying on empty-return-data decode failures.
- Add a regression test analogous to `non_existent_erc20_will_error` for the `impl_fungibles.rs` path if/when it is wired into a `FungiblesAdapter` in any runtime.

### Proof of Concept
Not independently reproduced end-to-end (would require confirming a runtime that instantiates `FungiblesAdapter` with `pallet_revive::Pallet<T>` as the fungibles implementation, then dispatching an XCM `WithdrawAsset`/`DepositAsset` targeting an `H160` asset id with no deployed contract code, which per `Stack::call`'s documented no-code branch behavior [1](#0-0)  would return `Ok` with empty data into `bool::abi_decode_validate(...).expect(...)` at [10](#0-9) , panicking).

### Citations

**File:** substrate/frame/revive/src/tests/sol.rs (L376-384)
```rust
/// `Stack::call`'s no-code branch (the path taken when a running contract
/// makes an external call into an account with no code, e.g.
/// `payable(addr).transfer(...)` or `addr.call{value: ...}("")` to an EOA)
/// invokes `exit_child_span` with `Default::default()` for both `gas_used`
/// and `weight_consumed`. The frame meter does charge an existential
/// deposit when the destination is fresh, so the inner `CallTrace` should
/// report non-zero `gas_used`, but today it reports zero. The top-level
/// `Stack::run_call` no-code branch has the same shape and is fixed
/// separately; this test pins down the nested case.
```

**File:** substrate/frame/revive/src/impl_fungibles.rs (L158-161)
```rust
// We implement `fungibles::Mutate` to override `burn_from` and `mint_to`.
//
// These functions are used in [`xcm_builder::FungiblesAdapter`].
impl<T: Config> fungibles::Mutate<<T as frame_system::Config>::AccountId> for Pallet<T> {
```

**File:** substrate/frame/revive/src/impl_fungibles.rs (L169-185)
```rust
	) -> Result<Self::Balance, DispatchError> {
		let checking_account_eth = T::AddressMapper::to_address(&Self::checking_account());
		let checking_address = Address::from(Into::<[u8; 20]>::into(checking_account_eth));
		let data =
			IERC20::transferCall { to: checking_address, value: EU256::from(amount) }.abi_encode();
		let ContractResult { result, weight_consumed, .. } = Self::bare_call(
			OriginFor::<T>::signed(who.clone()),
			asset_id,
			U256::zero(),
			TransactionLimits::WeightAndDeposit {
				weight_limit: WEIGHT_LIMIT,
				deposit_limit:
					<<T as pallet::Config>::Currency as fungible::Inspect<_>>::total_issuance(),
			},
			data,
			&ExecConfig::new_substrate_tx(),
		);
```

**File:** substrate/frame/revive/src/impl_fungibles.rs (L186-203)
```rust
		log::trace!(target: "whatiwant", "{weight_consumed}");
		if let Ok(return_value) = result {
			if return_value.did_revert() {
				Err("Contract reverted".into())
			} else {
				let is_success =
					bool::abi_decode_validate(&return_value.data).expect("Failed to ABI decode");
				if is_success {
					let balance = <Self as fungibles::Inspect<_>>::balance(asset_id, who);
					Ok(balance)
				} else {
					Err("Contract transfer failed".into())
				}
			}
		} else {
			Err("Contract out of gas".into())
		}
	}
```

**File:** substrate/frame/revive/src/impl_fungibles.rs (L212-224)
```rust
		let data = IERC20::transferCall { to: address, value: EU256::from(amount) }.abi_encode();
		let ContractResult { result, .. } = Self::bare_call(
			OriginFor::<T>::signed(Self::checking_account()),
			asset_id,
			U256::zero(),
			TransactionLimits::WeightAndDeposit {
				weight_limit: WEIGHT_LIMIT,
				deposit_limit:
					<<T as pallet::Config>::Currency as fungible::Inspect<_>>::total_issuance(),
			},
			data,
			&ExecConfig::new_substrate_tx(),
		);
```

**File:** substrate/frame/revive/src/impl_fungibles.rs (L225-241)
```rust
		if let Ok(return_value) = result {
			if return_value.did_revert() {
				Err("Contract reverted".into())
			} else {
				let is_success =
					bool::abi_decode_validate(&return_value.data).expect("Failed to ABI decode");
				if is_success {
					let balance = <Self as fungibles::Inspect<_>>::balance(asset_id, who);
					Ok(balance)
				} else {
					Err("Contract transfer failed".into())
				}
			}
		} else {
			Err("Contract out of gas".into())
		}
	}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L191-194)
```rust
				let is_success = IERC20::transferCall::abi_decode_returns_validate(&return_value.data).map_err(|error| {
					tracing::debug!(target: "xcm::transactor::erc20::withdraw", ?error, "ERC20 contract result couldn't decode");
					XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")
				})?;
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
