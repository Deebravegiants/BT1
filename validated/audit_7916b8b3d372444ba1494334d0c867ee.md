### Title
Decimal-truncation on inbound token-bridge transfers can silently zero out credited amounts, permanently losing the burned/escrowed EVM-side tokens - (File: modules/pallets/hyper-fungible-token/src/impls.rs, modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` converts an inbound ERC20-denominated amount to the local asset's balance by dividing by `10^(erc_decimals - local_decimals)` via `convert_to_balance`. Registration (`register_token`/`update_token`) only enforces `erc_decimals >= local_decimals`, which can leave an arbitrarily large decimal gap (e.g. local asset decimals = 0/2, EVM decimals = 18). Any inbound message whose ERC20 amount is smaller than that divisor truncates to a locally-credited amount of `0`, yet the corresponding tokens were already burned/escrowed on the EVM side by the `HyperFungibleToken`/`WrappedHyperFungibleToken` contract before the message was dispatched. `on_accept` performs no minimum-amount check and proceeds to call `transfer`/`mint_into` with `amount == 0`, which succeeds silently instead of reverting or crediting dust — so the sender's real value is permanently lost with no refund path (the `on_timeout` refund only fires for expired outbound `send`s, not for a delivered-but-truncated inbound message).

### Finding Description
`convert_to_balance` in [1](#0-0)  computes:

```rust
let dec_str = (value / U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))).to_string();
```

`register_token` and `update_token` only guarantee `config.decimals (erc_decimals) >= local_decimals`, as seen in [2](#0-1)  and [3](#0-2) . This does not bound how large `erc_decimals - local_decimals` can be — a chain operator can register a low-decimal local asset (e.g. 0, 2, 6 decimals) against an 18-decimal EVM token, yielding a divisor of up to `10^18` or more.

`on_accept`, invoked for every inbound `Send` message from the paired EVM contract, computes the credited amount this way with no floor/minimum check before minting or transferring: [4](#0-3) . If the ERC20 `message.amount` is below the divisor, `amount` resolves to `0`, and the subsequent `NativeCurrency::transfer`/`Assets::transfer`/`Assets::mint_into` call with `amount = 0` completes without error — no revert, no event indicating failure, and no way for the beneficiary to reclaim value.

Critically, by the time this message is processed, the EVM-side contract has already burned (non-native) or escrowed (native) the sender's tokens on the source chain before dispatching the cross-chain `Send` message — this is the documented escrow/burn model in the pallet's README: [5](#0-4) . So the value has already left the sender's control on the EVM side, but the local mint/credit is silently zero. `on_timeout` only refunds if the *outbound* request the pallet itself dispatched later times out ( [6](#0-5) ); it does not apply to inbound messages that were delivered but truncated to zero.

### Impact Explanation
This is a permanent loss of user funds: an end user who transfers a small amount of a bridged token from the EVM side to Substrate receives nothing while their tokens are already burned/escrowed on the EVM chain. Because token metadata (decimals) is often small integers for non-EVM-native assets (e.g., stablecoins with 6, or custom assets with fewer/no decimals) while ERC20 tokens conventionally use 18, this decimal gap is a realistic, easily-triggered configuration rather than an edge case, and it requires no privileged action — any ordinary bridge user sending a routine "small" transfer relative to the gap can be affected. This satisfies the "permanent freezing/loss of funds" bar.

### Likelihood Explanation
Likelihood is high in practice for any token pair registered with a meaningful decimal gap (which the pallet explicitly supports and even documents, "Decimals between this chain and each remote chain may differ"). Any transaction whose ERC20-denominated amount is smaller than `10^(erc_decimals - local_decimals)` — e.g., sending under `1e12` wei of an 18-decimal token against a 6-decimal local asset — triggers the truncation. No attacker coordination is needed; ordinary usage of the bridge with small transfer amounts on a token pair with a nontrivial decimal gap reproduces this deterministically.

### Recommendation
- In `convert_to_balance`, reject (return an error) rather than silently truncate when the computed local `amount` would be `0` for a nonzero `value`, so `on_accept` can either refuse to process the message (leaving it to be retried/handled) or explicitly document dust loss.
- Alternatively/additionally, at `register_token`/`update_token`, bound the allowed decimal gap (e.g., require `erc_decimals - local_decimals <= N`) or require the local asset to carry sufficient decimals to represent the smallest meaningful ERC20 unit, preventing this configuration entirely.
- Consider surfacing a `TokenReceived` variant or dedicated event/error for zero-credit deliveries so operators and users can detect and account for truncation, rather than it passing invisibly.

### Proof of Concept
1. Register a non-native asset via `register_token` with `local_id` decimals = `2` and `chains[EVM].decimals = 18` (passes the `config.decimals (18) >= local_decimals (2)` check in [2](#0-1) ).
2. On the EVM side, a user calls the paired `HyperFungibleToken`/`WrappedHyperFungibleToken` contract's send function with `amount = 999_999_999_999_999` wei (i.e., `< 1e16`, the divisor `10^(18-2)=10^16`). The EVM contract burns/locks this amount and dispatches a `Send` message.
3. The relayer delivers the message; `pallet-hyper-fungible-token::on_accept` runs `convert_to_balance(value=999999999999999, erc_decimals=18, local_decimals=2)`, computing `value / 10^16 = 0`.
4. `mint_into`/`transfer` is called with `amount = 0`, succeeding without error; the beneficiary's local balance is unchanged, while the sender's tokens remain burned/locked on the EVM chain with no recovery path. [1](#0-0) [4](#0-3)

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L352-355)
```rust
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L403-406)
```rust
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-101)
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
```

**File:** modules/pallets/hyper-fungible-token/README.md (L20-26)
```markdown
- **Native** (`native = true`) — the asset originates on this chain. Outgoing
  transfers move the local balance into the pallet's escrow account; incoming
  messages release from escrow.
- **Non-native** (`native = false`) — the asset originates on a remote chain.
  Outgoing transfers burn the local representation; incoming messages mint
  fresh tokens.

```

**File:** modules/pallets/hyper-fungible-token/README.md (L83-89)
```markdown
- `on_accept` — receives `Send` messages from the paired EVM contract. Maps
  the source contract back to a local asset via `ContractToAsset`, scales the
  amount using `Precisions`, then mints (non-native) or releases from escrow
  (native) to the beneficiary. Emits `TokenReceived`.
- `on_timeout` — refunds the original sender's balance from escrow or by
  re-minting. Emits `TokenRefunded`.
- `on_response` — unused; this pallet uses post-only messaging.
```
