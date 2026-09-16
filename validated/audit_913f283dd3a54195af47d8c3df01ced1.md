# Analog Found

### Title
Incoming HyperFungibleToken transfers below the decimals-scaling floor round down to zero, silently destroying user funds - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`pallet-hyper-fungible-token` converts an incoming ERC20-encoded `U256` amount to the pallet's local balance type using integer division by a fixed decimals-scaling factor. Because this is a floor division with no minimum-amount guard, any transfer whose value is smaller than the scaling factor truncates to exactly zero, causing the recipient (or the escrow release path) to receive nothing while the equivalent value was already burned/locked on the source chain — the same "amount below the precision floor becomes worthless" bug class as the referenced fractional-vault finding.

### Finding Description
`convert_to_balance` performs a straight floor-division scale-down: [1](#0-0) 

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

There is no check that `value >= 10^(erc_decimals - local_decimals)` before dividing, and no revert path for a resulting zero. The scaling factor is exactly the kind of value the H-11 report warns about: when it is large relative to typical transfer sizes, values below it are annihilated by truncation rather than rejected or rounded fairly.

This is concretely instantiated by `BridgeToken`, the canonical HyperFungibleToken deployment for the native BRIDGE asset: the EVM side always uses 18 decimals while nexus uses 12, a fixed 10^6 scaling factor baked into every deployment: [2](#0-1) 

Any incoming message whose ERC20-encoded amount is less than 10^6 (i.e., less than 0.000001 of a token in 18-decimal terms) converts to a local balance of `0` via `convert_to_balance`, even though the corresponding value was already burned/escrowed on the EVM side by `HyperFungibleToken.send` before dispatch: [3](#0-2) 

Symmetric arbitrary chains can register far larger decimal disparities (e.g. an 18-decimal ERC20 registered against a pallet asset with far fewer decimals via `Precisions`), which only widens the truncation floor: [4](#0-3) 

### Impact Explanation
Any relayed cross-chain transfer whose destination-side converted amount floors to zero results in permanent, silent loss of the transferred value: the sender's EVM-side tokens are already burned (or the nexus pallet's escrow custody already debited) before the message is processed on the receiving side, and the receiving side either mints/credits/releases `0` or errors depending on how the zero balance is subsequently handled. Either way the user's principal disappears — a direct instance of concrete theft/permanent loss of funds via a token-bridge mint/burn path, satisfying the "unbacked mint / permanent freezing of funds" acceptance bar. Because `BridgeToken` is the canonical BRIDGE deployment used everywhere BRIDGE crosses EVM↔nexus, and 18↔12 decimals is fixed in its bytecode, this is not a theoretical edge case restricted to obscure custom asset registrations — it is present in the flagship token bridge.

### Likelihood Explanation
Reachable by any unprivileged user/relayer: a user only needs to initiate a `send` (or the equivalent `bridge()` SDK call) for a sub-10^6-wei amount, or a relayer needs to deliver a message whose body encodes such an amount (dust, rounding remainders from fee calculations, or programmatic senders that don't defensively floor their own amounts). No special privileges, governance, or malicious actors are required — a legitimate small-value transfer, or fee-remainder dust generated elsewhere in the system (e.g., partial-fill remainders, gas-cost dust), can trigger it. The condition is deterministic (any value < scaling factor), making it trivially and repeatedly triggerable.

### Recommendation
- In `convert_to_balance`, reject (return an error) rather than silently truncate when the resulting local balance would be zero for a non-zero input `value`.
- Alternatively/additionally, enforce a minimum transferable amount at the `send`/dispatch entry points (both `HyperFungibleToken.send` on EVM and the pallet's `send` extrinsic) equal to `10^(erc_decimals - local_decimals)`, so a user cannot construct a transfer that the destination side will floor to nothing.
- Audit all other call sites of `convert_to_balance`/decimals-scaling divisions in the bridge/token-governor code for the same floor-to-zero pattern.

### Proof of Concept
1. A user calls `HyperFungibleToken.send` (or `BridgeToken.send`) on the EVM chain with `amount = 500_000` wei (i.e., `0.0000005` BRIDGE, less than 10^6, the fixed EVM(18)→nexus(12) scaling factor).
2. `_burn(msg.sender, params.amount)` burns the tokens on EVM and dispatches a POST request carrying `amount = 500_000` (U256) to nexus's `pallet-hyper-fungible-token`. [5](#0-4) 
3. On delivery, nexus decodes the message and calls `convert_to_balance(500_000, 18, 12)`, computing `500_000 / 10^6 = 0` (integer division floors to zero). [6](#0-5) 
4. The pallet credits/releases `0` BRIDGE to the recipient/escrow, while the sender's EVM balance was already reduced by 500,000 wei's worth of value — funds are permanently lost with no revert or refund path triggered by the zero-amount conversion.

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

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L145-155)
```rust
	/// EVM decimals per (AssetId, StateMachine) for precision conversion
	#[pallet::storage]
	pub type Precisions<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		AssetId<T>,
		Blake2_128Concat,
		StateMachine,
		u8,
		OptionQuery,
	>;
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L257-296)
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L293-311)
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
