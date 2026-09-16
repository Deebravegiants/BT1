## Analysis

The DODO report is about a lending vault (`D3Vault`) losing funds because rounding direction favored the user (borrower) instead of the vault when converting between raw amounts and rate-adjusted amounts. The reachable Hyperbridge analog is in `pallet-hyper-fungible-token`'s cross-chain decimal-scaling helpers, which convert amounts between a substrate chain's local asset precision and an EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract's ERC-20 precision on every `send`/`on_accept`/`on_timeout`. [1](#0-0) 

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

pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

Both functions compute the scale exponent as `erc_decimals.saturating_sub(local_decimals)`, which silently clamps to `0` whenever `erc_decimals < local_decimals`. That is the wrong-direction rounding/scaling bug: the code only ever knows how to *divide down* (assuming `erc_decimals >= local_decimals`); when the registered ERC-20 has fewer decimals than the local substrate asset, `convert_to_erc20` should instead *divide* by `10^(local_decimals - erc_decimals)`, but because of the saturating subtraction it multiplies by `10^0 = 1`, i.e. does no scaling at all.

`register_token`/`update_token` let a `CreateOrigin` (governance) register arbitrary `(local_id, chains[].decimals)` pairs — nothing enforces `erc_decimals >= local_decimals`, and the docs only say EVM decimals are "typically 18," not that they must be `>=` the local asset's decimals. This is a normal, legitimate registration case (e.g. bridging a 6-decimal ERC-20 to a 12-decimal local asset), not a malicious-admin scenario. [2](#0-1) 

In `send`, the pallet escrows/burns `params.amount` (local decimals) and then computes `erc20_amount = convert_to_erc20(amount, erc_decimals, decimals)` which is dispatched as the `Message.amount` minted on the destination EVM contract. [3](#0-2) 

In `on_accept`, the reverse path (`convert_to_balance`) converts an EVM-originated `Message.amount` back into local balance before releasing escrow or minting.

### Title
Incorrect decimal-scaling direction in `pallet-hyper-fungible-token`'s ERC-20 ↔ local balance conversion causes unbacked minting when `erc_decimals < local_decimals` - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`convert_to_erc20`/`convert_to_balance` derive their scaling exponent as `erc_decimals.saturating_sub(local_decimals)`, which assumes the EVM-side token always has decimals `>=` the local substrate asset. When a token is legitimately registered with `erc_decimals < local_decimals`, the saturating subtraction clamps to `0`, so `convert_to_erc20` performs no down-scaling at all and mints/dispatches an ERC-20 amount that is `10^(local_decimals - erc_decimals)` times too large relative to what was actually escrowed/burned on the substrate side.

### Finding Description
`send()` escrows or burns `params.amount` in the local asset's own decimals, then calls `convert_to_erc20(amount, erc_decimals, decimals)` to build the `Message.amount` sent to the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract, which mints that amount 1:1. [4](#0-3)  The correct behavior when `erc_decimals < local_decimals` is to *divide* the local amount by `10^(local_decimals - erc_decimals)` before dispatch; instead the code multiplies by `10^0 = 1`, so the destination contract mints the full local raw-unit value as if it were already scaled to `erc_decimals`, over-minting by a factor of `10^(local_decimals - erc_decimals)`.

Symmetrically, `on_accept`/`on_timeout` call `convert_to_balance(erc_amount, erc_decimals, decimals)` to translate an incoming EVM-side amount back to local balance before crediting/releasing from escrow. [5](#0-4)  With the same clamp, when `erc_decimals < local_decimals` no up-scaling happens and the local credit is `10^(local_decimals - erc_decimals)` times too small, under-crediting/permanently locking value escrowed on the substrate side.

This is directly analogous to the DODO report's core defect: the conversion helper only implements one rounding/scaling direction and is silently wrong when actual operating conditions invert the assumption it was built for, instead of correctly branching (or rounding conservatively) for both directions.

### Impact Explanation
- On the `send` (escrow/burn → EVM mint) leg, an amount that under-scales instead of over-scales results in the destination EVM contract minting far more ERC-20 tokens than were actually escrowed/burned on the substrate side — an unbacked mint that lets any user drain the token's backing across the bridge (High/Critical, direct value extraction, matches "unbacked mint").
- On the reverse leg (`on_accept`/`on_timeout`), the same clamp under-credits the local asset, permanently freezing the corresponding value in the pallet's escrow account, since the amount released back is `10^(local_decimals - erc_decimals)` times smaller than what was burned on the EVM side.

### Likelihood Explanation
The bug triggers under a completely ordinary, non-malicious configuration — registering any non-BRIDGE token where the destination chain's ERC-20 decimals are lower than the local asset's decimals (a common real-world case, e.g. a 6-decimal EVM stablecoin bridged against a 12-decimal substrate asset). `register_token`/`update_token` place no constraint requiring `erc_decimals >= local_decimals`, so this is reachable by any governance-approved token listing without any malicious intent, and every subsequent `send` from such a chain triggers the flawed conversion.

### Recommendation
Replace the `saturating_sub`-based exponent computation with an explicit signed comparison that scales in the correct direction for both cases:
```rust
if erc_decimals >= local_decimals {
    value * 10^(erc_decimals - local_decimals)   // convert_to_erc20
} else {
    value / 10^(local_decimals - erc_decimals)   // convert_to_erc20, correctly scaling down
}
```
and the inverse for `convert_to_balance`, with the down-scaling direction always rounding down (favoring the escrow) and never silently defaulting to "no scaling."

### Proof of Concept
1. Governance calls `register_token` for asset `X` with `local_decimals = 12` and, for chain `C`, `ChainConfig { decimals: 6, .. }` (a legitimate 6-decimal ERC-20 counterpart).
2. A user calls `send(SendParams { asset_id: X, destination: C, amount: 1_000_000_000_000 /* 1 token at 12 decimals */, .. })`. The pallet burns/escrows `1_000_000_000_000` local units.
3. `convert_to_erc20(1_000_000_000_000, erc_decimals=6, local_decimals=12)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so `erc20_amount = 1_000_000_000_000 * 10^0 = 1_000_000_000_000`.
4. The destination `HyperFungibleToken` contract mints `1_000_000_000_000` raw units at 6 decimals (i.e. `1,000,000` whole tokens) to the beneficiary, instead of the correct `1` whole token (`1_000_000` raw units at 6 decimals) — a `1,000,000×` unbacked over-mint relative to the value actually escrowed.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-58)
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
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L257-310)
```rust
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

			let token_message = Message {
				from: sender.to_vec().into(),
				to: params.recipient.to_vec().into(),
				amount: alloy_primitives::U256::from_be_bytes(erc20_amount.to_big_endian()),
				data: params.call_data.unwrap_or_default().into(),
			};

			let dispatch_post = DispatchPost {
				dest: params.destination,
				from: PALLET_ID.to_bytes(),
				to: token_contract,
				timeout: params.timeout,
				body: Message::abi_encode(&token_message),
			};
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L41-118)
```rust
impl<T: Config> IsmpModule for Pallet<T>
where
	<T as frame_system::Config>::AccountId: From<[u8; 32]>,
	<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance: core::str::FromStr,
	<<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance as core::str::FromStr>::Err:
		core::error::Error + Send + Sync + 'static,
	<<T as Config>::Assets as fungibles::Inspect<T::AccountId>>::Balance:
		From<<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance>,
{
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

		// Convert recipient bytes to substrate AccountId
		// If 32 bytes: use directly. If 20 bytes: left-pad with zeros.
		let mut beneficiary_bytes = [0u8; 32];
		let to_bytes = message.to.as_ref();
		if to_bytes.len() == 32 {
			beneficiary_bytes.copy_from_slice(to_bytes);
		} else if to_bytes.len() == 20 {
			beneficiary_bytes[12..].copy_from_slice(to_bytes);
		} else {
			Err(HftError::InvalidRecipientLength(to_bytes.len()))?;
		}
		let beneficiary: T::AccountId = beneficiary_bytes.into();

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
