## Analysis

The C4 report describes a class of bug: code that treats the ERC-20 `transfer`/`transferFrom` return value as a mandatory `bool`, which breaks against non-standard tokens (e.g. USDT-style) that don't return data — causing either a revert (in the original Wild Credit case) or a **silent accounting mismatch** in other integrations.

The Polkadot SDK analog is `pallet_revive`'s Solidity-ABI-based `ERC20Transactor` used by the XCM executor on Asset Hub to move locally-deployed ERC20 tokens. [1](#0-0) [2](#0-1) 

### Title
Non-standard ERC20 return values cause fund loss with no asset-trap safety net in `ERC20Transactor::withdraw_asset_with_surplus` - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor` (used as an XCM `TransactAsset` on Asset Hub Westend) assumes every ERC20 contract strictly returns a single ABI-encoded `bool` from `transfer(address,uint256)`. `ERC20Matcher` matches **any** local `AccountKey20` address, i.e. any user-deployed contract on the permissionless `pallet-revive` instance, not just vetted/registered tokens. If the underlying token deviates from strict ERC20 semantics (e.g. returns no data on success — the exact same "USDT-style" non-standard behavior from the referenced report), the on-chain token transfer succeeds and mutates real balances, but the transactor fails to decode the return value and returns an `XcmError` *after* the transfer has already committed.

### Finding Description
`withdraw_asset_with_surplus` performs the ERC20 transfer via `pallet_revive::Pallet::<T>::bare_call` and only credits the XCM holding register (`AssetsInHolding`) if `abi_decode_returns_validate` on the return data succeeds and decodes to `true`: [3](#0-2) 

If `return_value.did_revert()` is `false` (the token transfer succeeded at the EVM/contract level — this is precisely what happens with non-standard tokens that don't revert but simply omit the boolean return), the code path proceeds to `abi_decode_returns_validate`. For a token that returns empty data on success (like real-world USDT), this decode fails and the function returns `Err(XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode"))` — **without ever crediting `AssetsInHolding`**.

Unlike the standard `FungiblesAdapter`/`AssetsInHolding` flow where a successful withdrawal always yields a holding-register credit (protected downstream by XCM's asset-trap mechanism for excess/unused assets), here the actual token balance has already moved from the user to `ERC20TransfersCheckingAccount` (`py/revch`) on-chain, but XCM has no record of it. Since the asset never entered the holding register, it cannot be trapped/reclaimed via `ClaimAsset`; it is simply lost from the user's perspective while sitting in the checking account.

The identical bug exists symmetrically in `deposit_asset_with_surplus`, where a failed decode after a successful on-chain transfer from the checking account to the beneficiary causes the deposit to appear to fail (`Err`) while the beneficiary actually already received the tokens, causing double-crediting/replay risk upstream if callers retry the deposit. [4](#0-3) 

`ERC20Matcher` is not scoped to a curated/registered list of tokens — it matches any local 20-byte address: [2](#0-1) 

and contract instantiation on Asset Hub Westend's `pallet-revive` is permissionless (`InstantiateOrigin = EnsureSigned<Self::AccountId>`): [5](#0-4) 

so any unprivileged user can deploy (or already possess/bridge in bytecode for) a non-strictly-compliant ERC20 contract and reference it as an XCM asset via its `AccountKey20` location.

### Impact Explanation
A user (or a contract they interact with) whose ERC20 token does not return a strict ABI-encoded `bool` on `transfer` will have real token balance moved into the `py/revch` checking account during a `WithdrawAsset` XCM instruction, but the XCM message will report failure and no compensating `AssetsInHolding` credit or asset trap exists. This is a direct loss-of-funds scenario for the token holder, matching the "Medium" impact classified in the referenced report for deposit-accounting mismatches.

### Likelihood Explanation
Reachable by any unprivileged user: `pallet-revive` contract instantiation is permissionless, `ERC20Matcher` accepts any local address without a governance-curated allowlist, and non-standard-return-value ERC20 tokens are extremely common in practice (this is the entire premise of the original finding — USDT itself is one of the most widely used non-standard tokens). No trusted-role compromise is required.

I was not able to fully verify from the index whether the outer XCM instruction pipeline wraps each instruction (or the whole message) in a transactional storage layer that would roll back the `bare_call`'s state mutation when a later instruction/step returns an error — this is the key remaining variable for confirming un-recoverable fund loss versus atomic rollback. However, XCM's own asset-trap design (existence of `ClaimAsset`/trapped-asset accounting) strongly implies that successful withdrawals are *not* transactionally undone on later failures; that mechanism specifically exists to handle assets that entered holding but weren't consumed. In this bug, the asset doesn't even reach holding, so it also would not be captured by that safety net — this specific gap should be confirmed with an actual on-chain reproduction (deploying a non-boolean-returning ERC20 and issuing a `WithdrawAsset` XCM against it) before treating this as fully proven.

### Recommendation
- Do not fail the whole operation when `abi_decode_returns_validate` cannot decode a boolean; instead, follow common Solidity tooling conventions (e.g. OpenZeppelin `SafeERC20`'s pattern) by treating "call succeeded and returned no data" as success, and only treating a return value that decodes to an explicit `false` as failure.
- Alternatively/additionally, ensure `ERC20Matcher`/asset registration for XCM-eligible ERC20s is restricted to a governance-vetted allowlist rather than any local `AccountKey20`, reducing exposure to malicious/non-compliant contracts.
- Ensure that if the decode step fails after the on-chain transfer already succeeded, the transferred amount is still accounted for in `AssetsInHolding` (or otherwise reverted) so funds cannot become stranded/lost.

### Proof of Concept
1. Deploy a bespoke ERC20 contract via `pallet-revive` on Asset Hub Westend whose `transfer` function performs the state change but returns no data (mimicking real-world USDT behavior), matched via `ERC20Matcher`/`AccountKey20`.
2. Fund an account with this token and construct an XCM message with `WithdrawAsset` targeting this token's `AccountKey20` location and amount.
3. Execute the XCM message: `bare_call` in `withdraw_asset_with_surplus` succeeds (`did_revert() == false`, contract state updated, tokens moved to `ERC20TransfersCheckingAccount`), but `IERC20::transferCall::abi_decode_returns_validate` fails to decode the empty/non-bool return data, causing `withdraw_asset_with_surplus` to return `Err(XcmError::FailedToTransactAsset(...))`.
4. Observe that the ERC20 contract's balances show tokens now held by the checking account, but the XCM holding register/`AssetsInHolding` never received a corresponding credit, and no `AssetTrap` event captures it — the user's tokens are unaccounted for.

### Citations

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

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L132-160)
```rust
/// `Contains<Location>` implementation that matches locations with no parents,
/// a `PalletInstance` and an `AccountKey20` junction.
pub struct IsLocalAccountKey20;
impl Contains<Location> for IsLocalAccountKey20 {
	fn contains(location: &Location) -> bool {
		matches!(location.unpack(), (0, [AccountKey20 { .. }]))
	}
}

/// Fallible converter from a location to a `H160` that matches any location ending with
/// an `AccountKey20` junction.
pub struct AccountKey20ToH160;
impl MaybeEquivalence<Location, H160> for AccountKey20ToH160 {
	fn convert(location: &Location) -> Option<H160> {
		match location.unpack() {
			(0, [AccountKey20 { key, .. }]) => Some((*key).into()),
			_ => None,
		}
	}

	fn convert_back(key: &H160) -> Option<Location> {
		Some(Location::new(0, [AccountKey20 { key: (*key).into(), network: None }]))
	}
}

/// [`xcm_executor::traits::MatchesFungibles`] implementation that matches
/// ERC20 tokens.
pub type ERC20Matcher =
	MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>;
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/lib.rs (L1399-1400)
```rust
	type UploadOrigin = EnsureSigned<Self::AccountId>;
	type InstantiateOrigin = EnsureSigned<Self::AccountId>;
```
