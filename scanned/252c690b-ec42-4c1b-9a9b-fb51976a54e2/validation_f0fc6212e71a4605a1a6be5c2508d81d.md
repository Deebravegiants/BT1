### Title
ERC20Transactor: Strict ABI-decoded bool assumption on `transfer()` breaks XCM deposit/withdraw for non-standard ERC20 tokens (USDT-class) - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
The `ERC20Transactor` XCM asset transactor calls `transfer()` on an arbitrary ERC20-compatible contract (via `pallet_revive::Pallet::<T>::bare_call`) and then strictly ABI-decodes the return data as a `bool` using `IERC20::transferCall::abi_decode_returns_validate`. Non-standard ERC20 implementations (the canonical example being mainnet USDT) do not return any data from `transfer()`/`approve()`. Any call data decode failure is mapped to a hard error, causing the whole XCM asset transfer to fail. This is the same vulnerability class as the reported Sherlock finding (M-2, USDT `approve()` doesn't return a bool, causing `IERC20Upgradeable` callers to revert) — here manifesting on the `transfer()` path of an asset transactor that bridges XCM holding-register credits/debits into an EVM ERC20 contract.

### Finding Description
`withdraw_asset_with_surplus` and `deposit_asset_with_surplus` both perform a `bare_call` to the target ERC20 contract's `transfer()` function, then require the response to strictly ABI-decode as `bool`: [1](#0-0) [2](#0-1) 

In both functions, `IERC20::transferCall::abi_decode_returns_validate(&return_value.data)` is called on the raw output bytes of the target contract. If the target ERC20 contract does not return `abi.encode(bool)` from `transfer()` — exactly the pattern of real-world USDT and several other legacy tokens, which return no data at all — this decode fails and the transactor treats the entire operation as a hard failure:
- On withdraw: `Err(XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode"))`
- On deposit: `Err((what, XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")))`

This mirrors the root cause in the external report: an interface that mandates a `bool` return value is used against a token implementation that omits it, and the caller does not defensively handle the missing-return-data case (the standard mitigation being something equivalent to OpenZeppelin's `SafeERC20`, which treats empty return data as success when the target is a contract).

`ERC20Transactor` is wired into runtime XCM configuration: [3](#0-2) 

I was not able to fully verify, within the available iterations, whether the `Matcher`/foreign-asset registration path that associates an XCM `Location`/asset id with an arbitrary ERC20 contract address is permissionless or governance-gated in the shipped asset-hub-westend configuration. This matters for likelihood: if registration of the backing ERC20 contract is a privileged/governance action, then the "attacker" surface narrows to a governance decision to onboard a non-standard token (analogous to a project intentionally wanting to support USDT, as in the original report) rather than to an arbitrary unprivileged user forcing the failure. If registration is permissionless, any user could register (or the pallet could point at) a USDT-style contract and permanently break all deposits/withdrawals for that asset.

### Impact Explanation
If a non-standard ERC20 token (no bool return on `transfer()`, e.g. USDT-style contracts) is used as the backing contract for an asset routed through `ERC20Transactor`, every `withdraw_asset_with_surplus`/`deposit_asset_with_surplus` invocation for that asset will unconditionally fail with `XcmError::FailedToTransactAsset`. This is a complete denial of service for that asset's cross-consensus transfers (deposits and withdrawals), not merely a degraded UX — no legitimate user could ever move that asset in or out of the XCM holding register through this transactor. This matches the impact class described in the source report (liquidity/farming operations permanently broken for USDT).

### Likelihood Explanation
Likelihood is contingent on how backing ERC20 contracts get associated with XCM asset identities via `Matcher: MatchesFungibles`. This is realistic and plausible in practice: USDT and similarly non-compliant tokens are extremely widely used stablecoins, and the whole purpose of `ERC20Transactor` is to interoperate with arbitrary EVM ERC20 contracts deployed via `pallet-revive`, which is exactly the scenario the original Sherlock report flags as a natural, expected integration target ("USDC and USDT are the first natural candidates"). I could not confirm within the remaining tool budget whether the registration of the backing contract per asset is permissionless or requires governance in `asset-hub-westend`'s `xcm_config.rs`, so I cannot assert an unprivileged attacker can trigger this end-to-end without further verification — this should be confirmed by a maintainer/auditor with full repository access before scoring severity.

### Recommendation
Do not require a strictly ABI-decodable `bool` return from `transfer()` (and, if `approve()`/`transferFrom()` calls to arbitrary tokens exist elsewhere, from those too). Adopt SafeERC20-style semantics in `withdraw_asset_with_surplus`/`deposit_asset_with_surplus`:
- Treat empty return data (`return_value.data.is_empty()`) combined with a non-reverted, successful `bare_call` result as success.
- Only require a strict `bool` decode when return data is non-empty, and treat `false` decodes as unambiguous failure.
- Apply the same fallback logic anywhere else in the codebase that strictly ABI-decodes a `bool` return from a `transfer`/`transferFrom`/`approve` call made to an externally supplied, potentially non-standard ERC20 contract.

### Proof of Concept
1. Deploy (via `pallet-revive`) a minimal ERC20-like contract whose `transfer(address,uint256)` performs the balance update but returns no data (mirroring mainnet USDT's `function transfer(address _to, uint _value) public onlyPayloadSize(2 * 32)` with no `returns (bool)`).
2. Register/configure this contract as the backing ERC20 for an asset id matched by `Matcher` used in `ERC20Transactor` (as wired in `asset-hub-westend`'s `xcm_config.rs`).
3. Submit an XCM program that triggers `deposit_asset_with_surplus` or `withdraw_asset_with_surplus` for that asset, e.g. depositing to a beneficiary.
4. Observe: `bare_call` succeeds and `did_revert()` is `false`, but `return_value.data` is empty; `IERC20::transferCall::abi_decode_returns_validate(&return_value.data)` fails to decode, hitting the `Err(error)` branch at [4](#0-3)  and returning `XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")` even though the underlying transfer actually succeeded on-chain — permanently breaking XCM transfers for that asset.

### Citations

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

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L1-1)
```rust
// Copyright (C) Parity Technologies (UK) Ltd.
```
