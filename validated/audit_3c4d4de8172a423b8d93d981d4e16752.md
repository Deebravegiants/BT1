### Title
Silent truncation of dust during ERC20→local decimal conversion permanently destroys value in `pallet-hyper-fungible-token` on_accept/on_timeout - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
`pallet-hyper-fungible-token` bridges tokens between EVM chains (18-decimal-style precision, configurable per registration) and this chain's native/local assets, which may have far fewer decimals. `register_token`/`update_token` only enforce `config.decimals >= local_decimals` [1](#0-0) , with no floor on how small `local_decimals` may be (unlike the referenced fix that restricted supported decimals to 6–18 to bound rounding error). When an incoming message is processed, `convert_to_balance` performs a plain integer division to scale the ERC20 amount down to local precision, with no remainder check and no accounting for the discarded fraction [2](#0-1) .

### Finding Description
The EVM-side `HyperFungibleToken`/`WrappedHyperFungibleToken` contracts let a caller burn/escrow an arbitrary `uint256 amount` with no relationship enforced to the destination chain's local asset precision — `send`/`_buildDispatchPost` simply forwards `params.amount` verbatim [3](#0-2) .

On delivery, `on_accept` (and the timeout refund path `on_timeout`) converts that ERC20 amount into local balance units via `convert_to_balance`:
```
value / U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
``` [2](#0-1)  This is straight integer (floor) division. Any remainder — i.e., any portion of `amount` that is not an exact multiple of `10^(erc_decimals - local_decimals)` — is silently discarded. There is no `require` on the remainder, no partial refund, and no event that surfaces the lost dust; `module.rs::on_accept` mints/transfers only the truncated `amount` and emits `TokenReceived` with that truncated value [4](#0-3) .

The severity scales inversely with `local_decimals`, exactly as described in the reference report: the wider the decimal gap (which is unbounded here — `local_decimals` could be 0, and the pallet only checks `erc_decimals >= local_decimals`, so an asset registered with `decimals = 0` and `erc_decimals = 18` is fully valid), the larger the truncation window. For a `local_decimals = 0` asset paired with `erc_decimals = 18`, any ERC20 amount less than `10^18` wei converts to `0` local units — the beneficiary receives nothing while the equivalent value was burned/escrowed on the EVM side, and for a native-custody asset (escrow model, e.g. `BridgeToken` docs describe exactly this scale-by-`10^6` pattern for a 12-decimal native asset) the escrow account permanently retains the un-released dust with no path to reclaim or reconcile it [5](#0-4) . For non-native (mint/burn) assets the discarded fraction is destroyed entirely on both sides: burned on EVM, never minted on the destination.

This mirrors the referenced report's rounding-in-decimal-conversion bug class (precision loss growing as decimals shrink, unit loss for low-decimal high-value tokens) but manifests here as a token-bridge mint/burn precision bug rather than an AMM liquidity-math bug.

### Impact Explanation
This is a concrete, permanent loss-of-funds bug reachable by any unprivileged user calling `send()`/`fillOrder`-style bridging on the EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract, or the reciprocal `send` extrinsic on `pallet-hyper-fungible-token`. For a token registered with low `local_decimals` relative to the erc-side decimals, a user's cross-chain transfer can have up to `10^(erc_decimals - local_decimals) - 1` ERC20 wei silently and unrecoverably destroyed, with no revert, no refund and no on-chain signal beyond a `TokenReceived`/`TokenRefunded` event carrying the truncated amount. Because `local_decimals` has no enforced lower bound, governance (via `CreateOrigin`) registering a normal-looking low-decimal, high-value asset makes every transfer whose ERC20 amount isn't an exact multiple of the scale factor lossy, and worst case (amount below the scale factor) the beneficiary gets zero.

### Likelihood Explanation
Any legitimate user is likely to trigger this unintentionally, since off-chain wallets/SDKs specify amounts in the EVM token's own decimal units and have no reason to align to the destination local-asset's coarser precision; the SDK/bridge UI does not appear to enforce or round amounts to the scale factor before dispatch. The bug triggers on ordinary token transfers, not adversarial edge cases, so likelihood is high for any token registered with a decimal gap.

### Recommendation
- Bound `local_decimals` (and thus the maximum decimal gap) the same way the referenced fix did — e.g. require `local_decimals` be within a sane range (e.g. ≥ 6) relative to `erc_decimals`, or cap `erc_decimals - local_decimals`.
- In `convert_to_balance`, `require(value % scale == 0)` (reject non-representable amounts) rather than silently flooring, forcing the EVM-side caller/SDK to only submit amounts that convert exactly; alternatively, return/refund the truncated remainder explicitly (e.g. emit the dust amount and credit it to a reclaimable account, or reject the transfer up front on the EVM side by validating `amount % 10^(erc_decimals-local_decimals) == 0` before burning).
- Symmetrically validate amounts on the EVM contracts before burning/escrowing, using the same decimals metadata already tracked (`Precisions`), so dust never leaves the sender's control in the first place.

### Proof of Concept
1. Governance registers asset `X` via `register_token` with `native = false` (mint/burn model) and `chains[EVM-1].decimals = 18`; `X`'s local `Assets` pallet decimals = `0` (passes `ensure!(config.decimals >= local_decimals, ErcDecimalsBelowLocal)` since `18 >= 0`) [6](#0-5) .
2. A user on EVM-1 calls `HyperFungibleToken.send({ amount: 1_500_000_000_000_000_000 /* 1.5e18 wei */, ... })`, which burns exactly `1.5e18` units of the ERC20 representation of `X` from the caller [7](#0-6) .
3. On delivery, `on_accept` computes `erc_decimals = 18`, `local_decimals = 0`, and calls `convert_to_balance(1_500_000_000_000_000_000, 18, 0)` → `1_500_000_000_000_000_000 / 10^18 = 1` [2](#0-1) .
4. The pallet mints `1` unit of `X` to the beneficiary and emits `TokenReceived { amount: 1 }` [8](#0-7) ; the remaining `0.5e18` wei (half of the whole-token value the user burned) is permanently unaccounted for — burned on the EVM chain, never minted on this chain, with no error and no recovery mechanism.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L336-367)
```rust
			let local_decimals = if registration.local_id == T::NativeAssetId::get() {
				T::Decimals::get()
			} else {
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					registration.local_id.clone(),
				)
			};

			NativeAssets::<T>::insert(registration.local_id.clone(), registration.native);

			let chains: Vec<StateMachine> = registration.chains.keys().cloned().collect();
			for (chain, config) in registration.chains {
				// This pallet bridges substrate <-> EVM only; reject non-EVM peers.
				if !matches!(chain, StateMachine::Evm(_)) {
					return Err(Error::<T>::NonEvmPeerChain.into());
				}
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
				let token_contract = config.token_contract.0.to_vec();
				TokenContracts::<T>::insert(
					chain,
					registration.local_id.clone(),
					token_contract.clone(),
				);
				ContractToAsset::<T>::insert(
					chain,
					token_contract,
					registration.local_id.clone(),
				);
				Precisions::<T>::insert(registration.local_id.clone(), chain, config.decimals);
```

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L237-256)
```text
    function _buildDispatchPost(SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L258-260)
```text
    /**
     * @dev Burns `params.amount` from the caller and sends an ISMP POST request to the
     * destination chain. Fees can be paid in native tokens (via msg.value) or in the
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L84-117)
```rust
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
