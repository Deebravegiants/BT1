Looking at `send()` in `modules/pallets/hyper-fungible-token/src/lib.rs:241-325`, the `TokenSent` event is emitted with `amount: params.amount` — the **local denomination** value [1](#0-0) . But the value that actually contributes to the dispatched request's body (and therefore the commitment hash) is `erc20_amount`, computed via `convert_to_erc20(amount, erc_decimals, decimals)` and packed into `token_message.amount` [2](#0-1) . These two values differ whenever `erc_decimals != decimals` (which is guaranteed unequal for the native asset when `T::Decimals` — 12 for BRIDGE per the docs — differs from the registered EVM `decimals` — 18 per `BridgeToken.sol`) [3](#0-2) .

This mirrors the reported bug class exactly: the emitted event amount is in one denomination (local, e.g. 12-decimal BRIDGE units) while the value that was actually hashed/committed into the dispatched ISMP request body (and thus what a relayer/watcher must reconstruct to verify the request/commitment) is in a different denomination (18-decimal ERC20 units). Any off-chain component — indexer, relayer, or auditor — that reconstructs the request commitment or verifies delivered amounts using `TokenSent.amount` directly (rather than re-deriving `erc20_amount` via the same `Precisions` lookup and `convert_to_erc20`) will compute a mismatched/incorrect amount, exactly as described for the `savETHGateway`/`ERC20Gateway` inconsistency in the report.

On the receiving side, `on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs:50-117` decodes `message.amount` (ERC20/18-decimal units) from the request body and converts it back to local balance via `convert_to_balance` before minting/transferring, then emits `TokenReceived{ amount }` in local denomination [4](#0-3) [5](#0-4) . So `TokenSent` (source, local units) and `TokenReceived` (destination, local units) are each internally consistent with the minted/transferred amounts on their own chain, but neither directly matches the units actually embedded in the cross-chain message/commitment (`erc20_amount`, ERC20/18-decimal units). This is the same unit-mismatch class as the audit finding: the event value and the hashed/committed value are denominated differently, requiring an extra conversion step (using `Precisions` + `convert_to_erc20`/`convert_to_balance`) for anyone attesting to or verifying the commitment purely from event logs.

### Title
Inconsistent Units Between `TokenSent` Event and Committed Message Amount - (File: modules/pallets/hyper-fungible-token/src/lib.rs)

### Summary
`Pallet::send` emits `TokenSent.amount` in local asset denomination while the ISMP request body that is hashed into the dispatch commitment carries `erc20_amount`, scaled to the destination chain's registered ERC20 decimals via `convert_to_erc20`. These two values diverge whenever `erc_decimals != local decimals` (the common case, e.g. BRIDGE: 12 decimals locally vs 18 on EVM).

### Finding Description
In `send()`, `params.amount` (local denomination) is transferred/burned, then converted to `erc20_amount = convert_to_erc20(amount, erc_decimals, decimals)` and packed as `token_message.amount` inside the ABI-encoded `Message` body used to build `DispatchPost` [2](#0-1) . This body is what is hashed into the request commitment returned by `dispatcher.dispatch_request` [6](#0-5) . Immediately after, `TokenSent` is emitted using `params.amount` — the un-scaled, local-denomination value, not `erc20_amount` [1](#0-0) . Any consumer relying on the event to reconstruct or validate the request/commitment (indexers, off-chain attestors, or the SDK) will compute a value that is off by `10^(erc_decimals - decimals)` unless it separately re-fetches `Precisions` and reapplies `convert_to_erc20`.

### Impact Explanation
This is a data-integrity/consistency issue rather than a direct fund-theft bug in the pallet's own accounting (mint/burn amounts are computed independently in `on_accept`/`on_timeout` from the message body, not from the event). However, per the same bug class as the referenced report, it can mislead any off-chain component (attestors, watchers, the indexer/SDK) that uses `TokenSent.amount` as a stand-in for the committed message amount when verifying deliveries, computing RPC/attestation hashes, or reconciling volumes — potentially causing incorrect verification, false alerts, or acceptance of a mismatched proof if such logic assumes event amount == committed amount.

### Likelihood Explanation
High likelihood of being hit in practice: decimal mismatch between local and EVM precisions is the pallet's designed default state (explicitly documented for the `BridgeToken` case, 12 vs 18 decimals), so every native `send()` call to an EVM chain emits an event amount that differs from the committed message amount.

### Recommendation
Emit `erc20_amount` (or both the local and ERC20-scaled amounts) in `TokenSent`, consistent with the amount actually embedded in the dispatched request body, so that downstream consumers can reconstruct the commitment/message content directly from the event without needing a separate `Precisions` lookup and manual conversion.

### Proof of Concept
1. Register a native asset with `T::Decimals = 12` and `Precisions::<T>::insert(asset_id, dest_chain, 18)` (as done for BRIDGE/`BridgeToken.sol`).
2. Call `send(origin, SendParams { asset_id: native, amount: 1_000000000000 /* 1 unit at 12 decimals */, destination: dest_chain, .. })`.
3. Observe `TokenSent.amount == 1_000000000000` while the dispatched `Message.amount` (and therefore the value hashed in the commitment) equals `1_000000000000 * 10^6 = 1_000000000000000000` (18-decimal ERC20 units) [7](#0-6) .
4. Any off-chain verifier reading `TokenSent.amount` and assuming it equals the committed message amount will be off by a factor of `10^6`.

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L312-315)
```rust
			let metadata = FeeMetadata { payer: who.clone(), fee: params.relayer_fee.into() };
			let commitment = dispatcher
				.dispatch_request(DispatchRequest::Post(dispatch_post), metadata)
				.map_err(|_| Error::<T>::DispatchError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L317-323)
```rust
			Self::deposit_event(Event::<T>::TokenSent {
				from: who,
				to: params.recipient,
				dest: params.destination,
				amount: params.amount,
				commitment,
			});
```

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L205-209)
```rust
		Self::deposit_event(Event::<T>::TokenReceived {
			beneficiary,
			amount: amount.into(),
			source,
		});
```
