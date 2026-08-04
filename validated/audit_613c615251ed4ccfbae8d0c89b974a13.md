### Title
ERC20Transactor assumes a `bool` return from `transfer()`, breaking XCM transfers for non-standard ERC20 tokens (USDT-style) - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor` (used to move `pallet-revive` ERC20 tokens in/out of XCM holding) calls the token's `transfer()` function and then strictly ABI-decodes the return data as a `bool` using `IERC20::transferCall::abi_decode_returns_validate`. Just like the blueberry `EnsureApprove` bug, tokens that follow the real-world USDT pattern (successful state change, no returned boolean) will fail this decode step even though the underlying transfer already executed, making the asset unusable through this transactor and creating an on-chain/XCM-holding accounting mismatch.

### Finding Description
`withdraw_asset_with_surplus` and `deposit_asset_with_surplus` both build a standard `IERC20::transferCall` and execute it via `pallet_revive::Pallet::<T>::bare_call`: [1](#0-0) 

After the call executes without reverting, the code does not simply check a success flag returned by the runtime call machinery — it re-parses the raw contract return bytes as a Solidity `bool` via `abi_decode_returns_validate`: [2](#0-1) 

The same pattern is repeated for deposits: [3](#0-2) 

This mirrors exactly the root cause in the referenced report: OpenZeppelin's `IERC20` ABI (`function transfer(address,uint256) returns (bool)`) is used generically to interact with an arbitrary contract that may not conform to the exact expected return-data shape. Real-world USDT and several other legacy tokens implement `transfer`/`approve` with **no return value at all**. When such a contract is used, `return_value.did_revert()` is `false` (the transfer succeeded) but `return_value.data` is empty, so `abi_decode_returns_validate` fails and the transactor returns `XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")` — even though the token balance has already moved.

Unlike the Solidity `safeTransfer`/`EnsureApprove` case, this code isn't calling into an off-chain, arbitrary ERC20 — it's calling into a `pallet-revive` contract that is registered as an XCM-transactable asset via the `Matcher: MatchesFungibles` configuration. Any ERC20 contract deployed under `pallet-revive` that intentionally or accidentally omits the boolean return (a very common real-world token quirk, not just USDT) would trigger this failure mode for every withdrawal/deposit routed through `ERC20Transactor`.

### Impact Explanation
- **Denial of service for the asset**: once an ERC20 with non-standard return behavior is configured as a transactable asset via `ERC20Transactor`, every `withdraw_asset_with_surplus`/`deposit_asset_with_surplus` call for that asset permanently fails at the decode step, rendering the asset non-transactable through XCM.
- **Potential state mismatch / stuck funds**: the `bare_call` to the token contract already performs the real balance movement (to/from the `TransfersCheckingAccount`) before the return-data decode is attempted. If that call's storage effects are not rolled back together with the enclosing XCM error (this depends on `pallet_revive::bare_call`'s transactional isolation, which I was not able to fully verify within this scan), the transactor could report failure to the XCM executor (returning the asset to holding / not crediting holding) while the real ERC20 balance has already moved to/from the checking account — producing an accounting mismatch between the on-chain token balance and the XCM holding register.
- This matches the sherlock report's impact class: wasted/loss-of-funds risk anchored purely in the assumption that a token's `transfer`/`approve` call returns a well-formed boolean.

### Likelihood Explanation
Configuring which ERC20 contracts are matched by `Matcher: MatchesFungibles` is a governance/runtime-configuration decision, not something an arbitrary unprivileged user controls. However:
- Given the developers explicitly modeled this on the general `IERC20` Solidity ABI (same interface referenced in the report), any team wiring up `ERC20Transactor` for a bridged/wrapped token that mimics well-known non-standard tokens (USDT-style, no bool return) will hit this failure deterministically and unconditionally, not as an edge case.
- Once such a token is configured, the failure is triggered by ordinary, unprivileged XCM transfer messages — no special privileges are needed to trigger the DoS/mismatch, only to configure the asset (which is expected to be a normal integration step, exactly as blueberry's SoftVault deployer intended to support USDT).

### Recommendation
- Do not rely on strict ABI decoding of the `transfer`/`approve` return data for success determination. Instead, treat "call did not revert" (`!return_value.did_revert()`) as success when the return data is empty, and only attempt to decode a `bool` when return data is present (mirroring OpenZeppelin's `SafeERC20`/`safeTransfer` semantics, which explicitly special-case empty return data as success).
- Add an explicit code path/test for zero-length return data as used by non-standard ERC20 tokens (USDT-style), consistent with the parent report's recommendation of "add support for tokens with ERC20 functions that don't return values."
- Verify whether `pallet_revive::bare_call`'s internal storage effects are committed independently of the enclosing XCM transaction outcome; if so, ensure a failed decode does not leave the checking-account balance and XCM holding register in an inconsistent state.

### Proof of Concept
1. Deploy (or configure via `Matcher`) a `pallet-revive` ERC20 contract whose `transfer(address,uint256)` function performs the balance mutation but returns **no data** (matching real-world USDT bytecode behavior, only reachable inside `pallet-revive`/PVM rather than off-chain Solidity, but functionally identical to the report's PoC).
2. Register this contract as the underlying token for an XCM-transactable asset via `ERC20Transactor`'s `Matcher`.
3. Initiate any XCM message that triggers `withdraw_asset_with_surplus` or `deposit_asset_with_surplus` for this asset (e.g., a reserve-transfer or teleport-like local transfer routed through the transactor).
4. Observe that `pallet_revive::Pallet::<T>::bare_call` returns `Ok(return_value)` with `did_revert() == false` (transfer succeeded on-chain) but `IERC20::transferCall::abi_decode_returns_validate(&return_value.data)` errors due to zero-length data, causing the transactor to return `XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")` at: [4](#0-3) 
5. All subsequent XCM transfers of this asset fail identically, making the configured asset permanently unusable through `ERC20Transactor`.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L168-216)
```rust
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
