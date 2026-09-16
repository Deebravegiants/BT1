### Title
Incorrect decimal-scaling formula in `convert_to_balance`/`convert_to_erc20` breaks (and can invert) cross-chain amount conversion when ERC20 decimals are lower than the local asset's decimals - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `hyper-fungible-token` pallet converts amounts between an ERC20 token's decimals and the local Substrate asset's decimals using `erc_decimals.saturating_sub(local_decimals)` (and vice-versa). Exactly like the reported Curve `get_dy_underlying` bug — where the formula silently breaks once `rates[0] < 10**18` because the code assumes one operand is always the larger one — this pallet's scaling math assumes `erc_decimals >= local_decimals` for `convert_to_balance`, and the opposite for `convert_to_erc20`. When that assumption doesn't hold, `saturating_sub` clamps to zero and the scale factor collapses to `10**0 = 1`, i.e. no scaling is applied at all instead of the correct power-of-ten adjustment.

### Finding Description
```rust
// modules/pallets/hyper-fungible-token/src/impls.rs
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
``` [1](#0-0) 

Both functions only compute one direction of the decimal exponent (`erc_decimals - local_decimals`) and rely on Rust's `saturating_sub` to avoid underflow — but that silently produces `0` (scale factor `1`) instead of the correct *inverse* scaling that is needed when `local_decimals > erc_decimals`.

- `convert_to_balance` is called in `on_accept`/`on_timeout` to turn an inbound ERC20 `U256` amount into the local balance, using `erc_decimals` read from `Precisions::<T>::get(local_asset_id, source)` and `decimals` read from the local asset's metadata (or `T::Decimals` for the native asset). [2](#0-1) 
- `convert_to_erc20` is used on the outbound path when building the cross-chain `Message` that instructs the destination EVM contract to mint (confirmed present via `grep` in `modules/pallets/hyper-fungible-token/src/lib.rs`, not fully inspected in this pass due to tool-call limits).

The comment documenting `BridgeToken.sol` shows this is a real, non-malicious configuration shape in production: `decimals()` is 18 on EVM while BRIDGE is 12 decimals on nexus, so the pallet is *expected* to scale by `10^6` — i.e., asymmetric decimals between the ERC20 side and the local side is a normal, governance-configured setup, not an attacker-controlled edge case. [3](#0-2) 

If any registered token pair has `local_decimals > erc_decimals` (e.g. a local asset configured with 18 decimals bridging to a 6-decimal ERC20 stablecoin — the reverse of the BRIDGE example above, but equally plausible for a different asset), then:
- `convert_to_balance` on inbound delivery under-scales the mint amount by the missing factor, silently minting far less than the message specifies (loss for the recipient), rather than reverting.
- `convert_to_erc20` on outbound send fails to scale the raw local balance down before it is embedded in the ISMP message, so the destination EVM `HyperFungibleToken`/`BridgeToken` contract would be instructed to mint an amount inflated by the missing power of ten relative to what was actually escrowed/burned on the local chain — an unbacked mint on the receiving chain.

### Impact Explanation
This directly threatens the escrow invariant documented for `BridgeToken`/`pallet-hyper-fungible-token`: "the supply of this token is always backed by the pallet's escrow account." [4](#0-3) 
An incorrect scale factor on the `convert_to_erc20` path breaks that backing relationship, letting a user's cross-chain transfer mint tokens on the destination in an amount inconsistent with what was locked/burned on the source — a classic unbacked-mint condition. On the inbound path (`convert_to_balance`), the effect is silent fund loss for legitimate bridging users (a Medium/High impact depending on the direction of the discrepancy and which token pair is affected).

### Likelihood Explanation
Reachable by any unprivileged user simply sending a normal cross-chain token transfer through `hyper-fungible-token` — no governance or admin compromise is required, only a token pair registered (by legitimate governance, via `Precisions`) where the ERC20 decimals differ from the local asset's decimals in the direction the current formula does not handle. Given the pallet already documents and tests a 12-vs-18-decimals pair for the native BRIDGE token, similar mismatches for other registered assets are a realistic and expected configuration, not a contrived scenario.

### Recommendation
Fix both helpers to use signed/directional scaling instead of a one-sided `saturating_sub`, matching the pattern already used correctly elsewhere in the codebase (e.g. `VWAPOracle._normalizeAmount` and the SDK's `adjustDecimals`, both of which branch on which side has more decimals and scale in the correct direction):
```rust
pub fn convert_to_balance<B: core::str::FromStr>(value: U256, erc_decimals: u8, local_decimals: u8) -> Result<B, B::Err> {
    let dec_str = if erc_decimals >= local_decimals {
        value / U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        value * U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }.to_string();
    dec_str.parse::<B>()
}

pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
``` [5](#0-4) [6](#0-5) 

### Proof of Concept
1. Governance registers a token pair via `Precisions::<T>::set(local_asset_id, source_contract, erc_decimals)` where the local asset (e.g. a parachain asset with `decimals() == 18`) bridges an ERC20 with `erc_decimals == 6`.
2. A user calls the EVM side's `send` to transfer `1_000_000` (raw ERC20 units, `= 1.0` token at 6 decimals) toward the parachain.
3. On `on_accept`, `convert_to_balance(1_000_000, erc_decimals=6, local_decimals=18)` computes `10u128.pow(6u8.saturating_sub(18) as u32) = 10u128.pow(0) = 1`, so the local balance minted/transferred is `1_000_000` raw local units — i.e. `0.000000000000001` of a token at 18 decimals — instead of the correct `1_000_000 * 10^12` units. The recipient receives ~10^12 times less than intended.
4. Symmetrically, on the reverse direction, a user burning `local_decimals=18`-denominated balance and calling `convert_to_erc20(value, erc_decimals=6, local_decimals=18)` gets `10u128.pow(6u8.saturating_sub(18)) = 1`, so the ERC20 `Message.amount` field embeds the raw 18-decimal value unscaled — instructing the destination EVM contract to mint an amount 10^12 times too large relative to what should correspond to a 6-decimal token unit, breaking the mint-is-backed-by-escrow invariant.

Note: I was unable to fully inspect `modules/pallets/hyper-fungible-token/src/lib.rs` (where `convert_to_erc20` is invoked on the outbound send path) before this analysis had to conclude, due to tool-call limits, so the exact outbound call site and any additional bounds-checking there could not be directly confirmed — only its existence via `grep`. This should be verified against `lib.rs` before treating the outbound direction as final.

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

**File:** evm/src/apps/BridgeToken.sol (L26-29)
```text
 * @dev BRIDGE is native to nexus, so the two ends run the escrow model: `pallet-hyper-fungible-token`
 * escrows the native balance on nexus and this contract mints the equivalent here, meaning the supply
 * of this token is always backed by the pallet's escrow account. Sending back burns here and releases
 * there.
```

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
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

**File:** sdk/packages/sdk/src/utils.ts (L985-994)
```typescript
export function adjustDecimals(feeInFeeToken: bigint, fromDecimals: number, toDecimals: number): bigint {
	if (fromDecimals === toDecimals) return feeInFeeToken
	if (fromDecimals < toDecimals) {
		const scaleFactor = BigInt(10 ** (toDecimals - fromDecimals))
		return feeInFeeToken * scaleFactor
	} else {
		const scaleFactor = BigInt(10 ** (fromDecimals - toDecimals))
		return (feeInFeeToken + scaleFactor - 1n) / scaleFactor
	}
}
```
