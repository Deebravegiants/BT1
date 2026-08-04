### Title
Silent, untrapped fund loss via `TransactAsset::transfer_asset` best-effort restore fallback - ([File: polkadot/xcm/xcm-executor/src/traits/transact_asset.rs])

### Summary
The default `transfer_asset` implementation performs a withdraw-then-deposit fallback when `internal_transfer_asset` is not atomic (returns `AssetNotFound`/`Unimplemented`). If the deposit to the beneficiary fails and the "best effort" restore deposit back to the source also fails, the resulting `Credit` imbalance is dropped and discarded via `let _ = ...`, with no `AssetTrap` recording, unlike the holding-based deposit path which the codebase explicitly hardened to always trap undeposited funds.

### Finding Description
`TransactAsset::transfer_asset` in [1](#0-0)  falls back to `withdraw_asset` + `deposit_asset` whenever `internal_transfer_asset` returns `AssetNotFound` or `Unimplemented`. On deposit failure, it attempts a "best effort" restore to `from` and then unconditionally discards the result of that restore call with `let _ = ...`, silently swallowing any second failure.

This fallback is reachable whenever the configured `AssetTransactor` does not implement an atomic `internal_transfer_asset`. `FungibleMutateAdapter` explicitly documents that it "Works for everything but transfers" and has no `internal_transfer_asset` override [2](#0-1) , so its inherited default returns `Err(XcmError::Unimplemented)`, forcing every `transfer_asset` call through the risky withdraw/deposit path.

In `deposit_asset` (shared by `FungibleMutateAdapter`/`FungibleAdapter`), a deposit failure (e.g., beneficiary balance below `ExistentialDeposit`) correctly returns the unresolved `Credit` back as `unspent` via `Fungible::resolve`'s `Err(unspent)` path [3](#0-2) , so no funds are destroyed at that point. The problem is entirely in the caller: if the attacker has drained `from` below ED via the preceding `withdraw_asset`, the restore-to-`from` deposit also fails, and the returned `(unspent, error)` tuple from that second call is discarded, dropping the `Credit` object. `Credit`'s `Drop` implementation is designed to decrease `TotalIssuance` on discard (to preserve the balance/issuance invariant for a truly-burned imbalance), so `TotalIssuance` stays internally consistent — but this is an unannounced, XCM-level burn with **no** `AssetsTrapped`/`AssetTrap::drop_assets` event, unlike the explicit trapping guarantee the codebase built for the holding-based `DepositAsset` path (`deposit_assets_with_retry`, tested in `initiate_transfer.rs` and `deposit_with_retry.rs`) [4](#0-3) . The user has no way to reclaim these funds via `ClaimAsset` because they were never placed in `self.holding` or trapped.

By contrast, `FungibleAdapter`'s combined transactor uses `FungibleTransferAdapter::internal_transfer_asset`, which calls `Fungible::transfer(...)` — an atomic operation that does not debit `from` unless the credit to `to` also succeeds [5](#0-4) . For this common, recommended configuration, `internal_transfer_asset` returns a concrete error (e.g. `FailedToTransactAsset`) rather than `AssetNotFound`/`Unimplemented`, so the vulnerable fallback path in `transfer_asset` is never triggered.

### Impact Explanation
Where reachable (an `AssetTransactor` lacking an atomic `internal_transfer_asset`, e.g. a bare `FungibleMutateAdapter` deployment, or any custom `TransactAsset` implementation relying on the default `transfer_asset`), an unprivileged XCM sender can cause funds withdrawn from `from` to be irrecoverably burned with no `AssetsTrapped` accounting trail, breaking the invariant that no unprivileged flow may silently destroy value without an accounting/trap record.

### Likelihood Explanation
This requires: (1) the runtime's `AssetTransactor` to not implement an atomic transfer (not true for the standard `FungibleAdapter`/`FungibleTransferAdapter` combination used in most production configs), and (2) the attacker to control `from`'s balance such that after `withdraw_asset` it drops below ED and the beneficiary deposit also fails. This is fully attacker-controllable via `TransferAsset`/teleport XCM messages with an exact holding amount. Likelihood is low-to-moderate overall because it depends on runtime configuration choice (whether `FungibleMutateAdapter` is used standalone rather than as part of `FungibleAdapter`), but it is a real logic flaw in the shared default trait method that any such configuration, or any third-party `TransactAsset` implementation without an atomic transfer, will hit deterministically.

### Recommendation
In `TransactAsset::transfer_asset`'s default implementation, do not discard the result of the restore attempt. If the restore-to-`from` deposit also fails, return the leftover `AssetsInHolding` up the call stack (or route it into the XCM executor's holding/trap mechanism) instead of dropping it, so funds are always trapped via `Config::AssetTrap::drop_assets` rather than silently burned by `Credit`'s `Drop` implementation.

### Proof of Concept
Rust unit test in `xcm-executor`'s test harness:
1. Configure `AssetTransactor = FungibleMutateAdapter<...>` (no atomic transfer).
2. Fund `SENDER` with exactly `ED` (e.g. 2 units), fund `RECIPIENT` with 0 and set beneficiary's minimum deposit requirement to fail (amount `< ED`, e.g. transfer 1 unit leaving both `SENDER` post-withdraw and `RECIPIENT` below ED).
3. Execute an XCM containing `TransferAsset { assets: (Here, 1u128), beneficiary: RECIPIENT }` originating from `SENDER`.
4. Assert: `SENDER`'s balance decreased by the withdrawn amount, `RECIPIENT` received nothing, `TotalIssuance` decreased by the same amount, and `TRAPPED_ASSETS`/`AssetTrap::drop_assets` recorded **nothing** — demonstrating the funds vanished without any trap/claim record, in contrast to the `DepositAsset`-instruction tests (`deposit_with_retry.rs`, `initiate_transfer.rs`) which do assert trapping for the equivalent failure via the holding path.

### Citations

**File:** polkadot/xcm/xcm-executor/src/traits/transact_asset.rs (L167-185)
```rust
	fn transfer_asset(
		asset: &Asset,
		from: &Location,
		to: &Location,
		context: &XcmContext,
	) -> Result<Asset, XcmError> {
		match Self::internal_transfer_asset(asset, from, to, context) {
			Err(XcmError::AssetNotFound | XcmError::Unimplemented) => {
				let credit = Self::withdraw_asset(asset, from, Some(context))?;
				Self::deposit_asset(credit, to, Some(context)).map_err(|(unspent, error)| {
					// best effort try to return the assets to original owner
					let _ = Self::deposit_asset(unspent, from, Some(context));
					error
				})?;
				Ok(asset.clone())
			},
			result => result,
		}
	}
```

**File:** polkadot/xcm/xcm-builder/src/fungible_adapter.rs (L55-80)
```rust
	fn internal_transfer_asset(
		what: &Asset,
		from: &Location,
		to: &Location,
		_context: &XcmContext,
	) -> result::Result<Asset, XcmError> {
		tracing::trace!(
			target: "xcm::fungible_adapter",
			?what, ?from, ?to,
			"internal_transfer_asset",
		);
		// Check we handle the asset
		let amount = Matcher::matches_fungible(what).ok_or(MatchError::AssetNotHandled)?;
		let source = AccountIdConverter::convert_location(from)
			.ok_or(MatchError::AccountIdConversionFailed)?;
		let dest = AccountIdConverter::convert_location(to)
			.ok_or(MatchError::AccountIdConversionFailed)?;
		Fungible::transfer(&source, &dest, amount, Expendable).map_err(|error| {
			tracing::debug!(
				target: "xcm::fungible_adapter", ?error, ?source, ?dest, ?amount,
				"Failed to transfer asset",
			);
			XcmError::FailedToTransactAsset(error.into())
		})?;
		Ok(what.clone())
	}
```

**File:** polkadot/xcm/xcm-builder/src/fungible_adapter.rs (L83-150)
```rust
/// [`TransactAsset`] implementation that allows the use of a [`fungible`] implementation for
/// handling an asset in the XCM executor.
/// Works for everything but transfers.
pub struct FungibleMutateAdapter<Fungible, Matcher, AccountIdConverter, AccountId, CheckingAccount>(
	PhantomData<(Fungible, Matcher, AccountIdConverter, AccountId, CheckingAccount)>,
);

impl<
		Fungible: fungible::Mutate<AccountId>,
		Matcher: MatchesFungible<Fungible::Balance>,
		AccountIdConverter: ConvertLocation<AccountId>,
		AccountId: Eq + Clone + Debug,
		CheckingAccount: Get<Option<(AccountId, MintLocation)>>,
	> FungibleMutateAdapter<Fungible, Matcher, AccountIdConverter, AccountId, CheckingAccount>
{
	fn can_accrue_checked(checking_account: AccountId, amount: Fungible::Balance) -> XcmResult {
		Fungible::can_deposit(&checking_account, amount, Minted)
			.into_result()
			.map_err(|error| {
				tracing::debug!(
					target: "xcm::fungible_adapter", ?error, ?checking_account, ?amount,
					"Failed to deposit funds into account",
				);
				XcmError::NotDepositable
			})
	}

	fn can_reduce_checked(checking_account: AccountId, amount: Fungible::Balance) -> XcmResult {
		Fungible::can_withdraw(&checking_account, amount)
			.into_result(false)
			.map_err(|error| {
				tracing::debug!(
					target: "xcm::fungible_adapter", ?error, ?checking_account, ?amount,
					"Failed to withdraw funds from account",
				);
				XcmError::NotWithdrawable
			})
			.map(|_| ())
	}

	fn accrue_checked(checking_account: AccountId, amount: Fungible::Balance) {
		let ok = Fungible::mint_into(&checking_account, amount).is_ok();
		debug_assert!(ok, "`can_accrue_checked` must have returned `true` immediately prior; qed");
	}

	fn reduce_checked(checking_account: AccountId, amount: Fungible::Balance) {
		let ok = Fungible::burn_from(&checking_account, amount, Expendable, Exact, Polite).is_ok();
		debug_assert!(ok, "`can_reduce_checked` must have returned `true` immediately prior; qed");
	}
}

impl<
		Fungible: fungible::Inspect<AccountId, Balance: 'static>
			+ fungible::Mutate<AccountId>
			+ fungible::Balanced<AccountId, OnDropCredit: 'static, OnDropDebt: 'static>,
		Matcher: MatchesFungible<Fungible::Balance>,
		AccountIdConverter: ConvertLocation<AccountId>,
		AccountId: Eq + Clone + Debug,
		CheckingAccount: Get<Option<(AccountId, MintLocation)>>,
	> TransactAsset
	for FungibleMutateAdapter<Fungible, Matcher, AccountIdConverter, AccountId, CheckingAccount>
where
	fungible::Imbalance<
		<Fungible as fungible::Inspect<AccountId>>::Balance,
		<Fungible as fungible::Balanced<AccountId>>::OnDropCredit,
		<Fungible as fungible::Balanced<AccountId>>::OnDropDebt,
	>: ImbalanceAccounting<u128>,
{
```

**File:** polkadot/xcm/xcm-builder/src/fungible_adapter.rs (L250-264)
```rust
		let Some(imbalance) = what.fungible.remove(&asset_id) else {
			return Err((what, MatchError::AssetNotHandled.into()));
		};
		// "manually" build the concrete credit and move the imbalance there.
		let mut credit = fungible::Credit::<AccountId, Fungible>::zero();
		credit.saturating_subsume(imbalance);
		Fungible::resolve(&who, credit).map_err(|unspent| {
			tracing::debug!(target: "xcm::fungible_adapter", ?asset_id, ?who, ?amount, "Failed to deposit asset");
			(
				AssetsInHolding::new_from_fungible_credit(asset_id, Box::new(unspent)),
				XcmError::FailedToTransactAsset("")
			)
		})?;
		Ok(())
	}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1837-1850)
```rust
	/// Deposit `to_deposit` assets to `beneficiary`, without giving up on the first (transient)
	/// error, and retrying once just in case one of the subsequently deposited assets satisfy some
	/// requirement.
	///
	/// Most common transient error is: `beneficiary` account does not yet exist and the first
	/// asset(s) in the (sorted) list does not satisfy ED, but a subsequent one in the list does.
	///
	/// Any per-asset failure on the retry pass propagates as `Err`, and the surrounding
	/// `transactional_process` rolls back the whole instruction (storage changes are reverted by
	/// `Config::TransactionalProcessor`, and `self.holding` is restored from its
	/// pre-instruction backup). Anything left in `self.holding` after the program finishes is
	/// then trapped by `post_process` via `Config::AssetTrap::drop_assets`, so funds are never
	/// silently lost.
	///
```
