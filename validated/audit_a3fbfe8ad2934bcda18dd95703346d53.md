### Title
Broken decimal-scaling math (`saturating_sub`) in `convert_to_erc20`/`convert_to_balance` allows unbacked minting or value destruction when a bridged asset's ERC20 decimals are lower than its local decimals - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
The `hyper-fungible-token` pallet scales token amounts between its local `Balance`/asset precision and the remote ERC20 contract's precision using `10 ** erc_decimals.saturating_sub(local_decimals)` (and the inverse) instead of computing the correct signed exponent for both directions. When a registered token has `erc_decimals < local_decimals` (a normal, expected configuration — e.g. a locally 18-decimal asset bridged to a 6-decimal ERC20 like USDC/USDT), `saturating_sub` collapses to `0`, so the scale factor becomes `1` and no scaling is applied at all in either direction. This is the same class of bug as the referenced report (`Bonding.sol` truncating/mis-scaling decimals around a bonding-curve graduation), but here it manifests as a critical unbacked-mint / fund-loss bug in the core token-bridge path, reachable by any ordinary bridge user.

### Finding Description
`convert_to_erc20` and `convert_to_balance` are defined as: [1](#0-0) 

Both use `erc_decimals.saturating_sub(local_decimals)` as the scaling exponent. This is correct only when `erc_decimals >= local_decimals` (as in the shipped `BridgeToken` example, 18 vs 12 decimals). When `erc_decimals < local_decimals`, `saturating_sub` returns `0`, so `10 ** 0 = 1` — no scaling is performed, even though the correct exponent should be `local_decimals - erc_decimals` applied by multiplication (not division) in that direction.

This function is used on both the outgoing (`send`) and incoming (`on_accept`/`on_timeout`) paths:

- Outgoing: `send()` computes `erc20_amount = convert_to_erc20(amount, erc_decimals, decimals)` and embeds this raw value directly as `message.amount` in the ISMP POST dispatched to the destination chain's `HyperFungibleToken` contract: [2](#0-1) 

- The destination EVM contract mints exactly `message.amount` raw ERC20 units to the beneficiary with no independent decimals reconciliation: [3](#0-2) 

- Incoming: `on_accept` calls `convert_to_balance(message.amount, erc_decimals, decimals)` to compute the local mint/transfer amount: [4](#0-3) 

If a token is registered where `erc_decimals < local_decimals` (fully plausible for any real-world pairing where the EVM-side representation uses fewer decimals than the local Substrate asset, e.g. local asset at 18 decimals bridged to a 6-decimal USDC-like ERC20), an ordinary user calling the permissionless `send()` extrinsic causes:
- `convert_to_erc20` to skip scaling entirely (factor `1` instead of multiplying by `10^(local_decimals - erc_decimals)`), so the raw local balance value is passed straight through as the ERC20 mint amount, which is then interpreted at the *ERC20's own (lower) decimal precision*. Because the raw integer is unchanged but the implied decimal point moves, the destination contract mints an amount inflated by `10^(local_decimals - erc_decimals)` relative to what was escrowed/burned locally — an unbacked mint.
- Symmetrically, `convert_to_balance` on the reverse leg (EVM → Substrate, or the `on_timeout` refund path) would under-credit users by the same factor, permanently destroying value since the source side already burned/escrowed the full amount.

Neither `register_token`/`Precisions` storage nor `convert_to_balance`/`convert_to_erc20` validate the direction (`erc_decimals >= local_decimals`) before applying `saturating_sub`, so there is no on-chain guard preventing this misconfiguration from being exploited once such a token is registered.

### Impact Explanation
This breaks the fungible-token bridge's core invariant that minted supply must be backed by locked/burned supply on the source chain. Depending on direction it results in:
- **Unbacked minting**: a user can send a small amount of a local asset and cause the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract to mint an amount inflated by `10^(local_decimals - erc_decimals)`, printing tokens with no backing.
- **Permanent value destruction**: on the opposite conversion (`convert_to_balance` in `on_accept`/`on_timeout`), user funds are under-credited by the same factor and the difference is irrecoverably lost, since the source chain already escrowed/burned the full amount.

Both outcomes are direct, permanent loss-of-peg / loss-of-funds conditions in the token bridge, reachable from a single unprivileged extrinsic (`send`) or a single relayed message delivery (`on_accept`/`on_timeout`), matching the allowed "token bridge mint/burn" impact category.

### Likelihood Explanation
The trigger condition (`erc_decimals < local_decimals`) is not an edge case requiring malicious governance — it is a realistic and likely configuration for any asset whose local Substrate representation uses more decimal places than its ERC20 counterpart (a very common real-world pattern, e.g. 18-decimal local asset vs 6-decimal ERC20 stablecoins). Once such a token is registered via `register_token`, every ordinary user's `send()` call and every relayed delivery is affected — no attacker privilege beyond being a normal bridge user is required.

### Recommendation
Fix the scaling helpers to correctly handle both directions instead of relying on `saturating_sub`, e.g.:
```rust
pub fn convert_to_balance<B: core::str::FromStr>(value: U256, erc_decimals: u8, local_decimals: u8) -> Result<B, B::Err> {
    let scaled = if erc_decimals >= local_decimals {
        value / U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        value * U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    };
    scaled.to_string().parse::<B>()
}

pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
    if erc_decimals >= local_decimals {
        U256::from(value) * U256::from(10u128.pow((erc_decimals - local_decimals) as u32))
    } else {
        U256::from(value) / U256::from(10u128.pow((local_decimals - erc_decimals) as u32))
    }
}
```
Additionally, add regression tests covering `erc_decimals < local_decimals` configurations for `send`, `on_accept`, and `on_timeout`, and consider validating decimal-scale sanity at `register_token` time.

### Proof of Concept
1. Register a local asset `X` with `local_decimals = 18` (e.g. via `Assets` pallet metadata) and set `Precisions::<T>::insert(X, dest_chain, 6)` (simulating a 6-decimal ERC20 counterpart, e.g. USDC-like).
2. Map `TokenContracts`/`ContractToAsset` for `X` on `dest_chain` to a deployed `HyperFungibleToken` contract.
3. A user calls `send(SendParams { asset_id: X, amount: 1_000_000_000_000_000_000 /* 1 token, 18 decimals */, destination: dest_chain, ... })`.
4. Inside `send()`, `convert_to_erc20(1e18, erc_decimals=6, local_decimals=18)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so `erc20_amount = 1e18` is embedded verbatim as `message.amount`.
5. On `dest_chain`, `HyperFungibleTokenUpgradeable.onAccept` calls `_mint(beneficiary, 1e18)` — but at 6-decimal precision, `1e18` raw units represents `1,000,000,000,000` tokens (10^12 units) rather than the intended `1` token, minting far more value than was ever escrowed on the source chain. [2](#0-1) [3](#0-2)

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-310)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

			let token_message = Message {
				from: sender.to_vec().into(),
				to: params.recipient.to_vec().into(),
				amount: alloy_primitives::U256::from_be_bytes(erc20_amount.to_big_endian()),
				data: params.call_data.unwrap_or_default().into(),
			};

			let dispatch_post = DispatchPost {
				dest: params.destination,
				from: PALLET_ID.to_bytes(),
				to: token_contract,
				timeout: params.timeout,
				body: Message::abi_encode(&token_message),
			};
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-330)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

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
