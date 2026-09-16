Confirmed: `Precisions` is read fresh (mutable, live storage) at delivery time in both `on_accept` and `on_timeout`, while the EVM-side counterpart (`HyperFungibleToken.sol` `send()`) embeds `params.amount` completely unscaled into the ISMP message. This is the structural analog to the ECO bridge finding.

### Title
Cross-chain amount decoded with the precision configured at delivery time instead of the precision in effect when the message was dispatched, allowing token loss/inflation on `update_token`/`register_token` changes - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` and `on_timeout` handlers convert the raw ERC20-denominated `message.amount` embedded in an ISMP request into local balance units using `Precisions::<T>::get(local_asset_id, source)` — the value **currently** stored for that `(asset, chain)` pair at the moment the message is delivered/timed-out, not the value that was in effect when the corresponding EVM contract emitted the message. Because the EVM side (`HyperFungibleToken.sol`) performs no decimal scaling at all (it just embeds the caller-supplied `params.amount` verbatim), the entire correctness of the cross-chain amount depends on `Precisions` staying constant between dispatch and delivery. If `CreateOrigin` calls `update_token` (or a fresh `register_token`) to change the recorded EVM decimals for that asset/chain pair while messages are still in flight (during the ISMP finality/relay window), those in-flight messages will be minted/unlocked using the wrong scale factor.

### Finding Description
In `send()` (`modules/pallets/hyper-fungible-token/src/lib.rs:237-325`), the pallet correctly snapshots `erc_decimals` from `Precisions` at dispatch time and bakes the already-scaled `erc20_amount` into the message body: [1](#0-0) [2](#0-1) 

However, the reverse direction is asymmetric. `HyperFungibleToken.sol`'s `send()` does not perform any decimal conversion — it burns and embeds `params.amount` directly: [3](#0-2) 

The substrate `on_accept` handler then re-derives the scale factor **at delivery time** by reading live `Precisions` storage, not a value captured when the EVM message was created: [4](#0-3) 

The same pattern repeats in `on_timeout` for refunds: [5](#0-4) 

`Precisions` is fully mutable after initial registration — `update_token` overwrites it per-chain at any time with no check against messages currently in flight: [6](#0-5) 

This is structurally identical to the reported ECO bug: a value used to scale a cross-chain amount (`inflationMultiplier` there, `Precisions`/EVM-decimals here) is read fresh at finalization time instead of being fixed at the time the transfer was initiated, so any change to that value while a message is in flight (ISMP finality + relay delay, which can span minutes to hours depending on the source/destination consensus) causes the delivered amount to be computed with a mismatched scale factor.

### Impact Explanation
If `Precisions` for `(asset_id, chain)` is corrected/updated (e.g., fixing an initial misconfiguration, or the same `local_id` now recording a different remote-chain decimals value) while a `Send` message from that EVM chain is still awaiting finality/relay, `on_accept`/`on_timeout` will scale `message.amount` by the new decimals value instead of the one the EVM contract used implicitly (its own fixed token decimals). If the new precision is lower than the old, users receive a vastly inflated (over-minted) amount, an unbacked-mint/insolvency risk for the pallet's custody account for native assets. If the new precision is higher, users receive far less than they sent, a fund-loss for the bridging user, identical to the ECO report's "user loses part of their tokens" outcome. Both directions correspond to Medium/High severity per the standard: unsound state conversion leading to incorrect minting or fund loss during normal bridge operation, not requiring a malicious admin — merely a routine precision correction performed while transfers are in flight.

### Likelihood Explanation
`update_token` is a normal maintenance/config-correction call (analogous to `rebase()` in the original report, which is also a routine, non-malicious call anyone could trigger). ISMP request delivery is not instantaneous — it requires consensus proof finalization on the source chain plus relayer submission, giving a real window (which can be substantial for some supported consensus clients) during which in-flight `Send` messages exist. Any legitimate reconfiguration of asset precision during that window — which the pallet provides no mechanism to prevent or checkpoint against — miscalculates every message dispatched-but-undelivered at the time of the change.

### Recommendation
Do not rely on live mutable `Precisions` storage to interpret amounts embedded in already-dispatched messages. Either:
1. Embed the source-chain decimals value used at send time directly in the message body (as is already done for the substrate→EVM direction via `convert_to_erc20`), so the receiving side has no ambiguity, or
2. Version `Precisions` and include the version/decimals value that was active at dispatch time in the message, validating it against history on delivery, or
3. Disallow decimals/precision updates for a chain while there are known undelivered requests to that chain (e.g., track outstanding commitments per chain and reject `update_token` until they clear or have timed out).

### Proof of Concept
1. Asset `X` is registered as non-native with `Precisions::<T>::insert(X, EVM_CHAIN, 18)` (18 decimals on the EVM chain) via `register_token`.
2. A user calls `send()` on the EVM `HyperFungibleToken.sol` deployment with `amount = 100e18` (its token uses 18 decimals). The contract burns `100e18` and embeds `message.amount = 100e18` verbatim: [7](#0-6) 
3. Before the ISMP request finalizes and is relayed to the substrate chain, `CreateOrigin` dispatches `update_token` for asset `X`/`EVM_CHAIN`, correcting the recorded EVM decimals to `6` (e.g., because the actual token deployment used 6 decimals and was mis-registered), updating `Precisions::<T>::insert(X, EVM_CHAIN, 6)`: [8](#0-7) 
4. The relayer delivers the already-in-flight request. `on_accept` reads the now-updated `erc_decimals = 6` and calls `convert_to_balance(100e18, 6, local_decimals)`: [9](#0-8) 
   With `erc_decimals(6) < local_decimals` the `saturating_sub` clamps to `0`, so the division factor is `10^0 = 1` — the beneficiary is minted `100e18` raw local-denomination units instead of the intended (scaled-down) amount, an over-mint of many orders of magnitude relative to what the pallet's other asset holders/backing expect. Conversely, if precision had instead been corrected upward (e.g., 18 → 30), the divisor would be `10^12`, and the beneficiary would receive `100e18 / 10^12`, a near-total loss of the transferred value.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L251-255)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L384-421)
```rust
		pub fn update_token(
			origin: OriginFor<T>,
			update: TokenUpdate<AssetId<T>>,
		) -> DispatchResult {
			T::CreateOrigin::ensure_origin(origin)?;

			let local_decimals = if update.asset_id == T::NativeAssetId::get() {
				T::Decimals::get()
			} else {
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					update.asset_id.clone(),
				)
			};

			for (chain, config) in update.add_chains {
				// This pallet bridges substrate <-> EVM only; reject non-EVM peers.
				if !matches!(chain, StateMachine::Evm(_)) {
					return Err(Error::<T>::NonEvmPeerChain.into());
				}
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
				// Remove old reverse mapping if it exists
				if let Some(old_contract) = TokenContracts::<T>::get(chain, update.asset_id.clone())
				{
					ContractToAsset::<T>::remove(chain, old_contract);
				}

				let token_contract = config.token_contract.0.to_vec();
				TokenContracts::<T>::insert(
					chain,
					update.asset_id.clone(),
					token_contract.clone(),
				);
				ContractToAsset::<T>::insert(chain, token_contract, update.asset_id.clone());
				Precisions::<T>::insert(update.asset_id.clone(), chain, config.decimals);
			}
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-255)
```rust
				let decimals = if local_asset_id == T::NativeAssetId::get() {
					T::Decimals::get()
				} else {
					<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
						local_asset_id.clone(),
					)
				};
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
