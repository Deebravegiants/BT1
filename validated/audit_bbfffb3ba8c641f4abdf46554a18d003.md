### Title
Loss-of-precision truncation in cross-chain decimal scaling permanently burns dust transfers - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler converts an incoming ERC20-scale amount (18 decimals on the EVM side) into the pallet's local balance decimals using `convert_to_balance`, which performs an unchecked integer division. When the transferred amount is smaller than `10^(erc_decimals - local_decimals)`, the division truncates to zero, silently minting/crediting nothing to the beneficiary while the equivalent value was already burned or escrowed on the source EVM chain.

### Finding Description
`convert_to_balance` scales down an ERC20 `U256` amount by dividing by `10^(erc_decimals - local_decimals)`, with no minimum-amount check and no revert on a zero result: [1](#0-0) 

This mirrors the reported bug class exactly: solidity/Rust integer division of a small numerator by a large denominator (here, the decimals scaling factor, analogous to `owedTime / daysInYear` in the report) truncates toward zero instead of reverting, silently destroying value instead of failing loudly.

This function is invoked from the pallet's ISMP `on_accept` handler when a `HyperFungibleToken`/`WrappedHyperFungibleToken` contract on an EVM chain dispatches a `Send` message to this pallet — a path directly reachable by any unprivileged user who calls `send()` on the EVM contract with a small amount: [2](#0-1) 

The EVM side already burned or locked the full sender amount before dispatching the message (see the `send` extrinsic's mirror-image scale-up via `convert_to_erc20`, and the analogous EVM contract debiting flow): [3](#0-2) 

Because the incoming direction (`on_accept`) is a **successful delivery**, not a timeout, there is no refund path triggered — refunds only fire via `on_timeout`: [4](#0-3) 

So a dust-sized inbound transfer (below the decimal-scaling threshold) results in the beneficiary receiving `0` local balance while the source-chain value is permanently gone — a straightforward "interest owed rounds to zero" analog, but here the truncated value is principal, not just yield.

### Impact Explanation
Any unprivileged token bridger can send an amount whose ERC20-scale value is smaller than `10^(erc_decimals - local_decimals)` (e.g. with 18 vs 12 decimals, any amount under `10^6` wei-equivalent, i.e. a sub-micro-unit of the asset). The corresponding value is burned/escrowed on the EVM side but the Polkadot-side beneficiary receives nothing, and the message is not treated as failed (so no refund fires). This is a permanent, unrecoverable loss of user funds — satisfying the "concrete theft or permanent freezing of funds" bar. While a single dust transfer's absolute loss may be small, the bug is systemic: any relayer, integrator, or automated system generating many small transfers (e.g. calldata-driven micro-payments via the `data` field) accumulates real, permanently lost value with no on-chain signal that anything went wrong.

### Likelihood Explanation
Reaching this path requires no special privilege — only a standard call to `send()` on the paired `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM contract with an amount below the scaling threshold, or accidental underflow from a UI/integration that doesn't account for the decimals mismatch documented for e.g. BRIDGE's 12-vs-18-decimal scaling (`sdk/packages/core` `BridgeToken.sol` explicitly warns about the 10^6 scaling). Given decimals mismatches are a normal, sanctioned configuration in this protocol (not an edge case), dust-sized transfers are a realistic and easily-triggered occurrence.

### Recommendation
In `convert_to_balance`, reject (return an error) rather than silently truncate when the computed local balance is `0` but the input `value` was non-zero. Propagate this as a dispatch error from `on_accept` so the pallet's ISMP dispatcher does not treat the delivery as accepted, or — since the source chain has already debited funds — surface a refund/credit-with-dust event so the value is not simply destroyed.

### Proof of Concept
1. Register an asset with `erc_decimals = 18` and `local_decimals = 12` (a 10^6 scale factor), matching the documented BRIDGE token configuration.
2. On the EVM side, call `send`/bridge with an amount of, e.g., `500_000` wei (i.e., `< 10^6`). The EVM contract burns/locks `500_000` units of the token from the sender.
3. The ISMP message is delivered to `pallet-hyper-fungible-token`'s `on_accept`, which calls `convert_to_balance(500_000, 18, 12)`.
4. `500_000 / 10^6 = 0` (integer division truncates), so the beneficiary is minted/credited `0` local balance.
5. No error is raised and no refund occurs (this is a successful accept, not a timeout), so the `500_000` units burned on the EVM chain are permanently lost with no compensating credit on the destination chain.

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

**File:** modules/pallets/hyper-fungible-token/README.md (L81-89)
```markdown
## ISMP module behaviour

- `on_accept` — receives `Send` messages from the paired EVM contract. Maps
  the source contract back to a local asset via `ContractToAsset`, scales the
  amount using `Precisions`, then mints (non-native) or releases from escrow
  (native) to the beneficiary. Emits `TokenReceived`.
- `on_timeout` — refunds the original sender's balance from escrow or by
  re-minting. Emits `TokenRefunded`.
- `on_response` — unused; this pallet uses post-only messaging.
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L257-295)
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
```
