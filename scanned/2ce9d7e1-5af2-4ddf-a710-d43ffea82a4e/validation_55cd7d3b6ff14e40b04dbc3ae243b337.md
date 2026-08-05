Based on my research, I found a direct analog to the reported ERC20 fee-on-transfer vulnerability in the Polkadot SDK's `ERC20Transactor`, which bridges XCM asset handling to real Solidity ERC-20 contracts via `pallet-revive`.

### Title
ERC20Transactor Credits Requested Amount Instead of Actually-Received Amount on Fee-on-Transfer Tokens - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` performs an actual Solidity ERC-20 `transfer()` call to move tokens from a user into a `TransfersCheckingAccount`, then unconditionally mints an XCM holding credit of the *requested* `amount`, without checking what the checking account actually received.

### Finding Description
In `withdraw_asset_with_surplus`, the transactor calls the ERC20 contract's `transfer()` function and, if the call succeeds (`is_success == true`), it creates `AssetsInHolding::new_from_fungible_credit(what.id.clone(), Box::new(Erc20Credit(amount)))` using the caller-supplied `amount` rather than the delta of the checking account's balance before/after the transfer: [1](#0-0) 

The symmetrical `deposit_asset_with_surplus` function has the same pattern: it transfers `amount` from the checking account to the beneficiary via ERC20 `transfer()` and treats a `true` return value as full success, again without verifying actual balance change: [2](#0-1) 

This is functionally identical to the reported PositionsManager bug: standard ERC-20 `transfer()` success (`return true`) does not guarantee the recipient's balance increased by the full `amount` — deflationary/fee-on-transfer tokens deduct a portion. The recommended fix in both cases is the same: compare balances before and after the transfer to derive the actual amount moved, rather than trusting the input `amount`.

Unlike `pallet-assets` and the native `fungible`/`fungibles` traits in this codebase, which internally track ledger balances exactly (see `Mutate::transfer` in `substrate/frame/support/src/traits/tokens/fungible/regular.rs`, which returns the ledger-verified `amount`), `ERC20Transactor` delegates to an external, arbitrary Solidity contract whose transfer semantics are not guaranteed to be conservative. [3](#0-2) 

### Impact Explanation
If an ERC20 contract registered for use with this transactor implements a transfer fee (common in real-world deflationary/reflection tokens), then on `withdraw_asset_with_surplus` the `TransfersCheckingAccount` receives less than `amount`, but the XCM holding register is credited with the full `amount`. This over-credited value then flows through the XCM executor (e.g., deposited to a destination account, reserve-transferred cross-chain, or reflected in `ReserveAssetDeposited`), creating an accounting mismatch between what is actually custodied in the checking account and what is represented as backing asset elsewhere in the system. Repeated use can drain the checking account below what is required to honor all outstanding claims, effectively creating unbacked value — an integrity/accounting failure at the bridge layer between Substrate/XCM and EVM-style contracts.

### Likelihood Explanation
I was unable to fully confirm within this session whether the `Matcher: MatchesFungibles<H160, u128>` type used to gate which ERC20 contract addresses are transactable is restricted to a governance-curated allowlist or can be permissionlessly extended (e.g., analogous to permissionless foreign-asset registration seen elsewhere in Asset Hub, such as `create_foreign_asset_call`/`ForeignAssets::Created` flows). This is a material open question: if the mapping is governance-gated to a small set of vetted, fee-free tokens, likelihood is low (mirroring the original report's "client comment" mitigation). If any user-deployed/attacker-deployed ERC20 contract can be registered as an XCM-transactable asset, likelihood is realistic for any unprivileged user, since the attacker fully controls the fee logic of their own contract.

### Recommendation
In both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus`, query the ERC20 contract's `balanceOf` for the relevant account (checking account or beneficiary) immediately before and after the `transfer()` call, and use the observed delta as the actual amount credited/withdrawn into `AssetsInHolding`/XCM holding, rather than trusting the caller-specified `amount`. Alternatively, restrict the `Matcher`/asset-registration path to explicitly whitelisted, audited ERC-20 contracts known not to implement transfer fees, and document this as a hard security requirement for anyone integrating `ERC20Transactor`.

### Proof of Concept
Conceptual (I do not have execution access in this session to run it):
1. Deploy an ERC-20 contract with a 1% transfer fee (standard fee-on-transfer pattern) and register it as a transactable asset via the `Matcher` used to configure `ERC20Transactor` for the target chain.
2. Initiate an XCM operation (e.g., a reserve transfer or local XCM `WithdrawAsset`) for `amount = 1_000_000` of this token from a user account.
3. `withdraw_asset_with_surplus` calls `transfer(checking_address, 1_000_000)`; the checking account actually receives `990_000` due to the fee, but the function returns `Erc20Credit(1_000_000)`.
4. Downstream XCM instructions (e.g., `DepositAsset`, `ReserveAssetDeposited` to another chain) operate on the inflated `1_000_000` credit, while the checking account only holds `990_000` of real backing — a 1% (or attacker-chosen %) accounting discrepancy is introduced per transfer, compounding with each use. [4](#0-3)

### Citations

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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-298)
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
			}
```

**File:** substrate/frame/support/src/traits/tokens/fungible/regular.rs (L321-339)
```rust
	fn transfer(
		source: &AccountId,
		dest: &AccountId,
		amount: Self::Balance,
		preservation: Preservation,
	) -> Result<Self::Balance, DispatchError> {
		let _extra = Self::can_withdraw(source, amount).into_result(preservation != Expendable)?;
		Self::can_deposit(dest, amount, Extant).into_result()?;
		if source == dest {
			return Ok(amount);
		}

		Self::decrease_balance(source, amount, BestEffort, preservation, Polite)?;
		// This should never fail as we checked `can_deposit` earlier. But we do a best-effort
		// anyway.
		let _ = Self::increase_balance(dest, amount, BestEffort);
		Self::done_transfer(source, dest, amount);
		Ok(amount)
	}
```
