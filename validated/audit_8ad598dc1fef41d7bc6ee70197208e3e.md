## Finding: Missing bidirectional decimal scaling in `pallet-hyper-fungible-token` allows unbacked cross-chain mint

Investigation of `modules/pallets/hyper-fungible-token/src/impls.rs` uncovered a decimal-conversion bug functionally equivalent to the Paid Network "infinite mint": a single unprivileged `send` extrinsic can cause the destination chain to credit orders of magnitude more tokens than were locked/burned on the source chain, because the ERC20 ⇄ local-balance conversion helpers only handle one direction of the decimal mismatch.

### Title
Unidirectional decimal-scaling bug in `convert_to_erc20`/`convert_to_balance` lets any sender mint unbacked tokens cross-chain - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s `send` extrinsic and its `on_accept`/`on_timeout` ISMP handlers rescale amounts between the local asset's decimals and the registered remote ERC20/ERC6160 decimals (`Precisions` storage) using `convert_to_erc20` and `convert_to_balance`. Both functions assume `erc_decimals >= local_decimals` and compute the scale factor as `10^(erc_decimals.saturating_sub(local_decimals))`. When an asset is registered where the remote chain's token has *fewer* decimals than the local asset (a legitimate, supported configuration per the pallet's own documentation, e.g. an 8-decimal WBTC-style or 6-decimal USDC-style remote token against an 18-decimal local asset), `saturating_sub` clamps to `0`, so the multiplier becomes `10^0 = 1` and **no down-scaling is applied**. The raw local amount is forwarded unchanged as the "ERC20 amount," inflating the credited value by `10^(local_decimals - erc_decimals)`.

### Finding Description [1](#0-0) 

`convert_to_balance` (incoming) divides by `10^(erc_decimals.saturating_sub(local_decimals))` and `convert_to_erc20` (outgoing) multiplies by the same clamped exponent. Both doc comments explicitly state the "divide/multiply to scale from ERC20 precision" assumption, i.e. they assume `erc_decimals >= local_decimals` always holds. There is no `assert`/`ensure!`/error path if this assumption is violated — the code just proceeds with a scale factor of `1`.

`send` uses `convert_to_erc20` to compute the outgoing message amount: [2](#0-1) 

`on_accept` uses `convert_to_balance` to compute the local credit amount from an incoming message: [3](#0-2) 

`on_timeout` (refund path) repeats the identical conversion: [4](#0-3) 

The pallet's own documentation confirms `Precisions` is meant to support arbitrary per-chain decimal configurations (e.g. comparing 10-decimal DOT on Polkadot to 18-decimal DOT on Ethereum), meaning the "remote decimals < local decimals" case is an expected, legitimately reachable configuration, not a governance error: [5](#0-4) 

Given such a registration (e.g. local asset with 18 decimals bridged to a genuine 6- or 8-decimal ERC20/ERC6160 on the EVM side — a normal token-listing scenario, not malicious governance), any signed account can call `send` with a small local amount. The pallet correctly burns/escrows the small local amount, but `convert_to_erc20` forwards the *raw* (unscaled) amount as the message's ERC20 `amount`, which is `10^(local_decimals - erc_decimals)` times larger than the correct converted value. When this message is delivered to `HyperFungibleToken.onAccept` on the EVM side, it mints/unlocks that inflated amount to the attacker's beneficiary address: [6](#0-5) 

Because the EVM-side contract has no independent sanity check on amount magnitude (it trusts the pallet-originated message body once source/from validation passes), the destination chain unconditionally mints the inflated amount — exactly analogous to Paid Network's infinite-mint exploit where an unchecked mint path let an attacker create tokens far exceeding backing collateral.

### Impact Explanation
This is a critical, direct loss-of-funds bug: a single unprivileged `send` transaction from any account can create unbacked tokens on the destination EVM chain (or vice versa, under-credit on the return leg, causing the same effect for anyone triggering the reverse flow). The attacker only burns/locks a tiny real amount locally but receives `10^(local_decimals - erc_decimals)` times more on the destination chain, which is then freely transferable/sellable — draining the backing/escrow relationship the bridge relies on, precisely the "unbacked mint" class called out in scope.

### Likelihood Explanation
The trigger condition (an asset registered where remote decimals are fewer than local decimals) is a normal, documented, and even encouraged configuration for real-world tokens with non-18 decimals (WBTC, USDC-style assets, etc.), not a misconfiguration or malicious governance action. Once such an asset is registered, exploitation requires only one ordinary signed `send` extrinsic — no privileged role, no consensus forgery, no relayer collusion.

### Recommendation
Fix `convert_to_balance` and `convert_to_erc20` in `modules/pallets/hyper-fungible-token/src/impls.rs` to handle both directions of the decimal difference: multiply when the target has more decimals than the source, and divide when it has fewer, instead of relying on `saturating_sub` (which silently clamps the exponent to zero and produces an unscaled/incorrect result). Add explicit tests covering `local_decimals > erc_decimals` for both `send`/`on_accept` and the timeout/refund path.

### Proof of Concept
1. Register an asset via `register_token` with `local` decimals = 18 and `chains[EVM].decimals` = 6 (a realistic configuration for a USDC-style remote ERC20).
2. Any signed account calls `send` with `amount = 1_000_000_000_000_000_000` (1 whole token, 18 decimals). The pallet burns/escrows exactly this amount locally (correct).
3. `convert_to_erc20(1e18, erc_decimals=6, local_decimals=18)` computes `10u128.pow(6u8.saturating_sub(18) as u32) = 10^0 = 1`, so `erc20_amount = 1e18` is dispatched unchanged in the outgoing `Message`.
4. On the EVM side, `HyperFungibleToken.onAccept` mints `1e18` raw units to the beneficiary. Since the token there is 6-decimal, `1e18` raw units represents `1,000,000,000,000` (1 trillion) whole tokens — a `10^12`x amplification from a single legitimate 1-token transfer, fully analogous to the Paid Network infinite-mint drain.

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-296)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-91)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L246-255)
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
```

**File:** modules/pallets/hyper-fungible-token/README.md (L30-32)
```markdown
Decimals between this chain and each remote chain may differ; per-pair
`Precisions` storage records the EVM-side decimals so amounts get scaled at
the boundary.
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
