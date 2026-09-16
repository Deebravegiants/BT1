### Title
Missing bidirectional scaling in ERC20↔local decimal conversion causes unbacked cross-chain mint / fund loss - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
`convert_to_erc20` and `convert_to_balance` in `pallet-hyper-fungible-token` only scale in one direction (`erc_decimals.saturating_sub(local_decimals)` / vice versa). When the destination/source decimals are *lower* than the local asset's decimals, `saturating_sub` clamps to zero, silently skipping the required scaling and passing the raw integer through unchanged — an analog of the Bancor-style "low decimal token" precision bug described in the external report, but here it is a broken conversion rather than merely coarse precision.

### Finding Description
The scaling helpers are: [1](#0-0) 

```
convert_to_balance: value / 10^(erc_decimals.saturating_sub(local_decimals))
convert_to_erc20:   value * 10^(erc_decimals.saturating_sub(local_decimals))
```

Both formulas assume `erc_decimals >= local_decimals` always. `send()` calls `convert_to_erc20(amount, erc_decimals, decimals)` to build the outbound `Message.amount` after the local asset has already been burned/escrowed at `decimals` precision: [2](#0-1) 

If the *local* asset has more decimals than the destination's registered `erc_decimals` (e.g. local asset = 18 decimals, destination ERC20 = 6 decimals), `erc_decimals.saturating_sub(local_decimals)` clamps to 0, so `convert_to_erc20` multiplies by `10^0 = 1` instead of *dividing* by `10^12`. The outbound message therefore carries the raw 18-decimal integer as if it were a 6-decimal amount — a 10^12x inflation of what should be minted on the destination chain, while only the correctly-scaled (small) amount was burned/escrowed locally. This is an unbacked mint reachable by any user calling `send()` with a token pair configured this way.

Symmetrically, `on_accept()` uses `convert_to_balance(erc_amount, erc_decimals, decimals)` to credit the beneficiary: [3](#0-2) 

If the *source* `erc_decimals` is lower than local `decimals` (the inverse mismatch), `erc_decimals.saturating_sub(local_decimals)` again clamps to 0, so the function fails to multiply up by `10^(local_decimals - erc_decimals)`, crediting the beneficiary with a vastly smaller amount than intended (effective fund loss/freezing for the recipient).

`Precisions` is populated per (asset, chain) via `register_token`/`update_token` with an arbitrary EVM-side decimals value chosen by `CreateOrigin`/governance, and nothing in the pallet enforces `erc_decimals >= local_decimals` or vice versa — the helper functions are one-directional by construction, not merely by misconfiguration.

### Impact Explanation
Any token pair where the destination `erc_decimals` is smaller than the local asset's decimals turns every `send()` into an unbacked-mint primitive: the source chain burns/escrows a small (correctly-scaled) amount while the destination contract mints an amount inflated by `10^(local_decimals - erc_decimals)`. This is a direct, attacker-triggerable theft/mint vector, not merely a "low precision" quoting nuisance as in the Bancor report — it is a broken conversion that can drain the destination's backing or mint unlimited value depending on custody model. The opposite decimals ordering silently under-credits/freezes user funds on `on_accept`. Both qualify as High/Critical per Hyperbridge's token bridge mint/burn threat model.

### Likelihood Explanation
Triggering requires only a normal, permissionless `send()` call from any user, provided the pallet is configured (via governance) with a token whose local decimals exceed its EVM decimals on some destination chain (common for reasonable configurations, e.g. an 18-decimal wrapped asset paired with a 6-decimal USDC-style token). No attacker privilege beyond being a token holder is needed; the bug is purely in the arithmetic helper, independent of governance intent.

### Recommendation
Rewrite `convert_to_balance`/`convert_to_erc20` to branch on the sign of `erc_decimals - local_decimals` and apply the correct multiply-or-divide in each direction (e.g. `if erc_decimals >= local_decimals { value * 10^(erc-local) } else { value / 10^(local-erc) }`), and add a unit/property test matrix covering `erc_decimals < local_decimals`, `==`, and `>` in both `send` and `on_accept` directions.

### Proof of Concept
Given local asset decimals = 18 and a destination chain's registered `Precisions` entry `erc_decimals = 6`:
1. User calls `send(asset_id, destination, amount = 1_000_000_000_000_000_000 /* 1 token, 18 decimals */)`.
2. Pallet burns/escrows exactly `1e18` units of the local 18-decimal asset (correct).
3. `convert_to_erc20(1e18, erc_decimals=6, local_decimals=18)` computes `10u128.pow(6u8.saturating_sub(18) as u32) = 10u128.pow(0) = 1`, returning `erc20_amount = 1e18` instead of the correct `1e6`.
4. The dispatched `Message.amount` (1e18, interpreted as 6-decimal units) instructs the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract to mint `1e18` raw units = `1,000,000,000,000` whole tokens (1 trillion), for only 1 token burned on the source — an unbacked mint of ~10^12x. [4](#0-3) [2](#0-1)

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-296)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

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
