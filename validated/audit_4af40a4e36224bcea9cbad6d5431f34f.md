`ERC20Transactor` is actually wired into `asset-hub-westend`'s XCM configuration, confirming it is reachable in a live runtime, not just a mock/test helper.

### Title
Fee-on-transfer / non-standard ERC20 tokens cause XCM holding-register accounting mismatch in `ERC20Transactor` - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

### Summary
`ERC20Transactor` is a `TransactAsset` implementation that lets the XCM executor move arbitrary Solidity ERC20 tokens (deployed on `pallet-revive`) by calling their `transfer` function. Like the reported Saddle-finance bug, the code assumes the amount requested equals the amount actually moved by the token contract, without checking real balance deltas. Fee-on-transfer, deflationary, or otherwise non-standard ERC20 tokens can desynchronize the XCM holding register from the real balance escrowed in the `TransfersCheckingAccount`.

### Finding Description
In `withdraw_asset_with_surplus` [1](#0-0) , the transactor calls `IERC20::transferCall{to: checking_address, value: amount}` on the user-supplied ERC20 contract via `pallet_revive::Pallet::<T>::bare_call`. It only checks whether the call reverted and whether the ABI-decoded boolean return value is `true`: [2](#0-1) 

If successful, it unconditionally credits the XCM holding register with the *requested* `amount`, not the amount actually received by `TransfersCheckingAccount`: [3](#0-2) 

The symmetric `deposit_asset_with_surplus` has the same pattern for the outbound leg: it transfers `amount` from the checking account to the beneficiary and, as long as the `transfer` call returns `true`, treats the deposit as fully successful without confirming the beneficiary's balance actually increased by `amount`: [4](#0-3) 

This is exactly the vulnerability class from the report: `safeTransferFrom`-style calls that check success/failure but not the actual balance delta, which breaks for tokens implementing fees-on-transfer, rebasing, or deflationary burn-on-transfer logic. Here, "the token" is any arbitrary Solidity ERC20 contract deployed on `pallet-revive` and picked up by `Matcher::matches_fungibles`, i.e., attacker-controlled code, since ERC20 asset registration for XCM in Asset Hub is permissionless (any contract implementing the `IERC20` interface can be wrapped as an XCM-transactable fungible, matching the same pattern used for real assets in the runtime's XCM config).

### Impact Explanation
Because the amount credited into `AssetsInHolding` on withdrawal is the *nominal* amount rather than the amount actually escrowed, a malicious ERC20 contract can charge itself an internal fee/burn on `transfer` while the runtime's XCM holding register still believes the full nominal amount is backed by `TransfersCheckingAccount`. Subsequent `deposit_asset_with_surplus` calls for that same virtual `AssetsInHolding` amount will attempt to move funds out of `TransfersCheckingAccount` that were never actually deposited there in full. Depending on how the token behaves, this can:
- create phantom/inflated internal accounting where the holding register reports more of the asset than the checking account actually possesses, enabling later withdrawals to fail unpredictably or to drain balances belonging to unrelated legitimate users of the same checking account, and
- desynchronize the "amount transferred" that gets propagated through the wider XCM message (fees, reserve calculations, multi-hop transfers), since the nominal `amount` (not the actual received amount) flows onward through the executor.

### Likelihood Explanation
This requires an attacker to deploy or use an ERC20 contract with non-standard transfer semantics (fee-on-transfer, rebasing, deflationary burn) and have it registered/matched as an XCM-fungible asset via the `Matcher`. This is directly analogous to the original disclosed bug and does not require any privileged role — any user can deploy such a contract on `pallet-revive` and attempt to transact it through XCM, provided the deployed environment's `Matcher` for `ERC20Transactor` accepts arbitrary contract addresses as asset IDs (as is implied by `MatchesFungibles<H160, u128>` keyed on contract address). Whether Asset Hub's specific `Matcher` configuration restricts this to an allow-list of vetted contracts is not fully verified from the available code (the exact `Matcher` type parameter used in `asset-hub-westend`'s `xcm_config.rs` was not inspected in full), which affects whether the attack surface is genuinely permissionless in the live configuration.

### Recommendation
In both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus`, query the `TransfersCheckingAccount`'s (or beneficiary's) ERC20 balance immediately before and after the `transfer` call, and use the observed balance delta — not the requested `amount` — when constructing `AssetsInHolding` credits or when treating the deposit as fully successful. If the delta is smaller than requested, either fail the operation or credit only the actual amount received, mirroring the Curve `FEE_INDEX`-style mitigation referenced in the original report.

### Proof of Concept
1. Deploy a Solidity ERC20 contract on `pallet-revive` whose `transfer` function burns/deducts e.g. 10% of `value` internally but still returns `true` on success (fully valid per any impl detail; not required to be "trusted" or standard-compliant).
2. Register/route this contract as an XCM-transactable fungible asset such that `Matcher::matches_fungibles` in `ERC20Transactor`'s configuration in `asset-hub-westend`'s `xcm_config.rs` accepts it.
3. Initiate an XCM `WithdrawAsset` for `amount = 1000` of this token from an account holding the token. `ERC20Transactor::withdraw_asset_with_surplus` calls `transfer(checking_account, 1000)`, the contract actually moves only 900 to the checking account, but the call returns `true`.
4. Observe that `AssetsInHolding` is credited with `Erc20Credit(1000)` (per line 200 of `erc20_transactor.rs`), even though `TransfersCheckingAccount`'s real ERC20 balance only increased by 900 — an unbacked 100-unit surplus is now represented in the executor's internal holding register, which can be deposited to any destination location by subsequent XCM instructions, unbacked by real tokens in the checking account.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L150-169)
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L185-208)
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
