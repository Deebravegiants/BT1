### Title
Unvalidated ERC20→local decimal conversion in `pallet-hyper-fungible-token` truncates cross-chain amounts, permanently trapping dust inside the pallet's escrow account - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`pallet-hyper-fungible-token`'s `convert_to_balance` performs a floor integer division when converting an incoming ERC20-denominated amount to the pallet's local balance precision, with no check that the amount is an exact multiple of the conversion factor. This is the same root cause as Sherlock M-15 (Stargate `convertRate` truncation inside the `Balancer` contract): whenever the amount is not a clean multiple of `10^(erc_decimals - local_decimals)`, the remainder is silently dropped and accumulates, unspendable, inside the pallet's custodial account (`Pallet::<T>::pallet_account()`).

### Finding Description
`convert_to_balance` divides the incoming `U256` ERC20 amount by `10^(erc_decimals - local_decimals)` with no remainder check: [1](#0-0) 

This function is used in both the receive path (`on_accept`) and the timeout/refund path (`on_timeout`) of the ISMP module implementation: [2](#0-1) [3](#0-2) 

For a native-custody token such as `BridgeToken` (18 decimals on EVM, 12 decimals on nexus, a scale factor of `10^6`), any EVM `send()` call whose `amount` is not a multiple of `10^6` causes:
1. The EVM side to fully burn/lock the ERC20 amount (exact, no truncation) — see `HyperFungibleToken.send` burn semantics documented for `BridgeToken`: [4](#0-3) 
2. Nexus's `on_accept` to floor-divide that amount by `10^6` and transfer only the truncated quotient out of `pallet_account()` to the beneficiary: [5](#0-4) 

The un-credited remainder (up to `10^6 - 1` local-precision-equivalent units, i.e. up to 0.999999 of a unit in BRIDGE's 12-decimal denomination) is never transferred to anyone — it stays parked inside `pallet_account()` forever. The identical truncation occurs on the `on_timeout` refund path, so a timed-out cross-chain send also returns strictly less than what was originally escrowed/burned on the source side, with the shortfall stuck in the escrow account.

This exactly parallels the Stargate `Balancer` bug: a fixed conversion rate is applied via integer division with no validation that the input is a clean multiple, so ERC20 dust silently accumulates inside the bridging contract/pallet account instead of being credited, refunded, or explicitly retained via a documented/recoverable mechanism.

### Impact Explanation
Every cross-chain transfer or timeout refund whose amount is not an exact multiple of the erc/local decimal conversion factor permanently strands a fraction of user funds inside `pallet_account()`. There is no extrinsic or code path shown to recover this dust. Over repeated transfers this compounds into a growing, permanently frozen balance — a direct loss to end users (they burn/lock the full amount on one side but receive less on the other), classified as permanent freezing of funds. This is reachable by any unprivileged user simply choosing an `amount` in the EVM `send()` call, or by the natural occurrence of a POST request timing out.

### Likelihood Explanation
High likelihood: nothing prevents a user (accidentally or intentionally) from sending an amount that isn't a multiple of the conversion factor, since decimals like 18 vs 12 (or any similar decimals mismatch, e.g. 18 vs 6) make truncation trivially probable for common "human" amounts. The same conversion function is invoked unconditionally on every `on_accept` and `on_timeout` in the pallet.

### Recommendation
Reject or explicitly handle non-exact conversions in `convert_to_balance`:
- Validate that `value % 10^(erc_decimals - local_decimals) == 0` before accepting the message; if not, either revert with a defined error, or
- Track and refund/credit the truncated remainder (e.g., accumulate per-beneficiary dust and allow it to be claimed, or require the EVM sender-side to pre-round the amount to a multiple of the conversion factor before burning, matching what it will actually deliver).
This mirrors the Sherlock M-15 fix pattern: normalize/round the amount before extracting/burning funds so the accounting on both sides remains exact and no dust silently accumulates in escrow.

### Proof of Concept
1. Register `BridgeToken` on an EVM chain with 18 decimals mapped to nexus's 12-decimal native BRIDGE asset (scale factor `10^6`), as described in `BridgeToken.sol`'s doc comment.
2. A user calls `send()`/bridges back `1_000_000_500` wei of BridgeToken (i.e., not a multiple of `10^6`) to nexus. The EVM contract burns the full `1_000_000_500`.
3. Nexus's `on_accept` computes `convert_to_balance(1_000_000_500, 18, 12)` = `1_000_000_500 / 10^6` = `1000` (floor), crediting the beneficiary 1000 local units instead of the fractional 1000.0000005 units backed by the burn.
4. The un-credited `500` wei-equivalent of ERC20 precision remains permanently inside `pallet_account()` on nexus, with no extrinsic to reclaim it — repeated transfers accumulate this dust indefinitely.

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-101)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L246-265)
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

				// Refund: release escrowed tokens back to the original sender
				if local_asset_id == T::NativeAssetId::get() {
					<T as Config>::NativeCurrency::transfer(
						&Pallet::<T>::pallet_account(),
						&beneficiary,
						amount.into(),
						ExistenceRequirement::AllowDeath,
					)
					.map_err(|e| HftError::TransferFailed(e.into()))?;
```

**File:** evm/src/apps/BridgeToken.sol (L26-36)
```text
 * @dev BRIDGE is native to nexus, so the two ends run the escrow model: `pallet-hyper-fungible-token`
 * escrows the native balance on nexus and this contract mints the equivalent here, meaning the supply
 * of this token is always backed by the pallet's escrow account. Sending back burns here and releases
 * there.
 *
 * Metadata and the nexus peer are fixed in the bytecode rather than passed at deployment, so every
 * chain gets an identical token, and with CREATE2 an identical address for the same deployer and salt.
 *
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```
