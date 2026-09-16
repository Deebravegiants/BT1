### Title
Precision loss in `convert_to_balance` can round incoming Hyper Fungible Token transfers to zero, permanently burning the user's bridged funds - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
The `pallet-hyper-fungible-token` bridge converts the 18-decimal (or otherwise high-precision) ERC20 `amount` carried in a cross-chain `Message` into the local chain's balance denomination by integer division. When the local asset has fewer decimals than the remote ERC20 token, small-but-nonzero incoming amounts are truncated to zero, silently minting/transferring nothing to the beneficiary while the equivalent value has already been burned or escrowed on the source chain.

### Finding Description
`convert_to_balance` performs unchecked integer division to scale an ERC20 `U256` amount down to the local balance type: [1](#0-0) 

This is invoked directly in `on_accept`, the ISMP delivery handler that processes an incoming `PostRequest` from a peer chain's HyperFungibleToken/WrappedHyperFungibleToken contract: [2](#0-1) 

The resulting `amount` is then used directly to mint or transfer funds to the beneficiary, with no check that it is nonzero: [3](#0-2) 

The division is `value / 10^(erc_decimals - local_decimals)`. If `erc_decimals > local_decimals` (e.g., an ERC20 token with 18 decimals bridging to a local asset with 6 or 12 decimals — the same shape as the `BridgeToken` contract's 18-decimal ERC20 representation bridging to nexus's 12-decimal native `BRIDGE`, documented in `evm/src/apps/BridgeToken.sol`), any raw ERC20 amount below `10^(erc_decimals - local_decimals)` truncates to zero. In the `BridgeToken` case that divisor is `10^6`, so ERC20 amounts under `1e6` wei collapse to `0` local balance: [4](#0-3) 

On the sending side, the source chain's contract has already deducted/burned the corresponding balance (via `send()`/`burn` semantics in the HyperFungibleToken solidity contract) before dispatching the message. Because `on_accept` neither reverts nor reports an error for a computed amount of `0`, the request is processed successfully (the module returns `Ok`, emits `TokenReceived` with `amount: 0`), and the tokens are permanently lost — the source-side balance was consumed but the destination beneficiary receives nothing. This mirrors the reported USSD bug class exactly: a legitimate deposit below the ratio of decimal places between the two representations rounds to zero and the depositor's principal is silently destroyed.

Note: `Error::<T>::ErcDecimalsBelowLocal` exists in the pallet's error enum, indicating awareness that `erc_decimals` must be `>= local_decimals`, but this only bounds the *direction* of scaling (guaranteeing division rather than multiplication in `convert_to_balance`) — it does not prevent the truncate-to-zero condition for small amounts, which is the actual vulnerability.

### Impact Explanation
Any dispatcher of a cross-chain HFT transfer (a plain user calling `send()` on an EVM HyperFungibleToken/BridgeToken/WrappedHyperFungibleToken contract, or a relayer submitting the resulting post-request through a genuine consensus proof) can trigger unbacked destruction of value: funds are escrowed/burned on the source chain but the mint/transfer on the destination silently no-ops. This is a direct, permanent loss of user funds reachable from a single unprivileged cross-chain token transfer — no malicious relayer or governance action is required, only an unlucky (or adversarially crafted) small amount relative to the configured decimal precisions.

### Likelihood Explanation
Likelihood is realistic but bounded by the decimal gap configured per asset (`Precisions` storage). For the shipped `BridgeToken` (18 decimals ERC20 vs 12-decimal native BRIDGE), the truncation threshold is `1e6` wei — a trivially small, non-dust ERC20 amount that a legitimate user could send by mistake or that could be deliberately crafted (e.g. to drain via repeated timeouts/refund-path asymmetries, or simply to grief users bridging tiny remainders). Any other asset registered with a similarly large `erc_decimals - local_decimals` gap (governed by `update_asset_precision`/`Precisions`) is equally exposed.

### Recommendation
In `convert_to_balance` (or at its call sites in `on_accept`/`on_timeout`), reject amounts that round to zero after scaling instead of silently proceeding: return an error (e.g. a new `AmountRoundsToZero`/`InvalidAmountConversion` variant) when `value < 10^(erc_decimals - local_decimals)`, causing the request to be treated as a timeout/refundable failure rather than silently consuming the request with no economic effect. Symmetrically, consider adding a client/contract-side minimum-transfer check in the EVM `send()` path to prevent dispatching amounts that will truncate to zero on the receiving chain.

### Proof of Concept
1. Register an asset (e.g. BRIDGE-style) with `erc_decimals = 18` and local `decimals = 12`, so `Precisions::<T>::get(asset_id, dest) == 18` and local `Decimals::get() == 12` (divisor `= 10^6`).
2. On the EVM side, call `HyperFungibleToken.send()` (or `BridgeToken.send()`) with `amount = 500_000` wei (i.e., `< 1e6`), which burns/escrows `500_000` units of the 18-decimal ERC20 token from the sender.
3. The dispatched `Message.amount = 500_000` is relayed and delivered to the substrate pallet's `on_accept`.
4. `convert_to_balance(500_000, 18, 12)` computes `500_000 / 10^6 = 0` (integer division), per `modules/pallets/hyper-fungible-token/src/impls.rs` lines 43-52.
5. `on_accept` proceeds to `mint_into`/`transfer` with `amount = 0` and emits `TokenReceived { amount: 0, .. }` — the call succeeds, but the beneficiary receives no tokens, while the 500,000 wei was already burned/escrowed on the source chain.

### Citations

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

**File:** evm/src/apps/BridgeToken.sol (L34-37)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
 */
```
