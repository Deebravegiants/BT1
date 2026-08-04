## Finding: Unchecked zero-amount ERC20 transfers in the XCM `ERC20Transactor`

### Summary
The `ERC20Transactor` in `assets-common` — used by Asset Hub Westend to let XCM move ERC20 tokens deployed on `pallet-revive` — always issues an ERC20 `transfer(to, value)` call for the exact `amount` extracted from the XCM `Asset`, with no check that `amount != 0` before invoking the contract. This mirrors the GoldLink bug class: some ERC20 contracts revert on a zero-value `transfer`, and unlike every other transfer path in this codebase (pallet-balances, pallet-assets, pallet-contracts, pallet-revive's native transfer helper, pallet-vesting), this one path has no zero-value short-circuit.

### Finding Description
`withdraw_asset_with_surplus` and `deposit_asset_with_surplus` both build the ERC20 `transferCall` payload directly from the matched `amount` and dispatch it via `pallet_revive::Pallet::<T>::bare_call`, without ever checking `amount.is_zero()`: [1](#0-0) [2](#0-1) 

If `return_value.did_revert()` is true, the transactor treats this as `XcmError::FailedToTransactAsset("ERC20 contract reverted")`: [3](#0-2) 

By contrast, every native/`fungibles`/`fungible` transfer path elsewhere in the codebase explicitly no-ops on a zero amount before doing any transfer work, e.g.:
- `pallet-balances` `transfer`: [4](#0-3) 
- `pallet-assets` `transfer_and_die`: [5](#0-4) 
- `pallet-contracts` `exec::transfer`: [6](#0-5) 
- `pallet-revive` `exec::transfer` (native balance): [7](#0-6) 

The `ERC20Transactor` is the sole path in this codebase that forwards a user/XCM-controlled `amount` straight into an external contract call representing an ERC20 asset without this guard, and it is wired into a runtime's XCM configuration: [8](#0-7) 

### Impact Explanation
If an ERC20 token registered for this transactor is implemented (or upgraded) to revert on a zero-value `transfer` — a documented real-world pattern (e.g. the historic LEND token cited in the original report) — then any XCM instruction that ends up calling `withdraw_asset`/`deposit_asset` with `amount == 0` for that asset will fail with `FailedToTransactAsset`, aborting that step of XCM execution. This can happen incidentally: XCM messages can legitimately contain a zero-amount fungible (e.g. as a result of fee/asset splitting, multi-asset transfers with a zero remainder, or a caller explicitly crafting a zero-amount asset in a `TransferAsset`/`TransferReserveAsset` instruction). The result is a denial-of-service on that specific XCM operation/message rather than fund loss — the ERC20 balance itself is unaffected since the underlying token never moves — but it can strand assets in XCM holding or cause otherwise-valid batched XCM programs to fail deterministically for that asset.

### Likelihood Explanation
Reachability is unprivileged: any account can construct an XCM message (via `pallet-xcm` `execute`/`send`, or reserve-transfer instructions) that references this ERC20 asset with a zero amount, and the transactor performs no filtering before calling into the contract. I was not able to fully confirm within this pass whether the XCM executor's holding/registration logic (`polkadot/xcm/xcm-executor/src/assets.rs` or the instruction-processing code that calls `deposit_asset_with_surplus`/`withdraw_asset_with_surplus`) filters out zero-amount `Asset` entries earlier in the pipeline before calling into `TransactAsset` implementations; I could not locate such a filter in `transact_asset.rs` itself (the default trait methods contain no such check), but this would need to be verified against the full XCM executor instruction-execution code and the specific `MatchesFungibles` implementation used for this config to be certain a zero-amount asset can actually reach this code path in practice. Likelihood also depends on whether any ERC20 token that reverts on zero-value transfers is actually registered against this transactor on a live/production Asset Hub deployment — this is a token-specific behavior, not universal to ERC20.

### Recommendation
Add an explicit `if amount == 0 { return Ok(...) }` (or equivalent "no-op success" behavior) in both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus` in `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs` before constructing/dispatching the `IERC20::transferCall`, matching the zero-amount short-circuit pattern used consistently elsewhere in the codebase (`pallet-balances`, `pallet-assets`, `pallet-contracts`, `pallet-revive`).

### Proof of Concept
Conceptual PoC (could not be executed in this pass, no terminal access):
1. Deploy (or use an existing) ERC20 contract via `pallet-revive` whose `transfer` function reverts when `value == 0` (mirrors LEND-style tokens).
2. Register this contract as a `MatchesFungibles` asset for `ERC20Transactor` in the Asset Hub XCM config.
3. Submit an XCM program (e.g. via `pallet_xcm::execute` or a `TransferReserveAsset`) that includes this asset with `amount = 0` in a `WithdrawAsset`/`DepositAsset` instruction.
4. Observe `withdraw_asset_with_surplus`/`deposit_asset_with_surplus` return `Err(XcmError::FailedToTransactAsset("ERC20 contract reverted"))`, failing the XCM instruction, even though no real token movement was expected or requested to fail.

**Caveat on confidence**: This is a real code-level gap (no zero-amount guard, unlike every analogous transfer path in the codebase), but I was not able to fully verify in this session whether the XCM executor filters zero-amount assets before reaching `TransactAsset` implementations, nor whether any currently-configured ERC20 asset on a live chain actually reverts on zero transfers. Both would need confirmation (ideally in a Devin session with test/build access) before treating this as a confirmed, in-the-wild exploitable issue rather than a defensive-coding gap.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L159-181)
```rust
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L186-190)
```rust
			tracing::trace!(target: "xcm::transactor::erc20::withdraw", ?return_value, "Return value by withdraw_asset");
			if return_value.did_revert() {
				tracing::debug!(target: "xcm::transactor::erc20::withdraw", "ERC20 contract reverted");
				Err(XcmError::FailedToTransactAsset("ERC20 contract reverted"))
			} else {
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L240-266)
```rust
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
```

**File:** substrate/frame/balances/src/impl_currency.rs (L393-401)
```rust
	fn transfer(
		transactor: &T::AccountId,
		dest: &T::AccountId,
		value: Self::Balance,
		existence_requirement: ExistenceRequirement,
	) -> DispatchResult {
		if value.is_zero() || transactor == dest {
			return Ok(());
		}
```

**File:** substrate/frame/assets/src/functions.rs (L658-661)
```rust
		// Early exit if no-op.
		if amount.is_zero() {
			return Ok((amount, None));
		}
```

**File:** substrate/frame/contracts/src/exec.rs (L1176-1188)
```rust
	/// Transfer some funds from `from` to `to`.
	fn transfer(
		preservation: Preservation,
		from: &T::AccountId,
		to: &T::AccountId,
		value: BalanceOf<T>,
	) -> DispatchResult {
		if !value.is_zero() && from != to {
			T::Currency::transfer(from, to, value, preservation)
				.map_err(|_| Error::<T>::TransferFailed)?;
		}
		Ok(())
	}
```

**File:** substrate/frame/revive/src/exec.rs (L1711-1736)
```rust
	/// Transfer some funds from `from` to `to`.
	///
	/// This is a no-op for zero `value`, avoiding events to be emitted for zero balance transfers.
	///
	/// If the destination account does not exist, it is pulled into existence by transferring the
	/// ED from `origin` to the new account. The total amount transferred to `to` will be ED +
	/// `value`. This makes the ED fully transparent for contracts.
	/// The ED transfer is executed atomically with the actual transfer, avoiding the possibility of
	/// the ED transfer succeeding but the actual transfer failing. In other words, if the `to` does
	/// not exist, the transfer does fail and nothing will be sent to `to` if either `origin` can
	/// not provide the ED or transferring `value` from `from` to `to` fails.
	/// Note: This will also fail if `origin` is root.
	fn transfer<S: State>(
		origin: &Origin<T>,
		from: &T::AccountId,
		to: &T::AccountId,
		value: U256,
		preservation: Preservation,
		meter: &mut ResourceMeter<T, S>,
		exec_config: &ExecConfig<T>,
	) -> DispatchResult {
		let value = BalanceWithDust::<BalanceOf<T>>::from_value::<T>(value)
			.map_err(|_| Error::<T>::BalanceConversionFailed)?;
		if value.is_zero() {
			return Ok(());
		}
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L16-22)
```rust
use super::{
	AccountId, AllPalletsWithSystem, Assets, Balance, Balances, BaseDeliveryFee, CollatorSelection,
	DepositPerByte, DepositPerItem, FeeAssetId, ForeignAssets, GeneralAdmin, ParachainInfo,
	ParachainSystem, PolkadotXcm, PoolAssets, Runtime, RuntimeCall, RuntimeEvent,
	RuntimeHoldReason, RuntimeOrigin, ToRococoXcmRouter, TransactionByteFee, Uniques, WeightToFee,
	XcmpQueue,
};
```
