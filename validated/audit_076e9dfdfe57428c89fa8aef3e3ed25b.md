## Title
Missing `erc_decimals >= local_decimals` enforcement in `pallet-hyper-fungible-token` causes unbacked cross-chain mints/burns (untracked bad debt) — (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s decimal-scaling helpers assume the destination ERC20's decimals are always `>=` the local asset's decimals. The pallet even defines an `Error::ErcDecimalsBelowLocal` for the inverse case [1](#0-0) , but that error is only referenced (declared) in `lib.rs` and grep shows no call site actually raising it during `register_token`/`update_token` validation or in the `send`/`on_accept` hot paths. This means a misconfigured (or attacker-influenced, if `register_token`'s admin ever configures a token where the remote ERC20 has fewer decimals than the local asset) `Precisions` entry silently breaks the fixed-point conversion, causing minted/escrowed amounts on one side of the bridge to no longer be backed by the correct amount on the other side — the same "coverage of the collateral is not 100%" class of bug as the source report, just realized as a cross-chain custody mismatch instead of a stablecoin-market mismatch.

### Finding Description
The scaling helpers in `modules/pallets/hyper-fungible-token/src/impls.rs` are: [2](#0-1) 

Both `convert_to_balance` and `convert_to_erc20` compute the exponent as `erc_decimals.saturating_sub(local_decimals)`. `saturating_sub` clamps to `0` whenever `erc_decimals < local_decimals`, silently turning the scaling factor into `10^0 = 1` instead of correctly scaling in the opposite direction. The pallet's own documentation states this precondition explicitly ("Divides by 10^(erc_decimals - local_decimals) to scale down… Configured ERC decimals are less than the local asset's decimals; precision conversion requires erc_decimals >= local_decimals" — see the `ErcDecimalsBelowLocal` error and its doc comment) [1](#0-0) , but no code path was found (via `grep_search` across the whole repo) that actually returns `ErcDecimalsBelowLocal` before or during a `send`/`on_accept` call.

Both `send()` and the `on_accept` `IsmpModule` handler pull `Precisions::<T>::get(asset_id, chain)` — a value governance sets via `register_token`/`update_token` — and pass it straight into `convert_to_erc20` / `convert_to_balance` with no `ensure!(erc_decimals >= local_decimals, ...)` guard: [3](#0-2) [4](#0-3) 

If `Precisions` for an `(asset, chain)` pair is ever configured with `erc_decimals < local_decimals` (a plausible governance/config error — e.g. a local 18-decimal asset paired against a destination contract declared with 6 decimals), the conversion silently degenerates to a 1:1 pass-through instead of the intended scale-down/up:
- On `send()`, `convert_to_erc20` no longer multiplies the outgoing amount by the correct factor, so the ISMP message dispatched to the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract carries an amount denominated in the *wrong* scale — the contract will mint/unlock an amount many orders of magnitude larger (or smaller) than what was actually escrowed/burned on the source chain.
- Symmetrically, on `on_accept()`, `convert_to_balance` will credit the local beneficiary with an amount that no longer matches what was burned/locked on the remote EVM side.

This is structurally the same failure mode as the source report's "coverage of the collateral is not 100%" — value minted on one leg of a two-sided custody system is not backed by the corresponding value locked on the other leg — except here it's realized via a decimal-scaling defect in a token-bridge accounting path rather than a stablecoin/perp market. As with the report, the protocol has no functionality to detect or query this drift after the fact; the escrow/mint ledgers on the two chains simply diverge with each cross-chain transfer through the misconfigured pair.

### Impact Explanation
A wrongly configured `Precisions` entry lets every `send()` and every inbound message for that `(asset, chain)` pair mint/release funds on the receiving side that are unbacked by the correct amount escrowed/burned on the sending side (or vice versa, causing the sending side to escrow far more than the receiving side credits, permanently locking user funds). Reachable via a single unprivileged, signed `send()` extrinsic once the misconfiguration exists — an ordinary token bridger triggers the mismatch — so this can result in either theft/unbacked mint (attacker sends a small amount and receives a disproportionately large mint on the destination) or a permanent freeze of funds (dust-level destination credit for a large source escrow). Both outcomes match the "unbacked mint" / "permanent freezing of funds" acceptance criteria.

### Likelihood Explanation
This bug requires a governance/config error (an `(asset, chain)` `Precisions` row where `erc_decimals < local_decimals`) to be introduced via `register_token`/`update_token`. It is not exploitable purely by an external attacker without that misconfiguration, so likelihood is contingent on operational error rather than a purely permissionless attack path — but there is no on-chain invariant preventing it, and the presence of the declared-but-unused `ErcDecimalsBelowLocal` error strongly suggests the developers intended to guard this exact case and the guard is missing/dead code, indicating a real gap rather than a defense-in-depth omission.

### Recommendation
Add an explicit `ensure!(erc_decimals >= local_decimals, Error::<T>::ErcDecimalsBelowLocal)` check in `register_token`, `update_token`, and defensively in both `send()` and `on_accept()` before calling `convert_to_erc20`/`convert_to_balance`, so a misconfigured pair is rejected outright rather than silently truncating the scaling factor to `10^0`. Additionally, replace `saturating_sub` with a checked subtraction that hard-errors when `erc_decimals < local_decimals`, since silent saturation is what turns a config mistake into a silent fund-accounting bug.

### Proof of Concept
1. Governance calls `register_token`/`update_token` for asset `X` (local `decimals = 18`) with `ChainConfig { token_contract, decimals: 6 }` for destination `Evm(1)` (i.e. `erc_decimals (6) < local_decimals (18)`) — no error is raised because no invariant check exists [5](#0-4) .
2. A user calls `send(SendParams { asset_id: X, amount: 1_000_000_000_000_000_000 /* 1 token, 18dp */, destination: Evm(1), ... })`. Inside `send()`, `convert_to_erc20(amount, 6, 18)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so `erc20_amount = amount * 10^0 = 1_000_000_000_000_000_000` unchanged [6](#0-5) .
3. The dispatched `Message.amount` field therefore encodes `1e18` raw units even though the destination `HyperFungibleToken` contract is denominated in 6 decimals, so on delivery it mints/unlocks `1e18` "USDC-like" units — 10^12 times the value of the 1 token actually escrowed/burned on the source chain — creating unbacked mint on the destination side that is never reconciled against the source-side escrow, i.e. untracked bad debt in the bridge's custody accounting.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L219-224)
```rust
		/// Peer chain is not an EVM state machine; this pallet bridges substrate <-> EVM only
		NonEvmPeerChain,
		/// Configured ERC decimals are less than the local asset's decimals; precision conversion
		/// requires erc_decimals >= local_decimals
		ErcDecimalsBelowLocal,
	}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-300)
```rust
			let token_contract =
				TokenContracts::<T>::get(params.destination, params.asset_id.clone())
					.ok_or(Error::<T>::TokenContractNotFound)?;
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

			let token_message = Message {
				from: sender.to_vec().into(),
				to: params.recipient.to_vec().into(),
				amount: alloy_primitives::U256::from_be_bytes(erc20_amount.to_big_endian()),
```

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-118)
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

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L66-77)
```rust
/// Per-chain configuration for a registered token
#[derive(
	Debug, Clone, Encode, Decode, DecodeWithMemTracking, scale_info::TypeInfo, PartialEq, Eq,
)]
pub struct ChainConfig {
	/// The HyperFungibleToken/WrappedHyperFungibleToken EVM contract address on this chain.
	/// A fixed 20-byte EVM address: this pallet bridges substrate <-> EVM only, so a
	/// (non-EVM) substrate peer module id cannot be registered here.
	pub token_contract: H160,
	/// ERC20 decimals on this chain
	pub decimals: u8,
}
```
