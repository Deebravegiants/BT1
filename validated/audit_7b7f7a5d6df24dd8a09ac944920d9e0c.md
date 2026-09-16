The Hyperbridge codebase does have a decimals-scaling implementation in the token-bridge pallet that is structurally the same class of bug as the Maia H-05 report: a helper meant to scale bidirectionally between differing decimal precisions, but implemented with `saturating_sub`, which silently degrades to "no scaling" instead of scaling in the opposite direction whenever the remote (ERC20) decimals are lower than the local (Substrate) asset decimals. [1](#0-0) 

### Title
Decimal-scaling helpers `convert_to_balance`/`convert_to_erc20` silently skip scaling when ERC20 decimals < local decimals, causing unbacked mint or permanent value loss - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`pallet-hyper-fungible-token` converts amounts between the EVM-side ERC20 precision (`erc_decimals`) and the local Substrate asset precision (`local_decimals`) using `convert_to_balance` (incoming) and `convert_to_erc20` (outgoing). Both functions compute the scaling exponent as `erc_decimals.saturating_sub(local_decimals)`, which silently clamps to `0` whenever `erc_decimals < local_decimals`. In that case the functions apply no scaling at all instead of scaling in the opposite direction, corrupting the amount by a factor of `10^(local_decimals - erc_decimals)`.

### Finding Description
`convert_to_balance` divides the incoming ERC20 `U256` value by `10^(erc_decimals.saturating_sub(local_decimals))`: [2](#0-1) 

`convert_to_erc20` multiplies the outgoing local balance by the same clamped exponent: [3](#0-2) 

Both are called with `(erc_decimals, decimals)` derived from the per-chain `Precisions` storage and the local asset's actual decimals in `send()`, `on_accept`, and `on_timeout`: [4](#0-3) [5](#0-4) 

These helpers only work correctly when `erc_decimals >= local_decimals` (the documented/tested case, e.g. BRIDGE: EVM side fixed at 18 decimals vs. 12 decimals natively on nexus). When a real-world token pair is registered where the EVM ERC20 has *fewer* decimals than the local Substrate asset (a legitimate, non-malicious configuration — e.g., bridging a 6-decimal ERC20 like USDC to a Substrate asset minted with 12 or 18 decimals, which is a common Substrate convention), `saturating_sub` returns `0` for the exponent, and both directions skip scaling entirely instead of scaling the other way.

### Impact Explanation
- On `send()`: a user locks/burns `value` local-decimal units, but `convert_to_erc20` emits that same raw integer as the ERC20 `amount` field without scaling it down to ERC20 precision. If `local_decimals > erc_decimals`, the destination chain is instructed to release/mint `10^(local_decimals-erc_decimals)`x more tokens than were actually escrowed/burned — an unbacked mint / direct theft from the bridge's backing reserve, reachable by any ordinary unprivileged user simply calling `send()`.
- On `on_accept`/`on_timeout` (incoming direction): the corresponding under-scaling causes the recipient to receive `10^(local_decimals-erc_decimals)`x fewer tokens than intended, causing permanent, unrecoverable loss of value for legitimate depositors.

This exactly mirrors the Maia H-05 pattern: a decimal-normalization helper that only correctly handles one direction of the decimals relationship, silently mis-scaling amounts for tokens outside that assumption, on a mint/burn token-bridge path.

### Likelihood Explanation
Triggering this requires only a legitimate `register_token` configuration where the counterpart EVM contract's decimals are lower than the local asset's decimals — a normal outcome of onboarding real-world tokens with differing native precisions, not a malicious-admin action. Once such a pair exists, every subsequent `send()`, `on_accept`, or `on_timeout` call by any ordinary user silently mis-scales, so the likelihood of hitting the bug is high for any asset pair configured this way, and it is entirely unprivileged-user reachable after registration.

### Recommendation
Replace the one-directional `saturating_sub` scaling with a signed/bidirectional conversion that multiplies when `local_decimals > erc_decimals` and divides when `erc_decimals > local_decimals`, mirroring what `_normalizeAmount`-style helpers do elsewhere in the codebase (e.g. `VWAPOracle._normalizeAmount`, which correctly branches on both directions): [6](#0-5) 

### Proof of Concept
1. Register a token via `register_token` with `native = false`, local asset decimals = 12, and `Precisions` for the destination EVM chain set to `erc_decimals = 6` (e.g., wrapping a 6-decimal USDC-style ERC20).
2. User calls `send()` with `amount = 1_000_000_000_000` (1 whole token at 12 decimals). `convert_to_erc20(1_000_000_000_000, 6, 12)` computes exponent `6.saturating_sub(12) = 0`, so `erc20_amount = 1_000_000_000_000 * 10^0 = 1_000_000_000_000`.
3. This raw value is placed directly into the cross-chain `Message.amount` field and delivered to the destination contract, which treats it as `1_000_000_000_000` raw units of a 6-decimal token — i.e., 1,000,000 whole tokens — released/minted against only 1 whole token's worth of value actually locked/burned on the source chain, a 1,000,000x unbacked release of funds.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-59)
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

/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L254-295)
```rust
			let erc_decimals = Precisions::<T>::get(params.asset_id.clone(), params.destination)
				.ok_or(Error::<T>::DecimalsNotFound)?;

			// Lock or burn the local asset
			let decimals = if params.asset_id == T::NativeAssetId::get() {
				// escrow the native asset
				<T as Config>::NativeCurrency::transfer(
					&who,
					&Self::pallet_account(),
					params.amount,
					ExistenceRequirement::AllowDeath,
				)?;
				T::Decimals::get()
			} else {
				let is_native = NativeAssets::<T>::get(params.asset_id.clone());
				if is_native {
					<T as Config>::Assets::transfer(
						params.asset_id.clone(),
						&who,
						&Self::pallet_account(),
						params.amount.into(),
						Preservation::Expendable,
					)?;
				} else {
					<T as Config>::Assets::burn_from(
						params.asset_id.clone(),
						&who,
						params.amount.into(),
						Preservation::Expendable,
						Precision::Exact,
						Fortitude::Polite,
					)?;
				}
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					params.asset_id.clone(),
				)
			};

			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);
```

**File:** evm/src/utils/VWAPOracle.sol (L240-248)
```text
    function _normalizeAmount(uint256 amount, uint8 _decimals) private pure returns (uint256 normalized) {
        if (_decimals == 18) {
            return amount;
        } else if (_decimals < 18) {
            return amount * (10 ** (18 - _decimals));
        } else {
            return amount / (10 ** (_decimals - 18));
        }
    }
```
