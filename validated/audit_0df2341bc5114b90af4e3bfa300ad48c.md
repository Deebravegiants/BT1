## Analog Found

### Title
Missing validation that `erc_decimals >= local_decimals` causes silent mis-scaling (unbacked mint) in `hyper-fungible-token` decimal conversion - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The reported bug class — a decimal-scaling exponent computed without validating operand ordering — reproduces in `pallet-hyper-fungible-token`'s cross-chain amount conversion helpers. Instead of reverting (as in the reported `Exchange.sol` case), the pallet's use of `saturating_sub` on `u8` decimals silently clamps the exponent to `0` when `erc_decimals < local_decimals`, producing a scaling factor of `1` instead of the correct value — which can mint/credit amounts off by many orders of magnitude.

### Finding Description
`convert_to_erc20` (used by the unprivileged `send` extrinsic to compute the ERC20-side amount dispatched to the EVM peer contract) and `convert_to_balance` (used by `on_accept`/`on_timeout` to convert an incoming ERC20 amount to the local balance) both compute their scaling exponent as: [1](#0-0) 

```rust
pub fn convert_to_balance<B: core::str::FromStr>(...) -> Result<B, B::Err> {
	let dec_str = (value /
		U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32)))
	.to_string();
	...
}

pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

`erc_decimals.saturating_sub(local_decimals)` never underflows or reverts; when `erc_decimals < local_decimals` it silently returns `0`, so the multiplier/divisor becomes `10^0 = 1` — i.e. **no scaling is applied at all**, even though the two sides use different decimal precisions.

The pallet's `Error` enum even declares a dedicated variant for this exact precondition, `ErcDecimalsBelowLocal` — "Configured ERC decimals are less than the local asset's decimals; precision conversion requires erc_decimals >= local_decimals" — but it is never actually returned by either conversion function: [2](#0-1) 

The call sites (`send` in `lib.rs`, and `on_accept`/`on_timeout` in `module.rs`) pass `erc_decimals`/`local_decimals` straight through with no ordering check before calling `convert_to_erc20`/`convert_to_balance`: [3](#0-2) [4](#0-3) 

`local_decimals` for non-native assets comes from `T::Assets::metadata::decimals`, and `erc_decimals` comes from the governance-set `Precisions` storage per `(AssetId, StateMachine)`. The codebase's own `BridgeToken.sol` documentation shows this asymmetry is a real, expected configuration (18-decimal EVM token vs 12-decimal native asset), confirming `erc_decimals`/`local_decimals` mismatches — including the unsafe direction (`erc_decimals < local_decimals`) — are within the pallet's supported configuration space, not merely a theoretical/malicious-admin scenario: [5](#0-4) 

### Impact Explanation
If any registered token has `erc_decimals < local_decimals` for a given peer chain:
- `send()` (callable by any unprivileged token holder) computes `convert_to_erc20` with exponent `0` instead of the correct `local_decimals - erc_decimals`, sending an ERC20 amount that is too large by a factor of `10^(local_decimals - erc_decimals)`. The peer `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM contract mints that inflated raw value — an **unbacked mint** on the destination chain, reachable from a single user transaction.
- Symmetrically, `on_accept`/`on_timeout` under-convert incoming ERC20 amounts by the same factor, causing recipients to be credited far less than intended (fund loss on receipt / refund).

This satisfies "unbacked mint" and "concrete theft/permanent freezing of funds" criteria, driven entirely by an unprivileged `send()` call plus a plausible (not necessarily malicious) decimals configuration — the same missing-validation root cause as the reported `Exchange.sol` bug, except here it corrupts silently rather than reverting, which is strictly worse.

### Likelihood Explanation
Requires a token registration where the EVM-side decimals are lower than the local substrate asset's decimals for some connected chain. The pallet's own error taxonomy (`ErcDecimalsBelowLocal`) shows this was anticipated as a real risk, and the shipped `BridgeToken` (18 EVM vs 12 native) demonstrates decimal mismatches between chains are a normal, supported pattern — only the specific direction (`erc < local`) needs to occur for exploitation, which is plausible for any future or misconfigured non-native asset registration.

### Recommendation
In `convert_to_balance` and `convert_to_erc20`, explicitly check `erc_decimals >= local_decimals` and return/propagate the existing `ErcDecimalsBelowLocal` error (or equivalent) instead of relying on `saturating_sub`, which silently clamps to a safe-looking but incorrect value of `0`. Add regression tests asserting the conversion functions error out rather than mis-scale when `erc_decimals < local_decimals`.

### Proof of Concept
1. Governance registers asset `X` as non-native with `local_decimals = 18` (via `T::Assets` metadata) and sets `Precisions::<T>::insert(X, evm_chain, 6)` (i.e., `erc_decimals = 6`).
2. Any user calls `send(origin, SendParams { asset_id: X, amount: 1 * 10^18, destination: evm_chain, ... })`.
3. `erc20_amount = convert_to_erc20(1e18, erc_decimals=6, local_decimals=18)` computes exponent `6.saturating_sub(18) = 0`, so `erc20_amount = 1e18 * 10^0 = 1e18` (instead of the correct `1e18 / 10^12 = 1e6`).
4. The dispatched `Message.amount = 1e18` is delivered to the EVM `HyperFungibleToken` contract, which mints `1e18` raw units of a 6-decimal token — `1,000,000,000,000` (one trillion) whole tokens instead of `1` — from burning/escrowing a single token's worth on the substrate side.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L43-59)
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

/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L219-224)
```rust
		/// Peer chain is not an EVM state machine; this pallet bridges substrate <-> EVM only
		NonEvmPeerChain,
		/// Configured ERC decimals are less than the local asset's decimals; precision conversion
		/// requires erc_decimals >= local_decimals
		ErcDecimalsBelowLocal,
	}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L254-296)
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

**File:** evm/src/apps/BridgeToken.sol (L34-37)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
 */
```
