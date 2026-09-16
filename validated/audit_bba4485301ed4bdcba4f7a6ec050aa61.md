### Title
Malicious/invalid inbound message in a relayer-submitted batch causes the entire batch (including unrelated legitimate messages) to be rejected on delivery - ([File: modules/pallets/ismp/src/impls.rs])

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic and the EVM handler's atomic `batchCall` path both process multiple independent ISMP messages together and fail the **entire** batch if any single message is invalid. Because the Tesseract relayer batches all deliverable messages headed to a destination at a given height into one submission, an attacker can craft one poisoned/invalid message and have it bundled — by the relayer's normal batching logic — alongside unrelated legitimate messages, causing the whole delivery attempt to be rejected. This mirrors the ZetaChain finding's root cause: one malformed inbound item silently blocks processing of other, unrelated, legitimate items grouped in the same unit of work.

### Finding Description
`Pallet::execute` builds the message batch result with a short-circuiting `collect`: [1](#0-0) 

If `handle_incoming_message` returns `Err` for *any* message in the `Vec<Message>` (invalid proof, duplicate commitment, decode failure, module-level revert surfaced as an error, etc.), `execute()` returns `Err(Error::<T>::InvalidMessage)` before any of the batch's events are deposited or fees charged — even though other messages in the same batch were individually valid. This is intentional/documented behavior: [2](#0-1) [3](#0-2) 

On the EVM side, the relayer submits multiple messages atomically via `IHandlerV2.batchCall` whenever the batch has ≥2 messages: [4](#0-3) 

The relayer constructs these batches by grouping **all** deliverable messages destined for a chain at a given consensus height into a single call, prefixed with the consensus update: [5](#0-4) 

Because `IsmpDispatcher::dispatch_request` is a permissionless entry point reachable by any application/user on a source chain, an attacker can dispatch a `PostRequest` whose `body` is crafted to make the destination module's `onAccept` revert (e.g. an `abi.decode` failure), similar to `HyperFungibleToken.onAccept`, which performs an unguarded decode with no try/catch: [6](#0-5) 

Note that other apps (e.g. `HyperbridgeLzEndpoint`) explicitly wrap the risky external call in `try/catch` specifically to avoid reverting the whole `onAccept`, underscoring that this is a known-necessary defensive pattern that isn't uniformly applied: [7](#0-6) 

Since the relayer's batching groups this poisoned request together with unrelated legitimate requests destined for the same chain/height, the atomic `batchCall` reverts entirely, and on Substrate destinations the equivalent `handle_unsigned` extrinsic fails entirely due to the short-circuiting `collect` in `execute()` — in both cases none of the bundled legitimate messages are delivered in that attempt, exactly analogous to the ZetaChain report where one malformed inbound message blocked the delivery of all other events processed together.

### Impact Explanation
An attacker who can call `dispatch` on any ISMP-enabled application (a normal, unprivileged action) can repeatedly inject a single poison request that gets swept into the relayer's shared per-destination-height batch. Every submission attempt containing that poisoned message reverts atomically, so legitimate cross-chain requests/responses batched alongside it are never delivered, and (depending on how the relayer's retry logic reconstitutes batches) can be repeatedly re-poisoned on retry, indefinitely delaying delivery of otherwise-valid messages to a destination chain. This is a message-delivery liveness/DoS issue reachable by any unprivileged dispatcher — matching the required class of "a route unable to deliver messages."

### Likelihood Explanation
Likelihood is high for the root cause (atomic batch semantics are used deliberately, per the pallet's own documentation, and the relayer's outbound path batches independently-sourced messages together by design). What is **not verified** from available code is the exact downstream retry behavior — i.e., whether `tesseract/messaging/messaging/src/retries.rs` filters out a previously-failing message before re-batching it with fresh legitimate messages, which would bound the blast radius, or whether it keeps re-including it, which would make the DoS persistent. This uncertainty should be confirmed by a deeper review of `retries.rs`/`batch_requests` and of the on-chain `IHandlerV2.batchCall` semantics (its exact Solidity source was not available in the indexed context).

### Recommendation
- Make batch execution partially fault-tolerant: in `pallet_ismp::Pallet::execute`, process each message independently (e.g. via `filter_map`/per-item try-catch equivalent) and only reject/charge-fee for the messages that actually fail, instead of short-circuiting the whole `Vec<Message>` on the first error.
- On EVM destinations, ensure `IHandlerV2.batchCall` either isolates per-message failures (e.g. via low-level `call`/`try/catch` per message with only the failing message rolled back) or ensure the relayer never groups an unverified/first-seen message from an unrelated application with a large set of legitimate messages without a fallback to per-message submission when the batch fails.
- Ensure every `onAccept` implementation (including `HyperFungibleToken`) wraps risky decode/dispatch logic in `try/catch`, following the pattern already used in `HyperbridgeLzEndpoint`, so a single malformed payload cannot revert the enclosing atomic delivery call.
- In the relayer, on an atomic batch failure, fall back to per-message (or bisected) submission so that only the actually-failing message is isolated and legitimate messages are retried without being permanently entangled with the poison message.

### Proof of Concept
1. An attacker calls `dispatch` (or any permissionless `IsmpDispatcher::dispatch_request` equivalent) on a source chain, targeting an application (e.g. a token adapter) with a `body` deliberately malformed so the destination's `onAccept` will revert on `abi.decode` (as in `HyperFungibleToken.onAccept`, which has no try/catch).
2. Legitimate users independently dispatch normal, valid PostRequests to the same destination chain in the same block window.
3. The relayer's outbound pipeline (`tesseract/messaging/messaging/src/outbound.rs`) collects all deliverable messages for that destination/height — including both the attacker's poisoned request and the legitimate ones — into a single batch.
4. `handle_message_submission` submits this batch atomically via `IHandlerV2.batchCall` (EVM) or as a single `handle_unsigned` extrinsic (Substrate, via `pallet_ismp::Pallet::execute`'s short-circuiting `collect`).
5. The poisoned message's `onAccept`/`handle_incoming_message` failure causes the entire batch to revert/fail, so none of the legitimate messages in that batch are delivered, and they must be resubmitted — repeatable by the attacker at will by continuing to dispatch new poisoned requests.

### Citations

**File:** modules/pallets/ismp/src/impls.rs (L40-51)
```rust
	pub fn execute(messages: Vec<Message>) -> Result<Vec<events::Event>, Error<T>> {
		let host = Pallet::<T>::default();

		let message_results = messages
			.iter()
			.map(|msg| handle_incoming_message(&host, msg.clone()))
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;
```

**File:** modules/pallets/ismp/src/lib.rs (L358-382)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
		///
		/// Emits different message events based on the Message received if successful.
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L249-253)
```text
| Call | Origin | Description |
|------|--------|-------------|
| `create_consensus_client` | AdminOrigin | Initialize the consensus state of a consensus client. Consensus clients must be initialized with a trusted state, so this call must only be called by a trusted party. |
| `update_consensus_state` | AdminOrigin | Update the unbonding period or challenge_period for a consensus client. It must only be called by trusted parties to prevent consensus exploits. |
| `handle_unsigned` | Unsigned | Execute the provided batch of ISMP messages for free with valid proofs. This will short-circuit and revert if any of the provided messages are invalid. |
```

**File:** tesseract/messaging/evm/src/tx.rs (L718-743)
```rust
/// Top-level submission entry.
///
/// - **Batch of 1** (e.g. the mandatory-consensus-only chunks from the outbound rotation catch-up)
///   routes through the legacy per-message [`submit_messages`] path. Wrapping a single call in
///   `IHandlerV2.batchCall` adds a self-delegatecall frame with no upside, costs extra gas, and
///   makes the receipt harder to interpret downstream.
/// - **Batch of ≥2** dispatches through [`submit_batch_messages`], the atomic
///   `IHandlerV2.batchCall` path. Chains whose handler doesn't implement `IHandlerV2` will revert
///   at the handler address — the legacy serial-submit fallback is no longer supported for real
///   batches.
pub async fn handle_message_submission(
	client: &EvmClient,
	messages: Vec<Message>,
) -> anyhow::Result<TxResult> {
	if messages.is_empty() {
		return Ok(TxResult::default());
	}

	let (receipts, unsuccessful, new_epochs) = if messages.len() == 1 {
		submit_messages(client, messages.clone()).await?
	} else {
		submit_batch_messages(client, messages.clone()).await?
	};
	let height = client.client.get_block_number().await?;
	Ok(build_tx_receipts(receipts, unsuccessful, messages, height, new_epochs))
}
```

**File:** tesseract/messaging/messaging/src/outbound.rs (L392-428)
```rust
	let mut batch: Vec<Message> = vec![consensus_msg.clone()];

	if has_events_for_dest {
		let state_machine_height =
			StateMachineHeight { id: hb_state_machine_id, height: new_height };

		match translate_events_to_messages(
			hyperbridge.clone(),
			dest.clone(),
			events,
			state_machine_height,
			relayer_config.clone(),
			coprocessor,
			&client_map,
			// Pass the consensus update as the gas-estimation prelude so EVM
			// sinks simulate each message inside `batchCall([consensus, msg])`
			// — matching the real on-chain dispatch order.
			Some(consensus_msg),
		)
		.await
		{
			Ok((deliverable, unprofitable)) => {
				park_undelivered(
					&dest_name,
					dest_state_machine,
					&relayer_config,
					unprofitable,
					&claim_tx_payment,
				)
				.await;
				batch.extend(deliverable);
			},
			Err(err) => {
				tracing::error!(target: LOG_TARGET, ?err, dest = %dest_name, "translate_events_to_messages failed")
			},
		}
	}
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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L384-396)
```text
        // Deliver to the OApp. Isolate the external call so a deterministic revert (zero
        // recipient, over-cap mint, blocklisted recipient, malformed payload, paused OApp, etc.)
        // does not revert `onAccept`. On failure the payload is retained for later retry/recovery
        // via retryPayload/clear/skip/nilify/burn.
        Origin memory origin = Origin({srcEid: srcEid, sender: sender, nonce: nonce});
        try ILayerZeroReceiver(receiverAddr).lzReceive(origin, guid, message, address(0), "") {
            // delivered successfully
        } catch {
            bytes32 payloadHash = keccak256(abi.encode(guid, message));
            _inboundPayloadHashes[receiverAddr][srcEid][sender][nonce] = payloadHash;
            emit InboundPayloadStored(receiverAddr, srcEid, sender, nonce, payloadHash);
        }
    }
```
