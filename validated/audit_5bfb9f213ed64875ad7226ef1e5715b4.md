### Title
Asymmetric decimal-conversion in `pallet-hyper-fungible-token` allows unbacked minting on the EVM leg when a token's Substrate decimals exceed its registered EVM decimals - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
`convert_to_erc20`/`convert_to_balance` in `pallet-hyper-fungible-token` scale cross-chain amounts using `erc_decimals.saturating_sub(local_decimals)`. This is only correct when the EVM side has *more or equal* decimals than the local Substrate asset. When the local asset has *more* decimals than the registered EVM contract decimals, `saturating_sub` clamps to `0`, silently skipping the scale-down that should occur on `send()`, and skipping the scale-up that should occur on `on_accept()`. The `send()` direction is the exploitable one: an ordinary user can escrow/burn a small local amount and have the ISMP message carry an amount many orders of magnitude larger than what was actually taken from them, which the destination `HyperFungibleToken`/`WrappedHyperFungibleToken` contract on EVM will mint or unlock in full.

### Finding Description
`convert_to_erc20` and `convert_to_balance` are defined as: [1](#0-0) 

Both use `erc_decimals.saturating_sub(local_decimals)` as the scaling exponent. This expression is only valid in the direction `erc_decimals >= local_decimals` (the case documented and tested for `BridgeToken`, where EVM decimals=18 > nexus native decimals=12): [2](#0-1) 

In `send()`, the pallet escrows/burns `params.amount` in local decimals, then computes the outgoing ISMP message amount via `convert_to_erc20(amount, erc_decimals, decimals)`: [3](#0-2) 

If the registered `Precisions` entry for a given `(asset_id, destination)` records an EVM decimal count *smaller* than the local asset's decimals (e.g. a Substrate asset minted with 18 decimals mapped to a 6-decimal EVM token, a very plausible configuration), `erc_decimals.saturating_sub(decimals)` evaluates to `0` instead of the correctly signed negative exponent that should divide the amount down. The result: `erc20_amount = amount` (unscaled), i.e. the dispatched `Message.amount` is `10^(local_decimals - erc_decimals)` times larger than it should be.

On the receiving EVM contract, the amount is minted/unlocked verbatim with no independent decimal check: [4](#0-3) [5](#0-4) 

So a user burning/escrowing a small local amount receives a hugely inflated mint (`HyperFungibleToken`, unbacked new supply) or unlock (`WrappedHyperFungibleToken`, draining the escrow pool of underlying tokens locked by other users) on the destination chain — this is reachable from the permissionless, signed `send` extrinsic: [6](#0-5) 

The reverse direction (`on_accept`, inbound mint to Substrate) has the same bug but produces under-minting instead (a loss for the user, not an attacker-favorable outcome), since `saturating_sub` again clamps to `0` and skips the needed scale-up: [7](#0-6) 

### Impact Explanation
This is a direct token-bridge mint/burn integrity bug reachable by a single unprivileged signed transaction (`send`), analogous to the Oraichain "unauthorized minting via a flaw in the EVM cross-chain transfer path" bug class. Depending on the custody model of the asset registered for the affected chain pair:
- Against a `HyperFungibleToken` (burn/mint) destination: unbacked mint of the ERC20 token — arbitrary unbacked token creation.
- Against a `WrappedHyperFungibleToken` (lock/unlock) destination: the escrowed underlying-token pool can be drained beyond what was ever locked, causing insolvency/fund loss for all other bridge users of that asset.

The precondition is that `register_token`/`update_token` (governance, `CreateOrigin`) has registered a `Precisions` value where the EVM-side decimals are lower than the local asset's decimals — a realistic and likely configuration for many real-world tokens (e.g., 18-decimal Substrate asset paired with a 6-decimal EVM stablecoin representation).

### Likelihood Explanation
Likelihood is high wherever such an asset/chain pairing exists, since the trigger is a routine `send()` call with no special permissions, no forged proofs, and no relayer collusion required — the ISMP dispatch/delivery path itself is fully honest; the bug is a pure integer-arithmetic/decimals mismatch in the pallet's amount conversion helpers. It does, however, depend on a governance-controlled `Precisions` configuration decision (asymmetric decimals), so it is a latent bug rather than universally triggerable for every registered token — this is the main source of uncertainty, since I could not find the concrete registration used in production (that would require deployment/config data outside the indexed code).

### Recommendation
Replace `saturating_sub`-based single-direction scaling with a signed comparison that multiplies when `erc_decimals > local_decimals` and divides when `local_decimals > erc_decimals` (and vice versa in `convert_to_balance`), or use a `checked_sub`/explicit `Ordering` match and return an error for degenerate cases instead of silently defaulting to no scaling. Add symmetric unit/integration tests for both directions of decimal disparity (`erc_decimals < local_decimals` and `erc_decimals > local_decimals`) on both `send` and `on_accept`/`on_timeout` paths, mirroring the existing tests such as `should_send_asset_correctly`/`should_receive_asset_correctly`.

### Proof of Concept
1. Governance registers a non-native asset `X` with `local_decimals = 18` and configures `Precisions::<T>::insert(X, StateMachine::Evm(dest), 6)` (EVM contract for `X` uses 6 decimals), via `register_token`.
2. A user calls `HyperFungibleToken::send` with `amount = 1_000_000_000_000_000_000` (1 token in 18-decimal units); this burns exactly `1` token locally via `Assets::burn_from`.
3. `erc_decimals.saturating_sub(decimals)` = `6u8.saturating_sub(18u8)` = `0`, so `convert_to_erc20` returns `erc20_amount = amount` unscaled = `1_000_000_000_000_000_000` (1e18) instead of the correctly scaled `1_000_000` (1e6).
4. The dispatched `Message.amount` field carries `1e18` to the destination `HyperFungibleToken` contract, whose `onAccept` (`sdk/packages/core/contracts/apps/HyperFungibleToken.sol:292-305`) mints `1e18` raw ERC20 units directly to the beneficiary — 1,000,000,000,000× more than the single token burned on the source chain. [1](#0-0)

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

**File:** evm/src/apps/BridgeToken.sol (L30-36)
```text
 *
 * Metadata and the nexus peer are fixed in the bytecode rather than passed at deployment, so every
 * chain gets an identical token, and with CREATE2 an identical address for the same deployer and salt.
 *
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L241-256)
```rust
		pub fn send(
			origin: OriginFor<T>,
			params: SendParams<
				AssetId<T>,
				<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
			>,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let dispatcher = <T as Config>::Dispatcher::default();

			let token_contract =
				TokenContracts::<T>::get(params.destination, params.asset_id.clone())
					.ok_or(Error::<T>::TokenContractNotFound)?;
			let erc_decimals = Precisions::<T>::get(params.asset_id.clone(), params.destination)
				.ok_or(Error::<T>::DecimalsNotFound)?;

```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-302)
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
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-305)
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L302-324)
```text
        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
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
