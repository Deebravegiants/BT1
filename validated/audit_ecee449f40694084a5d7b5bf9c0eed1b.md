### Title
Precision loss (integer division) in `convert_to_balance` truncates incoming cross-chain amounts to zero, permanently burning user funds - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s inbound message handler converts an incoming ERC20-denominated `uint256` amount into the pallet's local balance type by dividing by `10^(erc_decimals - local_decimals)`. Any raw amount smaller than that scale factor — or simply not an exact multiple of it — truncates the fractional remainder to nothing, while the corresponding EVM-side tokens have already been irrevocably burned. This is the same integer-division/precision-loss bug class as the referenced DODO `getUserQuota` finding, but here it directly destroys user funds instead of just miscalculating a quota.

### Finding Description
`convert_to_balance` performs a pure integer division with no remainder handling or minimum-amount check: [1](#0-0) 

This is invoked in `on_accept` (message delivered from an EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` peer to the substrate side) to compute the local amount to mint/transfer to the beneficiary: [2](#0-1) 

The scale factor comes directly from the registered `erc_decimals` for that chain, e.g. for `BridgeToken` the EVM side is fixed at 18 decimals while the substrate BRIDGE asset is 12 decimals, giving a `10^6` divisor as documented in the contract itself: [3](#0-2) 

On the EVM sending side, `send()` burns `params.amount` unconditionally — nothing constrains the amount to be an exact multiple of the peer's decimal scale factor: [4](#0-3) 

So a user (or any integrator building on `HyperFungibleToken`) who sends any amount whose low-order digits fall below the scale factor (e.g. less than `1e6` wei of an 18-decimal token bridging to a 12-decimal asset, or the whole amount if it is under that threshold) has those tokens burned on the source chain, but `convert_to_balance` on the destination floors the division and mints/transfers a smaller (possibly zero) amount to the beneficiary. The truncated remainder is not tracked, refunded, or re-escrowed anywhere — it is simply gone. This mirrors the DODO issue exactly: `tokenBalance * price / 10^(decimals)` truncating to zero when the numerator is smaller than the denominator, except here the truncated value corresponds to already-burned/escrowed real funds rather than a discretionary quota figure.

Note that the opposite direction (`convert_to_erc20`, local → ERC20) only ever multiplies (scales up), which is lossless given the `ErcDecimalsBelowLocal` registration invariant, so the round-trip on `on_timeout` refunds correctly. The vulnerability is isolated to the EVM→substrate inbound path where the numeric precision of the *source* amount is not controlled by the destination pallet.

### Impact Explanation
Any inbound cross-chain transfer whose amount is not an exact multiple of `10^(erc_decimals-local_decimals)` loses the truncated remainder permanently; amounts smaller than that factor are fully destroyed (burned on the EVM side, zero minted on the substrate side). This is a direct, permanent loss of user funds through the token-bridge mint/burn path with no error, revert, or recovery mechanism, satisfying the "permanent freezing/loss of funds" impact bar. Because `HyperFungibleToken` is a generic, permissionlessly deployable base contract (per the docs, any project can `deploy` and `configure` one), the affected decimal mismatch (e.g., 18 vs 12, or 18 vs 6) is a common, realistic configuration, not a contrived edge case.

### Likelihood Explanation
Reachable by any unprivileged user calling `send()` on a deployed `HyperFungibleToken`/`BridgeToken` contract with an amount not aligned to the destination pallet's decimal scale factor — no special privileges, governance, or malicious actors required. Given `BRIDGE`'s documented 18→12 decimal scaling (`10^6` divisor), any transfer amount with nonzero digits below `1e6` wei triggers loss, which is trivially reachable by ordinary user input (e.g., typing a "round" token amount in a UI that isn't perfectly aligned, or any amount under `0.000001` BRIDGE).

### Recommendation
In `convert_to_balance`, either (a) reject/revert amounts that are not exact multiples of `10^(erc_decimals-local_decimals)` before burn/escrow on the sending contract, so no value can ever be dispatched that would round to a smaller amount on receipt, or (b) track and carry forward the truncated remainder (e.g., accumulate dust per-beneficiary/per-asset and allow it to be claimed once it exceeds one local unit) rather than silently discarding it. The safest fix is to enforce alignment on the EVM `send()`/`SendParams.amount` validation, since that is the point where the burn is irreversible.

### Proof of Concept
1. Deploy `BridgeToken` on an EVM chain (18 decimals) and register it with `pallet-hyper-fungible-token` on nexus, where BRIDGE has 12 decimals (`erc_decimals=18`, `local_decimals=12`, scale factor `10^6`), matching the documented configuration in `evm/src/apps/BridgeToken.sol`.
2. A user calls `BridgeToken.send({..., amount: 500_000})` (i.e., `0.0000000000005` tokens in 18-decimal terms, or any amount `< 1_000_000`). `_burn(msg.sender, 500_000)` executes, permanently destroying the sender's balance. [5](#0-4) 
3. The ISMP POST is delivered to nexus; `on_accept` calls `convert_to_balance(U256::from(500_000), 18, 12)`, which computes `500_000 / 10^6 = 0` (integer division floors to zero). [1](#0-0) 
4. `amount` is `0`; the pallet transfers/mints `0` to the beneficiary and still emits `TokenReceived { amount: 0, ... }` without reverting. [6](#0-5) 
5. Net result: the user's 500,000 wei of BridgeToken were burned on the EVM chain and 0 BRIDGE was credited on nexus — a total, unrecoverable loss of the transferred value.

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

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-282)
```text
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
