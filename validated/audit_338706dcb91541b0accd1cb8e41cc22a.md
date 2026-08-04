### Title
Fee-on-transfer / deflationary ERC20 tokens break XCM holding-register accounting in `ERC20Transactor` - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor` (used as an `AssetTransactor` for ERC20 contracts deployed via `pallet-revive`, wired into `asset-hub-westend`'s XCM config, see `ERC20TransfersCheckingAccount` usage in `cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs`) already fixed two of the three token-compatibility classes described in the referenced report (non-`bool`-returning `transfer` and silent-`false`-returning `transfer`), as shown by the `smart_contract_not_erc20_will_error` and `smart_contract_does_not_return_bool_fails` tests in `cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs`. It has not fixed the third class: fee-on-transfer / deflationary ERC20 tokens, because it never checks the actual balance delta before/after the `transfer` call.

### Finding Description
`withdraw_asset_with_surplus` (`erc20_transactor.rs:150-216`) performs an ERC20 `transfer(checking_address, amount)` from the user to the checking account and, if the call succeeds and returns `true`, unconditionally credits the XCM holding register with the full nominal `amount`: [1](#0-0) 

Similarly, `deposit_asset_with_surplus` (`erc20_transactor.rs:225-306`) transfers `amount` from the checking account to the beneficiary and, on a `true` return, treats the whole `amount` as successfully delivered: [2](#0-1) 

Neither function reads the checking account's (or beneficiary's) actual `balanceOf` before and after the transfer to confirm that `amount` tokens were actually moved. If the underlying ERC20 contract implements a transfer fee/deflationary mechanism (analogous to `STA`/`PAXG`/rebasing tokens in the original report), the contract can return `true` while transferring less than `amount`. Since any unprivileged user can deploy an arbitrary Solidity contract via `pallet-revive` and then reference it as an XCM `AssetId` (`AccountKey20`), the attacker fully controls the token contract's transfer semantics — this is not a mocked or trusted-role path; it's the same live contract-instantiation + XCM-execute flow already exercised by `smart_contract_not_erc20_will_error`.

### Impact Explanation
Because the XCM holding register is credited with the nominal `amount` instead of the amount actually received, the same nominal `amount` is later used to instruct `deposit_asset_with_surplus` to move funds out of the checking account (`erc20_transactor.rs:253`). Over repeated withdraw/deposit cycles with a fee-on-transfer token, the checking account's real balance falls behind the amount the runtime believes it holds. This can:
- Silently under-collateralize the checking account, causing later legitimate deposit attempts (for other users/messages) to fail with `ERC20 contract reverted`/insufficient-balance errors — a availability/DoS impact on unrelated XCM messages sharing the same checking account.
- If this transactor's checking-account pattern is ever relied upon as a reserve/backing invariant across chains (bridging nominal amounts), it can produce an accounting mismatch between what is nominally represented in XCM messages and what is actually custodied, which is exactly the “fee-on-transfer token compatibility” root cause flagged in the external report, mapped onto Substrate's `TransactAsset`/XCM holding-register accounting model.

This is scoped strictly to Medium-severity accounting drift/DoS for the shared checking account rather than a direct fund-theft primitive, since each individual withdraw only ever moves what the calling user actually approves/owns.

### Likelihood Explanation
Likelihood is Medium: it requires a user to register/use a non-standard, fee-charging ERC20 contract as an XCM-transactable asset, which is realistic given that any account can deploy arbitrary contracts through `pallet-revive` and that `Matcher::matches_fungibles` only needs to resolve an `AccountKey20` location to a contract address — there's no allowlisting visible in this transactor guaranteeing only vetted, standard-compliant ERC20s reach it.

### Recommendation
Add balance checks around both transfer calls in `erc20_transactor.rs`: read `balanceOf(checking_address)` (withdraw) / `balanceOf(beneficiary)` (deposit) before and after the `IERC20::transferCall`, and credit/report only the actually-observed delta instead of the requested nominal `amount`. Alternatively, explicitly document (as the original report’s discussion resolved) that fee-on-transfer/rebasing ERC20 tokens are unsupported, and add a defensive check that reverts the whole XCM instruction if the observed balance delta does not equal the requested `amount`, mirroring the `did_revert`/`abi_decode_returns_validate` guards already present for the return-value classes.

### Proof of Concept
1. Deploy a Solidity ERC20 contract via `pallet-revive` whose `transfer(to, value)` moves `value - fee` to `to`, burns/redirects `fee`, but still returns `true` (a fee-on-transfer token, analogous to the `MyTokenFake`/`MyTokenExpensive` fixtures already used in `cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs`).
2. Register this contract's address as an `AccountKey20` XCM asset, matching the pattern in `smart_contract_not_erc20_will_error` (`tests.rs:1971-2017`).
3. Execute an XCM `withdraw_asset`/`deposit_asset` program moving `amount` of this token through `ERC20Transactor`.
4. Observe: `withdraw_asset_with_surplus` credits `AssetsInHolding` with the full nominal `amount` (`erc20_transactor.rs:197-203`) even though the checking account's `balanceOf` increased by only `amount - fee`; a subsequent `deposit_asset_with_surplus` for that same nominal `amount` will eventually fail once the checking account balance is exhausted by the accumulated fee deficit, or will incorrectly report `amount` delivered while the actual on-chain state reflects the exact fee-reduced total.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L195-203)
```rust
				if is_success {
					tracing::trace!(target: "xcm::transactor::erc20::withdraw", "ERC20 contract was successful");
					Ok((
						AssetsInHolding::new_from_fungible_credit(
							what.id.clone(),
							Box::new(Erc20Credit(amount)),
						),
						surplus,
					))
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-280)
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
```
