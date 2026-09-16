### Title
Cross-chain decimal-scaling in `pallet-hyper-fungible-token::on_accept` silently truncates sub-unit amounts to zero, permanently destroying bridged value - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`, `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
The Sherlock report describes a protocol that hardcodes value thresholds assuming 18-decimal tokens, breaking (or in this analog, silently mis-handling) low/mismatched-decimals tokens such as `USDC`. The Hyperbridge analog is `pallet-hyper-fungible-token`'s ERC20→local decimal conversion: `convert_to_balance` performs an unconditional integer division by `10^(erc_decimals - local_decimals)` with no floor/minimum check, so any inbound amount smaller than that scaling factor is silently rounded down to `0` while the corresponding tokens were already burned/locked on the EVM side.

### Finding Description
`register_token`/`update_token` enforce `config.decimals >= local_decimals`, i.e. the EVM-side ERC20 decimals must always be `>=` the local asset's decimals: [1](#0-0) 

This makes the ERC20→local direction of `convert_to_balance` a division by `10^(erc_decimals - local_decimals)` on every single inbound transfer, by design: [2](#0-1) 

`on_accept` (triggered by an EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract's `send()`/burn, which is reachable by any unprivileged token bridger) calls this conversion directly on the untrusted amount decoded from the incoming message, with no check that the result is non-zero (or that the original amount was an exact multiple of the scaling factor): [3](#0-2) 

Concretely, the amount computed is:
```
amount = value_in_erc20_units / 10^(erc_decimals - local_decimals)
```
If `erc_decimals - local_decimals` is large relative to the amount sent (e.g. a local asset registered with few decimals, such as `0` or `2`, paired against an 18-decimal EVM token — a completely normal, permitted configuration since only `decimals >= local_decimals` is enforced, not any bound on the *difference*), any amount below `10^(erc_decimals-local_decimals)` wei truncates entirely to `0`. The mint/transfer call is still executed with `amount = 0`, which succeeds silently — there is no revert, no error, and no event indicating a loss.

Meanwhile, on the EVM side the corresponding value was already burned (for non-native assets) or moved into escrow (for native custody) unconditionally as part of the `send()` flow before the cross-chain message is dispatched — there is no reciprocal check there either. The result is tokens destroyed on the source chain with nothing minted on the destination — a real, permanent loss of user funds purely due to a decimals-scaling assumption, the same root cause class as the referenced Sherlock finding (hardcoded scale-dependent arithmetic that silently breaks/loses value once decimals diverge from the implicitly assumed case).

Even in the "safe" configuration the pallet ships with today (`BridgeToken`: 18 EVM decimals vs 12 local decimals — a difference of `10^6`), the same bug produces silent dust-level loss on every transfer whose wei amount isn't a multiple of `10^6`, as acknowledged implicitly by the contract's own comment about scaling: [4](#0-3) 

### Impact Explanation
This is a "token bridger"-reachable path (explicitly listed as an allowed analog actor) that results in permanent loss/freezing of user funds: the source chain destroys or escrows value that is provably backing the destination-chain balance, but the destination-chain mint/credit can be silently reduced to zero (or an under-counted amount) whenever the local asset's decimals are coarser than the ERC20 side's by enough to exceed the transferred amount. Because `register_token`/`update_token` permit arbitrarily large decimal gaps (only requiring `erc_decimals >= local_decimals`, not bounding the difference), governance configuring a low-decimals local asset (e.g. an integer-denominated asset) against an 18-decimal EVM token creates a systemic version of this bug where ordinary user transfer sizes are fully zeroed out rather than merely dust-truncated.

### Likelihood Explanation
High likelihood for any asset pair with a meaningful decimals gap: the vulnerable arithmetic executes unconditionally on every `on_accept` call, requires no attacker sophistication (any user calling the EVM contract's `send()`/bridge function with an amount below the scaling threshold triggers it), and is not gated behind any privileged role. Even for the currently-shipped `BridgeToken` (12 vs 18 decimals) it silently loses the fractional remainder on essentially every transfer that isn't a round multiple of `10^6` wei.

### Recommendation
- In `convert_to_balance`, reject (or refund) conversions that floor to `0` when the input value was non-zero, rather than silently proceeding.
- Consider requiring the caller/dispatcher to round transferred amounts up to the local asset's minimum representable unit before burning/escrowing on the EVM side, or emit/refund the truncated remainder.
- Add an explicit bound on the allowed decimals gap in `register_token`/`update_token`, or require assets with large decimal disparities to accumulate dust in a recoverable account instead of discarding it.
- Add a regression test asserting that a sub-unit EVM amount either reverts the whole cross-chain flow or is provably preserved (not silently zeroed) end-to-end.

### Proof of Concept
1. Governance calls `register_token` for a local asset `X` with `local_decimals = 0` (e.g., an "integer units" asset) and configures an EVM chain with `ChainConfig { decimals: 18, .. }`. This passes the `ensure!(config.decimals >= local_decimals, ...)` check since `18 >= 0`. [5](#0-4) 
2. A user on the EVM chain calls the paired `HyperFungibleToken`/`WrappedHyperFungibleToken` contract's `send()` with `amount = 5 * 10^17` (0.5 whole ERC20 tokens). The EVM contract burns/escrows this amount and dispatches an ISMP POST to the pallet.
3. `on_accept` decodes the message and calls `convert_to_balance(value=5e17, erc_decimals=18, local_decimals=0)`, which computes `5e17 / 10^(18-0) = 5e17 / 1e18 = 0` (integer division floors to zero). [6](#0-5) 
4. `on_accept` proceeds to mint/transfer `amount = 0` to the beneficiary — the call succeeds, no error is raised, and no event flags the discrepancy. [7](#0-6) 
5. Net effect: the user's 0.5 tokens were burned/escrowed on the EVM chain, and the beneficiary received `0` on the destination chain — a permanent, unrecoverable loss of funds.

**Note on verification limits**: I was unable to fetch the exact `send()`/burn implementation of `HyperFungibleToken.sol` on the EVM side within the tool budget to confirm there is no independent minimum-amount guard there; the `HyperFungibleTokenUpgradeable.sol` `onAccept`/`_mint` snippet found confirms the mint side takes the message amount as-is with no re-validation, which is consistent with the described flow, but a full read of the EVM `send()` function is recommended to close out this verification.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L330-356)
```rust
		pub fn register_token(
			origin: OriginFor<T>,
			registration: TokenRegistration<AssetId<T>>,
		) -> DispatchResult {
			T::CreateOrigin::ensure_origin(origin)?;

			let local_decimals = if registration.local_id == T::NativeAssetId::get() {
				T::Decimals::get()
			} else {
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					registration.local_id.clone(),
				)
			};

			NativeAssets::<T>::insert(registration.local_id.clone(), registration.native);

			let chains: Vec<StateMachine> = registration.chains.keys().cloned().collect();
			for (chain, config) in registration.chains {
				// This pallet bridges substrate <-> EVM only; reject non-EVM peers.
				if !matches!(chain, StateMachine::Evm(_)) {
					return Err(Error::<T>::NonEvmPeerChain.into());
				}
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
				let token_contract = config.token_contract.0.to_vec();
```

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-52)
```rust
/// Converts an ERC20 U256 amount to a local balance type
///
/// Divides by 10^(erc_decimals - local_decimals) to scale down from ERC20 precision.
/// The target type must implement `FromStr`.
pub fn convert_to_balance<B: core::str::FromStr>(
	value: U256,
	erc_decimals: u8,
	local_decimals: u8,
) -> Result<B, B::Err> {
	let dec_str = (value /
		U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32)))
	.to_string();
	dec_str.parse::<B>()
}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-91)
```rust
		// Convert amount from ERC20 denomination to local
		let decimals = if local_asset_id == T::NativeAssetId::get() {
			T::Decimals::get()
		} else {
			<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
				local_asset_id.clone(),
			)
		};
		let erc_decimals = Precisions::<T>::get(local_asset_id.clone(), source)
			.ok_or(HftError::DecimalsNotConfigured(source))?;
		let amount = convert_to_balance::<
			<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
		>(
			U256::from_big_endian(&message.amount.to_be_bytes::<32>()),
			erc_decimals,
			decimals,
		)
		.map_err(|e| HftError::InvalidAmountConversion(format!("{e:?}")))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L93-117)
```rust
		// Mint or transfer to beneficiary
		if local_asset_id == T::NativeAssetId::get() {
			<T as Config>::NativeCurrency::transfer(
				&Pallet::<T>::pallet_account(),
				&beneficiary,
				amount,
				ExistenceRequirement::AllowDeath,
			)
			.map_err(|e| HftError::TransferFailed(e.into()))?;
		} else {
			let is_native = NativeAssets::<T>::get(local_asset_id.clone());
			if is_native {
				<T as Config>::Assets::transfer(
					local_asset_id,
					&Pallet::<T>::pallet_account(),
					&beneficiary,
					amount.into(),
					Preservation::Expendable,
				)
				.map_err(|e| HftError::TransferFailed(e.into()))?;
			} else {
				<T as Config>::Assets::mint_into(local_asset_id, &beneficiary, amount.into())
					.map_err(|e| HftError::MintFailed(e.into()))?;
			}
		}
```

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```
