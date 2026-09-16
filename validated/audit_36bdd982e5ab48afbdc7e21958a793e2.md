## Analysis

The reported bug is a **missing/incorrect scaling-factor compensation** between two components that assume mismatched numeric precisions (Chainlink script multiplies by 100, contract never divides back). The closest reachable analog in Hyperbridge is the decimals-scaling arithmetic in `pallet-hyper-fungible-token`, which converts amounts between a local Substrate asset's decimals and a remote EVM ERC-20 contract's decimals using a subtraction that silently clamps to zero instead of computing the correct exponent in both directions. [1](#0-0) 

Both helper functions assume `erc_decimals >= local_decimals` always holds:

```rust
pub fn convert_to_balance<B: core::str::FromStr>(value: U256, erc_decimals: u8, local_decimals: u8) -> Result<B, B::Err> {
    let dec_str = (value / U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))).to_string();
    dec_str.parse::<B>()
}

pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

`saturating_sub` returns `0` whenever `local_decimals > erc_decimals`, turning the scale factor into `10^0 = 1` — i.e., **no scaling at all** — in exactly the case where scaling in the opposite direction is required. This is used on every send/receive path:

- `send()` calls `convert_to_erc20(amount, erc_decimals, decimals)` to build the outgoing message amount: [2](#0-1) 
- `on_accept` (minting on receipt) and `on_timeout` (refunding) both call `convert_to_balance(..., erc_decimals, decimals)`: [3](#0-2) [4](#0-3) 

### Title
Decimal-scaling exponent silently clamps to zero for higher-precision local assets, enabling unbacked minting - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`convert_to_erc20` and `convert_to_balance` compute the power-of-ten scale factor as `erc_decimals.saturating_sub(local_decimals)`. This only produces correct results when the EVM contract's decimals are greater than or equal to the local asset's decimals. When a registered local asset has *more* decimals than its paired EVM contract (`local_decimals > erc_decimals`), `saturating_sub` returns `0`, so the functions apply a scale factor of `10^0 = 1` instead of dividing/multiplying by the true `10^(local_decimals - erc_decimals)` difference — exactly analogous to the reported bug where a 100x scaling factor applied on one side of a bridge is never compensated on the other.

### Finding Description
`send()` in `lib.rs` escrows/burns `params.amount` in local (Substrate) precision, then encodes the cross-chain message amount via `convert_to_erc20(amount, erc_decimals, decimals)` [5](#0-4) . If `decimals > erc_decimals` (e.g. a locally registered asset with 18 decimals paired with a destination contract configured for 6 decimals), the function should **divide** by `10^(decimals - erc_decimals)` to shrink the value into the destination's coarser precision, but instead multiplies by `10^0 = 1`, leaving the raw high-precision value unchanged. That inflated value is placed straight into the dispatched ISMP `Message.amount` and delivered to the EVM `HyperFungibleToken`/`BridgeToken` contract's `onAccept`, which mints exactly that many tokens on the destination chain — a mint that is orders of magnitude larger than what was actually escrowed/burned on the source chain.

Symmetrically, `convert_to_balance` is used in `on_accept` (crediting a beneficiary on receipt of a cross-chain transfer) and `on_timeout` (refunding the sender). In the same decimals configuration, the missing division causes an ERC20 amount to be credited without the necessary up-scaling, under-crediting the recipient relative to the value actually locked/burned on the other chain.

Both bugs stem from one root cause: the exponent is computed by unconditional subtraction with saturation, rather than determining which side has more precision and scaling accordingly (multiply on one branch, divide on the other), unlike the correctly bidirectional pattern used elsewhere in the codebase, e.g. `VWAPOracle._normalizeAmount`, which explicitly branches on `decimals < 18` vs `> 18`: [6](#0-5) .

### Impact Explanation
- In `send()` → `convert_to_erc20`: when `local_decimals > erc_decimals` for a registered asset/chain pair, a single unprivileged `send()` extrinsic call causes the destination `HyperFungibleToken` contract to mint an amount inflated by exactly `10^(local_decimals - erc_decimals)` relative to what was actually escrowed/burned on nexus — an unbacked mint of the bridged token, directly draining the peg/backing invariant documented for `BridgeToken` (`the supply of this token is always backed by the pallet's escrow account`) [7](#0-6) .
- In `on_accept`/`on_timeout` → `convert_to_balance`: the mirrored case causes permanent under-crediting/loss of the recipient's or refunded sender's funds by the same factor, since the equivalent value locked on the EVM side is not correctly reflected in the substrate balance minted/transferred.

Both are concrete theft-of-funds / unbacked-mint or fund-freezing outcomes reachable via ordinary token bridge dispatch (`send`) and delivery (`onAccept`/timeout refund), matching the required severity bar (Critical/High).

### Likelihood Explanation
The trigger condition depends only on the *decimals* configuration recorded in `Precisions` for a given `(AssetId, StateMachine)` pair versus the local asset's own decimals — not on any admin/governance behaving maliciously, just an entirely plausible real-world configuration (e.g., an 18-decimal local asset bridged to a 6-decimal ERC-20 deployment, or vice versa for the native asset's `T::Decimals`). Once such a pair exists, every unprivileged user's `send()`/relayed delivery through that route silently mis-scales, making this a systemic, easily triggered issue rather than an edge case requiring adversarial setup.

### Recommendation
Rewrite both `convert_to_balance` and `convert_to_erc20` to branch on which side has more decimals, mirroring the pattern used in `VWAPOracle._normalizeAmount`:

```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```
and the inverse for `convert_to_balance`. Add unit tests covering both `erc_decimals > local_decimals` and `erc_decimals < local_decimals` configurations to prevent regressions.

### Proof of Concept
1. Governance/admin registers a local asset `X` with `local_decimals = 18` and configures `Precisions::<T>::insert(X, dest_chain, 6)` (i.e., the destination `HyperFungibleToken` contract for `X` is deployed with 6 decimals) — a legitimate, non-malicious configuration.
2. A user calls `send(origin, SendParams { asset_id: X, amount: 1_000_000_000_000_000_000 /* 1 token, 18 decimals */, destination: dest_chain, ... })`.
3. Inside `send()`, `erc20_amount = convert_to_erc20(1e18, 6, 18)`. Since `erc_decimals(6).saturating_sub(local_decimals(18)) == 0`, the function computes `1e18 * 10^0 = 1e18` instead of the correct `1e18 / 10^12 = 1_000_000` (1 token at 6 decimals).
4. The ISMP message dispatched to `dest_chain` carries `amount = 1e18`.
5. On delivery, the destination `HyperFungibleToken`/`BridgeToken` contract's `onAccept` mints `1e18` units (i.e., `1e12` times more tokens than the `1e6` that should correspond to the 1 token actually burned/escrowed on the source chain) — an unbacked mint of `999,999,000,000` extra token-units for the cost of burning 1 real token.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L257-301)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-91)
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

**File:** evm/src/apps/BridgeToken.sol (L24-29)
```text
 * @notice The EVM representation of BRIDGE, the native token of the nexus parachain.
 *
 * @dev BRIDGE is native to nexus, so the two ends run the escrow model: `pallet-hyper-fungible-token`
 * escrows the native balance on nexus and this contract mints the equivalent here, meaning the supply
 * of this token is always backed by the pallet's escrow account. Sending back burns here and releases
 * there.
```
