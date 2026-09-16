### Title
Decimal-scaling `saturating_sub` in `convert_to_erc20` lets an ordinary `send()` mint far more `HyperFungibleToken` on the destination chain than was ever escrowed/burned on the source chain - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
The reported `CorePrimary.strategyMinting` bug is a case where a privileged role is trusted to mint an amount of token that isn't actually enforced to be 1:1 backed. The structurally analogous, unprivileged-reachable path in this codebase is `pallet-hyper-fungible-token`'s decimal conversion helper, `convert_to_erc20`, used by the `send` extrinsic (callable by any signed user) to compute the `amount` field of the cross-chain `Message` that the destination `HyperFungibleToken`/`BridgeToken` EVM contract will later `_mint` verbatim in `onAccept`.

### Finding Description
`convert_to_erc20` converts a local balance to the ERC20-denominated amount that gets embedded in the outgoing ISMP message body: [1](#0-0) 

```rust
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

The scaling exponent is computed as `erc_decimals.saturating_sub(local_decimals)`. This is only correct when `erc_decimals >= local_decimals` (the documented, illustrated case is DOT: 10 decimals locally vs. 18 decimals on the EVM peer, i.e. `erc_decimals > local_decimals`, which scales up correctly). When the reverse holds - a registered asset whose EVM-side `Precisions` entry has **fewer** decimals than the local asset (`erc_decimals < local_decimals`) - `saturating_sub` clamps the negative difference to `0`, so the multiplier degenerates to `10^0 = 1` instead of dividing the value down by `10^(local_decimals - erc_decimals)`. The dispatched `message.amount` therefore ends up `10^(local_decimals - erc_decimals)` times **larger** than the amount actually escrowed/burned locally.

The counterpart used on receive, `convert_to_balance`, has the exact same asymmetric flaw: [2](#0-1) 

The mismatched (inflated) `message.amount` is placed straight into the `HyperFungibleToken.Message` and dispatched via ISMP: [3](#0-2) 

On the destination EVM chain, `HyperFungibleToken.onAccept` trusts this `message.amount` completely and mints it without any further validation against the amount actually escrowed on the source chain — the only checks are on the *source contract address*, not on the *amount*: [4](#0-3) 

Because `register_token`/`update_asset_precision` (both `CreateOrigin`-gated) are the only calls that set `Precisions`, this is not a case of a compromised or malicious admin acting directly — it is a routine, documented configuration state (per-chain decimal precision differing per asset, explicitly called out in the pallet's own README: "Decimals between this chain and each remote chain may differ"). Once such an asset exists with `erc_decimals < local_decimals` for a given destination, **any unprivileged holder can call `send` (a `Signed` extrinsic)** to trigger the bug — no governance or admin action is needed at exploit time.

### Impact Explanation
Every ordinary `send()` call against an asset configured with `erc_decimals < local_decimals` for its destination chain causes the destination `HyperFungibleToken`/`BridgeToken` contract to mint `10^(local_decimals - erc_decimals)` times more tokens than were locked/burned on the source chain. This directly and permanently unbacks the bridged token's supply — the destination-chain token ceases to be redeemable 1:1 against the source-chain collateral, which is exactly the failure mode ("unbacked mint") the reference report flags as High severity. Repeated small transfers can drain arbitrarily large amounts of the wrapped asset on the destination chain relative to what is actually escrowed.

### Likelihood Explanation
The trigger requires only a legitimate, unprivileged `send()` call — no forged proofs, no compromised keys, no admin action at exploit time. The precondition (an asset registered with `erc_decimals < local_decimals` for some destination chain) is a normal, supported configuration explicitly acknowledged by the pallet's documentation (arbitrary per-chain decimal precision), not a contrived edge case, making this readily reachable once any such asset is onboarded.

### Recommendation
Fix `convert_to_erc20` and `convert_to_balance` in `modules/pallets/hyper-fungible-token/src/impls.rs` to handle both directions of the decimal difference correctly (i.e., divide when `local_decimals > erc_decimals`, multiply when `erc_decimals > local_decimals`), instead of relying on `saturating_sub`, which silently clamps negative exponents to zero. Add symmetric unit tests covering `erc_decimals < local_decimals` for both `send` and `on_accept`/timeout paths, and consider a runtime invariant/sanity check that a computed conversion never changes the represented value by more than the expected precision ratio.

### Proof of Concept
1. Governance (via `CreateOrigin`) registers a local asset with `local_decimals = 18` and, via `update_asset_precision`, sets its EVM-side `Precisions` entry for destination chain `D` to `erc_decimals = 6` (a legitimate configuration difference, e.g. mirroring a 6-decimal stablecoin representation on `D`).
2. Any unprivileged user calls `HyperFungibleToken::send` with `amount = 1` local unit (`1 * 10^18` in local base units), locking/escrowing that amount on the source chain.
3. `convert_to_erc20(value, erc_decimals=6, local_decimals=18)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so the multiplier is `10^0 = 1` — the dispatched `message.amount` equals the raw local value (`10^18`) instead of being scaled down to `10^6` (the correct 6-decimal representation).
4. The ISMP message with `amount = 10^18` (in `HyperFungibleToken.Message`) is delivered to the destination EVM chain; `HyperFungibleToken.onAccept` calls `_mint(beneficiary, 10^18)` — [5](#0-4) .
5. The beneficiary receives `10^18` units of a token meant to be minted at 6-decimal precision (i.e., `10^12` times its intended real-world value), while only `1` unit (in 18-decimal local terms) was ever escrowed on the source chain — an unbacked mint of `10^12`x the collateral.

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

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L54-59)
```rust
/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-91)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

		// Convert recipient bytes to substrate AccountId
		// If 32 bytes: use directly. If 20 bytes: left-pad with zeros.
		let mut beneficiary_bytes = [0u8; 32];
		let to_bytes = message.to.as_ref();
		if to_bytes.len() == 32 {
			beneficiary_bytes.copy_from_slice(to_bytes);
		} else if to_bytes.len() == 20 {
			beneficiary_bytes[12..].copy_from_slice(to_bytes);
		} else {
			Err(HftError::InvalidRecipientLength(to_bytes.len()))?;
		}
		let beneficiary: T::AccountId = beneficiary_bytes.into();

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```
