## Title
Cross-chain HFT transfers can round to zero on receipt, permanently burning user funds with no tokens minted - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler converts an incoming ERC20-denominated amount into the local asset's balance via `convert_to_balance`, which performs integer division and can truncate to zero for small amounts when the source chain's ERC20 decimals exceed the local asset's decimals. There is no check that the converted amount is non-zero before proceeding, so a user who burns/locks a small but real amount on the EVM `HyperFungibleToken` contract can have it delivered as `0` on the destination chain — the tokens are gone on the source, nothing is minted on the destination.

### Finding Description
`convert_to_balance` divides the raw `U256` ERC20 amount by `10^(erc_decimals - local_decimals)`: [1](#0-0) 

This is invoked unconditionally in `on_accept` (the handler for inbound cross-chain transfers from the EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contracts) to compute the amount to mint or release to the beneficiary: [2](#0-1) 

The result is then used directly to either transfer from escrow or `mint_into` without any check that `amount != 0`: [3](#0-2) 

Because `Precisions` records the EVM-side decimals per `(asset, chain)` pair — typically `18` for EVM tokens versus a lower-precision local asset (e.g., `6` or `12`) — any incoming amount smaller than `10^(erc_decimals - local_decimals)` divides to `0` under Rust/U256 integer arithmetic. The same unchecked division exists in the `on_timeout` refund path as well: [4](#0-3) 

Since this is a two-sided bridge with no supply governance ("no shared custody pool, no token-governor" per the pallet's own docs), the burn/lock on the EVM side is irreversible once dispatched — there is no re-check of the destination-side precision before the source-side burn occurs, and the ISMP message, once delivered, mints/releases whatever `convert_to_balance` computes, including zero.

This is a structural analog of the reported `USSD.calculateMint` bug: a division by a decimals-derived scale factor that silently floors to zero for small amounts, with no revert guard, causing the depositor/sender to lose the underlying asset while receiving nothing in return.

### Impact Explanation
Any unprivileged user who calls `send` on the pallet (locking/burning their asset) or the equivalent `send()` on the EVM-side `HyperFungibleToken` contract with an amount below the source-to-destination precision-scaling threshold will have their tokens irrecoverably burned or escrowed on the source chain while the destination side mints/releases `0` tokens to the beneficiary. This is a direct, unbacked loss of user funds reachable from a single ordinary token-bridge transaction — no privileged role, governance, or malicious actor is required; a user can trigger it accidentally (e.g., dust transfers, wrong decimal assumptions in a wallet/dApp) or an attacker can grief user funds by convincing them to send a sub-threshold amount. Given the pallet is meant to be a general drop-in bridge for arbitrary tokens/decimals configurations, this is broadly reachable across any token pairing with a decimals gap.

### Likelihood Explanation
Likelihood is Medium-to-High: this requires no special conditions beyond a normal cross-chain transfer of an amount smaller than the decimals-scale factor (e.g., transferring less than 1e-6 of a token when bridging an 18-decimal EVM token to a 6-decimal-precision-configured local asset). SDK-level integrations that default to human-friendly small amounts, or wallets that don't clamp minimum transferable amounts per token pair, could easily trigger this unintentionally. There is no on-chain validation anywhere in the `send` extrinsic or `on_accept`/`on_timeout` handlers preventing it.

### Recommendation
Add an explicit check immediately after computing `amount` in `on_accept` (and `on_timeout`) in `modules/pallets/hyper-fungible-token/src/module.rs`, and reject/refuse processing if the converted amount is zero (e.g., return an `HftError::AmountTooLow`/`ZeroAmountConverted` and revert instead of silently minting nothing). Symmetrically, the pallet's `send` extrinsic and the EVM `HyperFungibleToken.send()`/`WrappedHyperFungibleToken` sender-side logic should pre-validate that `convert_to_erc20`/`convert_to_balance` round-trips to a non-zero amount before locking/burning the user's tokens, so the transaction reverts up front rather than losing funds irretrievably after the ISMP message settles.

### Proof of Concept
1. Register a token via `register_token` with `local_id` decimals `= 6` and the EVM-side `ChainConfig.decimals = 18` (a realistic USDC(6)-vs-ERC20(18) pairing), stored in `Precisions`.
2. On the EVM chain, a user calls `HyperFungibleToken.send()` (or the paired `WrappedHyperFungibleToken`) with `amount = 1e11` wei (0.0000001 token in 18-decimal terms) — well below `10^(18-6) = 1e12`. Tokens are burned/locked on the EVM side and an ISMP POST request is dispatched.
3. On delivery, `on_accept` calls:
   `convert_to_balance(U256::from(1e11), erc_decimals=18, local_decimals=6)`
   `=> 1e11 / 10^(18-6) = 1e11 / 1e12 = 0` (integer division truncates to zero). [1](#0-0) 
4. `amount.into()` is `0`; the code proceeds to `mint_into`/`transfer` of `0` to the beneficiary: [3](#0-2) 
5. `TokenReceived` fires with `amount: 0`; the user's `1e11`-wei burn/lock on the EVM side is permanently lost with no compensating credit on the destination chain, and no timeout/refund path exists since the message was successfully "delivered" (not timed out).

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L246-255)
```rust
				let erc_decimals = Precisions::<T>::get(local_asset_id.clone(), dest)
					.ok_or(HftError::DecimalsNotConfigured(dest))?;
				let amount = convert_to_balance::<
					<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
				>(
					U256::from_big_endian(&message.amount.to_be_bytes::<32>()),
					erc_decimals,
					decimals,
				)
				.map_err(|e| HftError::InvalidAmountConversion(format!("{e:?}")))?;
```
