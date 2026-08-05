### Title
Excess/rebased ERC-20 balances accumulate un-withdrawably in the shared `TransfersCheckingAccount` used by `ERC20Transactor` - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

### Summary
The `ERC20Transactor` XCM asset transactor moves ERC-20 tokens between users and a single shared "checking" account by calling `IERC20::transfer` for the exact numeric `amount` extracted from the XCM `Asset`. Because the transactor treats the stated `amount` as the sole source of truth for how much value is held on behalf of users, any ERC-20 whose `balanceOf()` can increase independently of transfers (a rebasing/interest-bearing token) will leave real, un-accounted-for balance sitting in the checking account, with no code path to reconcile or withdraw it. This mirrors the C4 finding [M-09] in 2022-05-factorydao, where deposited rebasing-token balance in excess of the tracked ledger amount is permanently stuck.

### Finding Description
`ERC20Transactor::withdraw_asset_with_surplus` withdraws a user's tokens by transferring exactly `amount` to `TransfersCheckingAccount` and wraps that literal `amount` in an `Erc20Credit(amount)` imbalance object placed into `AssetsInHolding`: [1](#0-0) 

`deposit_asset_with_surplus` later moves exactly that recorded `amount` back out of the checking account to a beneficiary: [2](#0-1) 

Both directions rely entirely on the *stated* XCM `Asset` amount, never on reading the checking account's actual `balanceOf()` from the ERC-20 contract. Per the PR description, this transactor matches **any** contract address referenced as `{parents:0, interior: X1(AccountKey20{key, network})}` — there is no allowlist or governance-gated registration step for which ERC-20 contracts can be transacted this way: [3](#0-2) 

Any unprivileged user can permissionlessly deploy an arbitrary ERC-20 contract via `pallet-revive` (e.g. a rebasing/auto-compounding token that increases every holder's balance over time, including the pooled `TransfersCheckingAccount`), and then move it through XCM using this transactor. Because `Erc20Credit` only ever tracks the literal transferred `amount` (see its `saturating_subsume`/`saturating_take` semantics, which never touch on-chain balance): [4](#0-3) 

the checking account's real ERC-20 balance can grow beyond the sum of amounts ever recorded in flight, with no `withdraw_excess`-style function, no reconciliation hook, and no owner able to claim the drift — exactly the root cause identified in the referenced report (value in excess of the tracked/pre-calculated ledger amount is neither returned to depositors nor recoverable by an owner).

### Impact Explanation
Rebased/accrued value belonging to depositors of a rebasing ERC-20 asset becomes permanently locked in the shared `TransfersCheckingAccount`, unreachable by any code path in this transactor. This is a fund-lock/accounting-drift issue rather than a direct theft vector, consistent with the "Medium" classification and sponsor's "acknowledged, will not officially support rebasing tokens" resolution in the original report.

### Likelihood Explanation
Likelihood is bounded by (a) whether Asset Hub's runtime actually enables `ERC20Transactor` for arbitrary user-deployed `pallet-revive` contracts without an allowlist/registration gate, and (b) whether a rebasing ERC-20 would realistically be used in this flow. Given the transactor design explicitly matches on `AccountKey20` address alone (no create/registration step described in the PR), an unprivileged user can trigger the condition simply by deploying a token contract with self-inflating balances and routing it through XCM deposit/withdraw calls — no privileged origin is required. This mirrors upstream's own stance of "not officially supporting" such tokens rather than a hard technical impossibility.

### Recommendation
- Reconcile the checking account's real ERC-20 balance (`balanceOf`) against the sum of outstanding `AssetsInHolding` credits and expose a mechanism (e.g., a permissioned sweep/adjustment call) to redistribute or claim drift, similar to `adjust_pool_deposit` added to `pallet-nomination-pools` for ED drift.
- Alternatively, explicitly document/enforce that only ERC-20 contracts with strictly transfer-conserved balances (no rebasing/fee-on-transfer semantics) are safe to use with `ERC20Transactor`, and consider restricting which contracts can be matched (allowlist) rather than matching any `AccountKey20`.

### Proof of Concept
1. Deploy an ERC-20 contract via `pallet-revive` whose `balanceOf()` increases for all holders over time (e.g., a simple rebase that mints proportional balance to every holder on each `transfer`/block).
2. Use XCM to `WithdrawAsset` some amount of this token from a user account; `ERC20Transactor::withdraw_asset_with_surplus` moves `amount` tokens to `TransfersCheckingAccount` and credits `AssetsInHolding` with `Erc20Credit(amount)`.
3. Let time pass / trigger rebases so the checking account's actual `balanceOf()` grows beyond `amount`.
4. Any subsequent `DepositAsset` only moves the originally recorded `amount` back out via `deposit_asset_with_surplus`; the rebased excess remains in `TransfersCheckingAccount` indefinitely, with no function anywhere in `erc20_transactor.rs` to withdraw it.

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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L159-203)
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L251-266)
```rust
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

**File:** prdoc/stable2506/pr_7762.prdoc (L8-19)
```text
    description: |
      This PR introduces an Asset Transactor for dealing with ERC20 tokens and adds it to Asset Hub
      Westend.
      This means asset ids of the form `{ parents: 0, interior: X1(AccountKey20 { key, network }) }` will be
      matched by this transactor and the corresponding `transfer` function will be called in the
      smart contract whose address is `key`.
      If your chain uses `pallet-revive`, you can support ERC20s as well by adding the transactor, which lives
      in `assets-common`.
  - audience: Runtime User
    description: |
      This PR allows ERC20 tokens on Asset Hub to be referenced in XCM via their smart contract address.
      This is the first step towards cross-chain transferring ERC20s created on the Hub.
```
