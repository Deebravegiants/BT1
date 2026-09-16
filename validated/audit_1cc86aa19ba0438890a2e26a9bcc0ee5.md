This confirms the analog. The EVM-side `HyperFungibleToken.send()` burns `params.amount` at the EVM contract's own precision (18 decimals, arbitrary raw wei-like value) and puts the **full unscaled amount** into the ISMP message body unconditionally, without any check that the amount is a multiple of the scale factor required for the substrate destination's lower decimal precision. [1](#0-0) 

On the substrate side, `on_accept` divides that raw amount by `10^(erc_decimals - local_decimals)` using integer (floor) division in `convert_to_balance`, silently truncating any remainder/dust below the local asset's precision. [2](#0-1) [3](#0-2) 

### Title
Cross-chain amount truncation in `pallet-hyper-fungible-token`'s `on_accept`/`on_timeout` permanently burns sub-precision dust with no reduction check on the EVM sender side - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`, `modules/pallets/hyper-fungible-token/src/module.rs`, `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`)

### Summary
`HyperFungibleToken.send()` on EVM chains burns and dispatches an arbitrary `uint256 amount` (at the EVM token's own decimals, e.g. 18) with no check that the amount is a multiple of the destination's precision scale factor. The substrate `pallet-hyper-fungible-token::on_accept` handler converts that amount to local balance via `convert_to_balance`, which performs a floor integer division by `10^(erc_decimals - local_decimals)`. Any remainder below the destination's precision granularity is silently discarded, mirroring the analog report's "no reduction to gwei" precision-loss bug class.

### Finding Description
- `send()` on `HyperFungibleToken.sol` burns `params.amount` unconditionally and encodes it verbatim into the `Message.amount` field of the dispatched POST request: [4](#0-3) . There is no validation that `amount % 10^(erc_decimals - local_decimals) == 0`.
- On the destination substrate chain, `on_accept` in `module.rs` decodes the message and calls `convert_to_balance::<Balance>(U256::from_be_bytes(message.amount), erc_decimals, decimals)` to scale the amount down to local precision before minting/unlocking to the beneficiary: [5](#0-4) .
- `convert_to_balance` performs `value / 10^(erc_decimals.saturating_sub(local_decimals))` — an integer division that floors any fractional remainder: [2](#0-1) .
- Because `register_token`/`update_token` only enforce `config.decimals >= local_decimals` (erc_decimals must be >= local decimals) [6](#0-5) , this scale factor is routinely non-trivial (e.g. 18 EVM decimals vs. 12 substrate decimals → scale factor `10^6`), so any user-submitted amount on the EVM side that isn't an exact multiple of the scale factor has its remainder burned on the source chain but never minted on the destination — the same "wei vs gwei" precision-drop bug class as the reported RioLRTDepositPool issue, just triggered from the message-dispatch (unprivileged `send()`) side instead of an internal share/asset conversion.
- The same truncation recurs in `on_timeout`'s refund path, which uses the identical `convert_to_balance` call before refunding the original sender: [7](#0-6) .

### Impact Explanation
Any unprivileged EVM user calling `HyperFungibleToken.send()` with an amount not aligned to the destination chain's precision scale factor permanently loses the truncated remainder: it is burned on the EVM chain but the substrate side mints/unlocks only the floored amount. This is a direct, repeatable loss of user funds (dust up to `10^(erc_decimals-local_decimals)-1` units per transfer) with no recovery path, and because callers control `params.amount` freely, this can be triggered on every single transfer, not just edge cases.

### Likelihood Explanation
High: the bug is triggered by ordinary usage whenever the EVM token's decimals exceed the destination's local decimals (a configuration explicitly supported and required by `register_token`'s decimals check) and the user picks (or a caller/integration/wallet naively passes) an amount not divisible by the scale factor — which is the common case for any amount not deliberately rounded by the caller (e.g. arbitrary `parseEther` values, DEX-derived quantities, or programmatic transfers).

### Recommendation
Before burning/dispatching in `HyperFungibleToken.send()` (or equivalently before encoding the message), round the amount down to the nearest multiple of the destination's known scale factor (analogous to reducing ETH precision to gwei) and either revert on non-zero remainder or return/keep the dust with the sender instead of burning it. Alternatively, perform the precision check inside `convert_to_balance`/`on_accept` and reject (bounce/timeout) the message when a non-zero remainder is detected, rather than silently discarding it.

### Proof of Concept
1. Register a token via `register_token` with `local_decimals = 12` (e.g., substrate native asset) and EVM chain `config.decimals = 18` (passes the `ErcDecimalsBelowLocal` check since 18 ≥ 12), scale factor = `10^6`.
2. On the EVM chain, a user calls `HyperFungibleToken.send({..., amount: 1_000_000_000_000_000_123})` (not a multiple of `10^6`).
3. `send()` burns the full `1_000_000_000_000_000_123` wei-equivalent from the sender and dispatches the message with that exact amount [1](#0-0) .
4. On the substrate destination, `on_accept` computes `convert_to_balance(1_000_000_000_000_000_123, 18, 12)` = `1_000_000_000_000_000_123 / 10^6` = `1_000_000_000_000` (floor), discarding the `123` remainder units of local-decimal-equivalent value [8](#0-7) .
5. The beneficiary receives strictly less value than was burned on the source chain, and the difference is unrecoverable — no accounting entry tracks or refunds it.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L258-282)
```text
    /**
     * @dev Burns `params.amount` from the caller and sends an ISMP POST request to the
     * destination chain. Fees can be paid in native tokens (via msg.value) or in the
     * host's fee token (pulled from msg.sender).
     * @param params The send parameters including destination, recipient, amount, and optional calldata
     */
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-52)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-101)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-265)
```rust
				let decimals = if local_asset_id == T::NativeAssetId::get() {
					T::Decimals::get()
				} else {
					<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
						local_asset_id.clone(),
					)
				};
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L352-355)
```rust
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```
