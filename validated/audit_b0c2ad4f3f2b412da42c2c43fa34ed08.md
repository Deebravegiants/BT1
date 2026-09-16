### Title
`pallet-hyper-fungible-token::on_accept` can mint zero tokens after truncating division, permanently losing bridged funds - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`on_accept` in `pallet-hyper-fungible-token` converts an incoming EVM-denominated amount to the local asset's balance type using `convert_to_balance`, which performs integer division with no floor/zero check before minting or releasing funds to the beneficiary [1](#0-0) . If the division truncates to zero, the pallet proceeds to "credit" the beneficiary with zero, even though the corresponding amount was already burned/escrowed on the EVM source chain.

### Finding Description
`convert_to_balance` divides the raw ERC20 `U256` value by `10^(erc_decimals - local_decimals)` and parses the result into the local balance type, with no assertion that the result is non-zero: [2](#0-1) 

`on_accept` calls this conversion and then unconditionally mints (or transfers from escrow) the resulting `amount` to the beneficiary — there is no `ensure!(amount > 0, ...)` guard before the mutate call: [3](#0-2) 

Any user who burns tokens via `HyperFungibleToken.send` on an EVM chain with high decimal precision (typically 18) and small amount, targeting a destination asset registered with lower `Precisions`/local decimals, can have `message.amount / 10^(erc_decimals - local_decimals)` round down to zero. The corresponding EVM-side burn (`HyperFungibleToken.send` calls `_burn(msg.sender, params.amount)` unconditionally, also with no minimum check) is real and irreversible [4](#0-3) , but the pallet's `on_accept` will successfully "deliver" the message while crediting the beneficiary nothing.

This is exactly analogous to the reported USSD bug class: a mint/credit function computes an output amount from a scaling calculation and mints/credits it without checking the result is non-zero, while the corresponding collateral/input has already been consumed.

### Impact Explanation
Because the message is *successfully processed* (it does not revert, and it is not a timeout), the ISMP request is marked delivered and the sender has no path to recover the burned tokens — the only refund path (`onPostRequestTimeout` / `TokenRefunded`) only triggers when a request times out undelivered, not when it is delivered with a truncated zero amount [5](#0-4) . This is a direct, permanent loss of user funds with no compensating mint, matching a Medium-severity fund-loss bug class.

### Likelihood Explanation
This requires a config where a token's EVM-side decimals significantly exceed the local (substrate) asset's decimals (e.g. `erc_decimals = 18`, `local_decimals = 6` or less) — a configuration explicitly supported and expected by the pallet's own precision-scaling design (`update_asset_precision`/`Precisions` storage, `ERC decimals >= local decimals` invariant enforced at registration) [6](#0-5) . Any unprivileged user who bridges a sufficiently small amount (below `10^(erc_decimals - local_decimals)` in ERC20 units, which can still be an economically meaningful amount, e.g. tens of thousands of raw units) triggers this without any special privilege — a single ordinary cross-chain `send` transaction is enough.

### Recommendation
Add an explicit non-zero check on the converted amount before crediting/minting in `on_accept` (and ideally also validate `params.amount > 0` and that the ERC20-converted amount round-trips to a non-zero value in the EVM `send`/pallet `send` paths), e.g.:
```rust
ensure!(amount > 0, HftError::AmountTooSmallAfterConversion);
```
placed immediately after the `convert_to_balance` call in `modules/pallets/hyper-fungible-token/src/module.rs`, so that requests which would truncate to zero are rejected rather than silently swallowing the sender's funds.

### Proof of Concept
1. Register an asset with `erc_decimals = 18` for a given EVM destination chain and `local_decimals = 6` (a valid, allowed configuration since `erc_decimals >= local_decimals`).
2. A user calls `HyperFungibleToken.send` on the EVM chain with `params.amount = 500_000_000_000` (5×10^11, i.e. 0.0000005 tokens in 18-decimal terms) — the contract unconditionally executes `_burn(msg.sender, params.amount)`.
3. The relayed message is delivered to `on_accept`, where `convert_to_balance` computes `500_000_000_000 / 10^(18-6) = 500_000_000_000 / 10^12 = 0`.
4. `Assets::mint_into`/`Currency::transfer` credits the beneficiary with `0`, `TokenReceived` is emitted with `amount: 0`, and the request is marked delivered — the user's burned tokens are gone with no refund mechanism triggered.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-117)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L43-52)
```rust
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-266)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);
```

**File:** modules/pallets/hyper-fungible-token/README.md (L83-89)
```markdown
- `on_accept` — receives `Send` messages from the paired EVM contract. Maps
  the source contract back to a local asset via `ContractToAsset`, scales the
  amount using `Precisions`, then mints (non-native) or releases from escrow
  (native) to the beneficiary. Emits `TokenReceived`.
- `on_timeout` — refunds the original sender's balance from escrow or by
  re-minting. Emits `TokenRefunded`.
- `on_response` — unused; this pallet uses post-only messaging.
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L352-355)
```rust
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```
