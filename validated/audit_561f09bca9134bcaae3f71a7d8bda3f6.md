### Title
Directional decimal-scaling bug in `hyper-fungible-token` ERC20⇄local balance conversion causes unbacked over-mint - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `hyper-fungible-token` pallet's decimal-conversion helpers assume the wrapped ERC-20 asset always has **more or equal** decimals than the local Substrate balance representation. When that assumption is false (local asset decimals > ERC-20 decimals), `saturating_sub` silently collapses the scaling exponent to zero instead of scaling in the opposite direction, producing wrong amounts rather than an error — mirroring the root cause of the referenced `_decimalMultiplier` finding (a decimal-scaling helper that only works for one relative ordering of decimals and mishandles the other).

### Finding Description
`convert_to_balance` and `convert_to_erc20` both compute the scaling exponent as `erc_decimals.saturating_sub(local_decimals)`: [1](#0-0) 

- `convert_to_balance` divides the incoming ERC-20 `U256` value by `10^(erc_decimals.saturating_sub(local_decimals))`, which is only correct when `erc_decimals >= local_decimals`.
- `convert_to_erc20` multiplies the local balance by the same exponent, again only correct when `erc_decimals >= local_decimals`.

If a registered asset has `local_decimals > erc_decimals` (e.g., a remote 6-decimal ERC-20 like USDC bridged into a local 18-decimal balance type), `saturating_sub` returns `0` for both functions instead of the negative exponent that should trigger multiplication (in `convert_to_balance`) or division (in `convert_to_erc20`) in the other direction. The functions silently treat the raw numeric value as already being on the correct scale.

### Impact Explanation
- On the mint path (`convert_to_balance`), a user would receive `10^(local_decimals - erc_decimals)` times **fewer** local tokens than deposited — funds effectively lost/frozen relative to the deposit.
- On the burn/withdraw path (`convert_to_erc20`), converting a local balance back to the ERC-20 representation would multiply by `10^0 = 1` instead of dividing by `10^(local_decimals - erc_decimals)`, producing an ERC-20 payout inflated by that same factor — an unbacked mint that lets a user withdraw far more ERC-20 value than they deposited, directly draining the bridge's backing reserve. This is a concrete "unbacked mint" / fund-theft scenario as defined in scope.

### Likelihood Explanation
Likelihood depends on whether governance/admin registers an asset pairing where the local balance type's decimals exceed the wrapped ERC-20's decimals — a legitimate and plausible configuration (e.g., normalizing all local balances to 18 decimals while wrapping a 6-decimal stablecoin), not a malicious-admin scenario. Once such a pairing exists, every ordinary user transfer/mint/burn triggers the flawed math — no privileged action or attacker-controlled parameter is needed beyond normal asset registration.

### Recommendation
Replace the one-directional `saturating_sub` scaling with a signed comparison that multiplies when `local_decimals > erc_decimals` and divides when `erc_decimals > local_decimals`, matching the bidirectional pattern already correctly implemented elsewhere in the codebase (e.g., `VWAPOracle._normalizeAmount`, which branches on `_decimals < 18` vs `> 18`). Add regression tests for both relative decimal orderings.

### Proof of Concept
Given `erc_decimals = 6` (wrapped USDC) and `local_decimals = 18`:
- `convert_to_balance(value, 6, 18)`: exponent = `6u8.saturating_sub(18) = 0` → divides by `10^0 = 1` → local balance = raw ERC-20 integer, i.e. `10^12` times smaller than the correct 18-decimal-scaled amount.
- `convert_to_erc20(value, 6, 18)`: exponent = `6u8.saturating_sub(18) = 0` → multiplies by `10^0 = 1` → returns the raw local balance as the ERC-20 amount, i.e. `10^12` times larger than correct, allowing withdrawal of far more ERC-20 tokens than were ever deposited.

**Uncertainty note:** I was not able to trace the exact call sites in `module.rs`/`lib.rs` (index limits) to confirm the specific mint/burn extrinsics that invoke these helpers, nor whether asset registration currently permits `local_decimals > erc_decimals` pairings in practice. This should be verified against the pallet's asset-registration logic in a full checkout before treating this as confirmed-exploitable. [2](#0-1)

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
