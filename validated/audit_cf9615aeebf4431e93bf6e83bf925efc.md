### Title
Primary outbound delivery path lacks a stale-timeout re-check before atomic batch submission, causing whole-batch reverts and delivery delay - ([File: tesseract/messaging/messaging/src/events.rs])

### Summary
The primary outbound relaying path (`translate_events_to_messages`) filters out timed-out `PostRequest`s using a single up-front timestamp check, then builds proofs, estimates gas, and submits the whole batch as one atomic on-chain call. Because the destination's `HandlerV2.handlePostRequests` / `pallet-ismp::handle_unsigned` revert the *entire* batch if even one request has crossed its timeout by execution time, a request that was valid at check-time but expires during the network round-trips before inclusion causes the whole multi-message, multi-application batch — including the bundled consensus update — to revert and be delayed, exactly the check-then-act TOCTOU pattern described in the Notional report.

### Finding Description
`translate_events_to_messages` performs exactly one liveness check per request, against `counterparty_timestamp` captured before any proof-fetching or gas-estimation work begins: [1](#0-0) 

After this check, the outbound task in `outbound.rs` assembles the consensus proof plus every deliverable request into one `batch: Vec<Message>` and submits it in a single transaction: [2](#0-1) 

For EVM destinations that batch is dispatched via `submit_batch_messages`, which performs several more network round-trips (fetch gas price, `estimate_gas`, fetch nonce, submit, and possibly retry on rate limiting) between the up-front timeout check and actual on-chain execution: [3](#0-2) 

On-chain, `HandlerV2.batchCall` is fully atomic — a failure anywhere in the batch reverts everything: [4](#0-3) 

and `handlePostRequests` reverts the whole call the instant any single leaf in the batch has crossed its timeout, with no mechanism to skip just that leaf and proceed with the rest: [5](#0-4) 

The Substrate side has the identical structural weakness: `pallet_ismp::handle_unsigned` is `#[frame_support::transactional]` and calls `Self::execute(messages)` for the whole `Vec<Message>` batch: [6](#0-5) 

and the core request handler performs its timeout check in an up-front loop over *all* requests in the message before dispatching *any* of them, aborting the entire message on the first timed-out entry: [7](#0-6) 

Notably, the retry path (`retries.rs`) already recognizes and mitigates this exact class of bug by re-querying `deliverable_requests` (timeout + receipt) immediately before regrouping and submitting, explicitly noting "one past its timeout is never accepted again... [it] reverts on delivery": [8](#0-7) 

but the **primary** delivery path (`events.rs` → `outbound.rs`) performs no equivalent re-check immediately before the final submission, leaving the same TOCTOU window the Notional report describes: a request valid at check time can expire during the subsequent proof/gas-estimation/mempool-inclusion delay, causing the atomic batch (which can bundle the consensus proof and many unrelated, still-valid requests to potentially many different destination applications) to revert as a whole.

### Impact Explanation
When this occurs, none of the batched messages are delivered — not just the stale one. Because the outbound batch bundles the BEEFY/consensus proof update together with application messages (`outbound.rs` lines 387-392), a revert can also delay the destination's view of Hyperbridge consensus, compounding the delay for every other message destined for that chain until the next successful submission cycle. Under bursty/volatile traffic where requests are batched near their timeout boundary, this can repeatedly occur, systematically delaying message delivery — a route temporarily unable to deliver messages, matching the accepted "route unable to deliver messages" impact class. It does not cause loss of funds directly, but repeated reverts degrade delivery reliability and consensus propagation for a destination chain.

### Likelihood Explanation
Likelihood is proportional to how close requests are batched to their `timeout_timestamp` and how much latency exists between the up-front check (`events.rs`) and the on-chain execution (gas estimation, nonce fetch, mempool wait, rate-limit retries seen in `tx.rs`). Requests with short timeouts or during network congestion are the most exposed; this is a naturally occurring condition, not one requiring an attacker, mirroring the "delayed rebalance" scenario in the source report which was judged valid at Medium severity for the same check-then-act class.

### Recommendation
Re-verify each request's liveness (and receipt/duplicate status) immediately before the final atomic submission in the primary outbound path, the same way `retries.rs::deliverable_requests` already does, and drop any request that has since timed out or been delivered from the outgoing batch rather than relying solely on the earlier, stale up-front filter in `translate_events_to_messages`. On the handler side, consider allowing `handlePostRequests`/`handle_unsigned` to skip an individual timed-out/duplicate entry rather than reverting the entire batch, so unrelated still-valid messages (and the bundled consensus update) are not held hostage by one stale entry.

### Proof of Concept
1. A relayer collects a batch of `PostRequest`s and passes the up-front timeout check in `translate_events_to_messages` (`events.rs:113-122`) because all are valid at that instant.
2. The relayer proceeds to fetch proofs, estimate gas, fetch nonce, and submit the batched `IHandlerV2.batchCall` (or `pallet_ismp::handle_unsigned`) — this takes non-trivial wall-clock time (network round-trips in `tx.rs:454-469`, plus mempool inclusion delay).
3. Before the transaction is mined, one of the bundled requests' `timeout_timestamp` elapses.
4. On execution, `handlePostRequests` hits `if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();` for that one leaf (`HandlerV2.sol:195`), and because `batchCall` is atomic, the *entire* transaction reverts — including the consensus update and every other still-valid request in the batch.
5. The relayer must detect the failure and resubmit, delaying delivery of all bundled (still valid) messages until the next cycle; if batching conditions recur, this can repeat.

### Citations

**File:** tesseract/messaging/messaging/src/events.rs (L97-122)
```rust
	let counterparty_timestamp = sink.query_timestamp().await?;

	// Fetch message proofs for estimating gas concurrently
	let batch_size = source.max_concurrent_queries();
	for chunk in events.chunks(batch_size) {
		let processes = chunk
			.into_iter()
			.map(|event| {
				let source = source.clone();
				let event = event.clone();
				let sink = sink.clone();
				let config = config.clone();
				async move {
					match event {
						IsmpEvent::PostRequest(post) => {
							// Skip timed out requests
							if post.timeout_timestamp != 0 &&
								post.timeout_timestamp <= counterparty_timestamp.as_secs()
							{
								tracing::trace!(
									target: crate::LOG_TARGET, "Found timed out request, request: {}, counterparty: {}",
									post.timeout_timestamp,
									counterparty_timestamp.as_secs()
								);
								return Ok::<_, anyhow::Error>(None);
							}
```

**File:** tesseract/messaging/messaging/src/outbound.rs (L387-463)
```rust
	let consensus_msg = Message::Consensus(ConsensusMessage {
		consensus_proof: proof_bytes,
		consensus_state_id: BEEFY_CONSENSUS_STATE_ID,
		signer: dest.address(),
	});
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

	// If translate returned no deliverable messages we may be left with only
	// the consensus entry — only worth sending on mandatory (rotation) proofs.
	if batch.len() == 1 && !is_mandatory {
		tracing::trace!(target: LOG_TARGET,dest = %dest_name, "skipping — consensus-only batch, not mandatory");
		// As above: catch-up rotations already landed on the dest carry
		// claim-eligible new_epochs; persist them before bailing out.
		forward_consensus_delivery_claims(
			&dest_name,
			dest_state_machine,
			catchup_new_epochs,
			&claim_tx_payment,
		)
		.await;
		return Ok(());
	}

	if batch.len() == 1 && is_mandatory {
		tracing::info!(target: "tesseract", msgs = batch.len(), "🛰️ Transmitting Mandatory Consensus Message to {dest_name}");
	} else {
		tracing::info!(target: "tesseract", msgs = batch.len(), "🛰️ Transmitting ismp messages to {dest_name}");
	}
	// Keep a copy of the request messages before submit consumes the batch:
	// the request-claim forwarder indexes them by commitment, and a submission
	// that never lands parks them for the retry task.
	let requests: Vec<Message> =
		batch.iter().filter(|msg| matches!(msg, Message::Request(_))).cloned().collect();
	let batch_requests: Vec<PostRequest> = requests
		.iter()
		.flat_map(|msg| match msg {
			Message::Request(req_msg) => req_msg.requests.clone(),
			_ => Vec::new(),
		})
		.collect();

```

**File:** tesseract/messaging/evm/src/tx.rs (L454-469)
```rust
	let handler_addr = Address::from_slice(&client.handler().await?.0);
	let from = Address::from_slice(&client.address);
	let gas_price = fetch_gas_price(client, false).await?;
	let chain_gas_limit = get_chain_gas_limit(client.state_machine);

	let inner_calls = build_batch_inner_calls(client, &messages).await?;
	let handler_v2 = HandlerV2Instance::new(handler_addr, client.signer.clone());
	let call = handler_v2.batchCall(inner_calls);
	let gas = call.estimate_gas().await.unwrap_or_else(|_| (chain_gas_limit * 8) / 10);
	let calldata = call.calldata().clone();
	let calldata_len = calldata.len();
	let tx_request =
		build_tx_request(from, handler_addr, calldata, gas_price, gas_with_buffer(gas));

	let nonce = client.signer.get_transaction_count(from).await?;
	let tx = tx_request.nonce(nonce).transaction_type(0);
```

**File:** evm/src/core/HandlerV2.sol (L129-135)
```text
    function batchCall(bytes[] memory calls) external {
        uint256 len = calls.length;
        for (uint256 i = 0; i < len; ++i) {
            (bool success, bytes memory returnData) = address(this).delegatecall(calls[i]);
            if (!success) revert BatchCallFailed(i, returnData);
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L190-197)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }
```

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
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

**File:** modules/ismp/core/src/handlers/request.rs (L55-65)
```rust
	for req in msg.requests.iter() {
		let req = Request::Post(req.clone());
		// If a receipt exists for any request then it's a duplicate and it is not dispatched
		if host.request_receipt(&req).is_some() {
			Err(Error::DuplicateRequest { meta: req.clone().into() })?
		}

		// can't dispatch timed out requests
		if req.timed_out(host.timestamp()) {
			Err(Error::RequestTimeout { meta: req.clone().into() })?
		}
```

**File:** tesseract/messaging/messaging/src/retries.rs (L245-277)
```rust
/// Requests that are still worth submitting.
///
/// A request the destination already has a receipt for was delivered by some
/// other submission, and one past its timeout is never accepted again. Both
/// revert on delivery, so neither is carried any further.
async fn deliverable_requests(
	dest: &Arc<dyn IsmpProvider>,
	requests: Vec<(PostRequest, u64)>,
) -> Result<Vec<(PostRequest, u64)>, anyhow::Error> {
	let timestamp = dest.query_timestamp().await?;
	let mut deliverable = vec![];

	for chunk in requests.chunks(dest.max_concurrent_queries()) {
		let checked = chunk
			.iter()
			.map(|(post, height)| async move {
				let request = Request::Post(post.clone());
				if request.timed_out(timestamp) {
					return Ok::<_, anyhow::Error>(None);
				}

				let receipt = dest.query_request_receipt(hash_request::<Hasher>(&request)).await?;
				Ok((!was_delivered(&receipt)).then(|| (post.clone(), *height)))
			})
			.collect::<FuturesOrdered<_>>()
			.collect::<Result<Vec<_>, _>>()
			.await?;

		deliverable.extend(checked.into_iter().flatten());
	}

	Ok(deliverable)
}
```
