### Title
Message delivery status is derived from unfiltered transaction logs, allowing a malicious destination module to forge `PostRequestHandled`/`GetRequestHandled` events and cause permanent non-delivery of unrelated messages - (File: tesseract/messaging/evm/src/tx.rs)

### Summary
When a relayer submits a batch of ISMP messages to an EVM destination, it determines which individual messages were actually "handled" by scanning **all logs in the transaction receipt** for `PostRequestHandled`/`GetRequestHandled` event signatures, without verifying that the log was emitted by the `EvmHost` contract itself. Because the receipt log list is a flat, contract-agnostic list of every log emitted anywhere in the call tree (including inside the destination module's own callback), any attacker-controlled destination module invoked in the same transaction can emit a spoofed log matching the event's ABI signature and an arbitrary commitment value, causing the relayer to believe an unrelated message was successfully delivered.

### Finding Description
`extract_event_commitments` collects commitments purely by ABI-decoding every log in the receipt against the `PostRequestHandled`/`GetRequestHandled` event shape — it never checks `log.address` against the actual `EvmHost` address: [1](#0-0) 

This is called from `wait_for_success`, gated only on the *overall* transaction status (`Eip658Value::Eip658(true)`), not on whether the specific message's dispatch to its destination module actually succeeded — and, critically, not on the emitting address: [2](#0-1) 

The resulting commitment set feeds `submit_messages`/`build_tx_receipts`, which marks any message whose (real, correctly-computed) commitment happens to appear in this attacker-influenced set as delivered, removing it from the retry/unsuccessful queue: [3](#0-2) [4](#0-3) 

The same class of bug exists in the TRON path, where `extract_commitment_hashes` scans `info.log` for the same topics without checking `log_entry.address`: [5](#0-4) 

A related, compounding instance exists in the pre-submission gas-estimation/simulation path: `any_frame_has_event` walks the entire `debug_traceCall` call tree and accepts a matching log from *any* frame/address, and does not exclude frames flagged with `frame.error` (a revert) before scanning their `logs`: [6](#0-5) 

The Phoenix SDK issue this analog is drawn from is a failure to check whether the enclosing execution context (the outer transaction/instruction) actually succeeded before trusting nested logs/instructions as authoritative events. Here, the root cause is structurally identical but broader: the code trusts *any* log in the receipt/trace that matches an event signature, without pinning it to the contract (`EvmHost`) that is the sole legitimate emitter, and (in the trace path) without excluding reverted call frames.

### Impact Explanation
Dispatching a `PostRequest`/`GetRequest` to an arbitrary destination module address is fully permissionless — any user can deploy a malicious contract and target it as the module `to`. When a relayer batches deliveries (`handlePostRequests`/`handleGetResponses`) that include a call into this malicious module, its `onAccept`/`onGetResponse` callback can emit a log with the exact topic/ABI shape of `PostRequestHandled(bytes32,address)` (or `GetRequestHandled`), carrying an **arbitrary commitment** chosen to match an unrelated, real, pending message. Because the relayer treats any matching log in the receipt as proof of delivery regardless of its emitting address, the relayer will incorrectly conclude the unrelated message was delivered and drop it from its retry/unsuccessful set — permanently starving that message of delivery attempts. This is a "route unable to deliver messages" condition reachable by any unprivileged message dispatcher, and can also pollute the outbound-delivery-claim bookkeeping with fabricated commitments (`build_tx_receipts`), even though the eventual on-chain reward claim would still require matching `RequestReceipts[commitment]` on the destination host.

### Likelihood Explanation
No privileged access is required: an attacker only needs to (1) deploy a contract as an ISMP module and dispatch a request to it (or otherwise get relayed) and (2) have it emit a crafted log during its callback. The relayer processes deliveries in batches, so getting the malicious module's callback included in the same transaction as a target message's delivery is realistically achievable by an attacker who controls dispatch timing/fees, making this a medium-to-high likelihood issue given the low barrier to entry (permissionless module deployment/dispatch) that any relayer, gateway user, or intent participant can trigger.

### Recommendation
When extracting `PostRequestHandled`/`GetRequestHandled` (and the TRON equivalent) commitments from a transaction receipt or trace, filter logs by `log.address == host_addr` (the actual `EvmHost`/handler contract address) before decoding, exactly analogous to filtering `program_id` in the Phoenix SDK fix. In the `debug_traceCall`-based simulation path (`any_frame_has_event`), additionally skip any call frame (and its descendants) whose `error`/revert_reason is set before scanning its logs, since geth's callTracer can retain logs from reverted sub-calls.

### Proof of Concept
1. Deploy `MaliciousModule` implementing `IIsmpModule.onAccept` to emit `emit PostRequestHandled(targetCommitment, address(this))` (or the `GetRequestHandled` equivalent) unconditionally, where `targetCommitment` is the precomputed commitment of a real, unrelated post request `X` sent by a victim to a legitimate module.
2. Dispatch a harmless `PostRequest` to `MaliciousModule` as its own `to` module.
3. Wait for (or induce) a relayer to batch-deliver both `X` and the attacker's own request in the same `handlePostRequests` transaction (or submit the attacker's request such that it lands in the same relaying cycle).
4. Observe `extract_event_commitments` (`tesseract/messaging/evm/src/tx.rs:110-124`) picks up the spoofed log for `X`'s commitment regardless of it originating from `MaliciousModule` rather than `EvmHost`.
5. Confirm `X` is subsequently treated as delivered by the relayer (removed from retry/unsuccessful tracking in `build_tx_receipts`) even though `EvmHost.dispatchIncoming` never actually processed `X`, leaving `X` permanently undelivered on-chain.

### Citations

**File:** tesseract/messaging/evm/src/tx.rs (L110-124)
```rust
fn extract_event_commitments(receipt: &TransactionReceipt) -> BTreeSet<H256> {
	receipt
		.inner
		.logs()
		.iter()
		.filter_map(|log| {
			if let Ok(ev) = PostRequestHandled::decode_log(&log.inner) {
				return Some(H256::from_slice(ev.commitment.as_slice()));
			}
			GetRequestHandled::decode_log(&log.inner)
				.map(|ev| H256::from_slice(ev.commitment.as_slice()))
				.ok()
		})
		.collect()
}
```

**File:** tesseract/messaging/evm/src/tx.rs (L614-639)
```rust
		let tx_hash = H256::from_slice(pending.tx_hash().as_slice());

		let (evs, epochs) = match wait_for_success(client, tx_hash).await? {
			Some(evs) => evs,
			None => {
				cancel_transaction(client, from, nonce, gas_price, tx_hash).await;
				return Err(anyhow!("Transaction to {:?} was cancelled", client.state_machine));
			},
		};

		if matches!(messages[idx], Message::Request(_) | Message::Response(_)) && evs.is_empty() {
			unsuccessful.push(messages[idx].clone());
		}
		events.extend(evs);
		new_epochs.extend(epochs);
	}

	if !events.is_empty() {
		tracing::trace!(
			target: crate::LOG_TARGET, chain = ?client.state_machine,
			"Got {} receipts",
			events.len(),
		);
	}

	Ok((events, unsuccessful, new_epochs))
```

**File:** tesseract/messaging/evm/src/tx.rs (L653-675)
```rust
#[tracing::instrument(skip(client), fields(chain = ?client.state_machine, ?tx_hash))]
pub async fn wait_for_success(
	client: &EvmClient,
	tx_hash: H256,
) -> anyhow::Result<Option<(BTreeSet<H256>, Vec<NewEpochEvent>)>> {
	match wait_for_transaction_receipt(tx_hash, client).await? {
		Some(receipt) =>
			if receipt.inner.status_or_post_state() == Eip658Value::Eip658(true) {
				tracing::info!(target: crate::LOG_TARGET, "Tx for {:?} succeeded", client.state_machine);
				let commitments = extract_event_commitments(&receipt);
				let new_epochs = extract_new_epochs_for_self(&receipt, &client.address);
				Ok(Some((commitments, new_epochs)))
			} else {
				tracing::info!(
					target: crate::LOG_TARGET, "Tx {:?} for {:?} reverted",
					receipt.transaction_hash,
					client.state_machine
				);
				Err(anyhow!("Transaction reverted"))
			},
		None => Ok(None),
	}
}
```

**File:** tesseract/messaging/evm/src/tx.rs (L682-716)
```rust
fn build_tx_receipts(
	receipts: BTreeSet<H256>,
	unsuccessful: Vec<Message>,
	messages: Vec<Message>,
	height: u64,
	new_epochs: Vec<NewEpochEvent>,
) -> TxResult {
	let mut results = vec![];
	for msg in messages {
		match msg {
			Message::Request(req_msg) =>
				for post in req_msg.requests {
					let req = Request::Post(post);
					let commitment = hash_request::<Hasher>(&req);
					if receipts.contains(&commitment) {
						results.push(TxReceipt {
							query: Query {
								source_chain: req.source_chain(),
								dest_chain: req.dest_chain(),
								nonce: req.nonce(),
								commitment,
							},
							height,
						});
					}
				},
			// `Message::Response` deliveries are excluded on purpose: `EvmHost.dispatchIncoming`
			// pays the relayer the origin GetRequest's fee inline, on this chain, in feeToken.
			// There is nothing to accumulate or claim on Hyperbridge, so emitting a receipt
			// here would enqueue a claim for a fee that was already settled.
			_ => {},
		}
	}
	TxResult { receipts: results, unsuccessful, new_epochs }
}
```

**File:** tesseract/messaging/tron/src/tx.rs (L365-436)
```rust
fn extract_commitment_hashes(info: &TransactionInfo) -> BTreeSet<H256> {
	log::trace!(
		target: crate::LOG_TARGET, "extract_commitment_hashes: processing {} log entries for tx {}",
		info.log.len(),
		info.id
	);

	let request_topic = H256::from(keccak_256(b"PostRequestHandled(bytes32,address)"));
	let response_topic = H256::from(keccak_256(b"PostResponseHandled(bytes32,address)"));

	log::trace!(target: crate::LOG_TARGET, "Looking for request_topic: {:?}", request_topic);
	log::trace!(target: crate::LOG_TARGET, "Looking for response_topic: {:?}", response_topic);

	let mut hashes = BTreeSet::new();

	for (idx, log_entry) in info.log.iter().enumerate() {
		log::trace!(target: crate::LOG_TARGET, "Processing log entry {} with {} topics", idx, log_entry.topics.len());

		if log_entry.topics.is_empty() {
			log::trace!(target: crate::LOG_TARGET, "Log entry {} has no topics, skipping", idx);
			continue;
		}

		// topics[0] is the event signature hash.
		let topic0 = match hex::decode(&log_entry.topics[0]) {
			Ok(bytes) if bytes.len() == 32 => {
				let h = H256::from_slice(&bytes);
				log::trace!(target: crate::LOG_TARGET, "Log entry {} topic0: {:?}", idx, h);
				h
			},
			Ok(bytes) => {
				log::trace!(target: crate::LOG_TARGET, "Log entry {} topic0 has wrong length: {}", idx, bytes.len());
				continue;
			},
			Err(e) => {
				log::trace!(target: crate::LOG_TARGET, "Log entry {} topic0 hex decode failed: {}", idx, e);
				continue;
			},
		};

		if topic0 != request_topic && topic0 != response_topic {
			log::trace!(target: crate::LOG_TARGET, "Log entry {} topic0 doesn't match request/response topics", idx);
			continue;
		}

		log::trace!(
			target: crate::LOG_TARGET, "Log entry {} matches {} event",
			idx,
			if topic0 == request_topic { "PostRequestHandled" } else { "PostResponseHandled" }
		);

		// topics[1] is the indexed `commitment` parameter.
		if log_entry.topics.len() >= 2 {
			if let Ok(bytes) = hex::decode(&log_entry.topics[1]) {
				if bytes.len() == 32 {
					let commitment = H256::from_slice(&bytes);
					log::trace!(target: crate::LOG_TARGET, "Extracted commitment: {:?}", commitment);
					hashes.insert(commitment);
				} else {
					log::trace!(target: crate::LOG_TARGET, "Log entry {} topic1 has wrong length: {}", idx, bytes.len());
				}
			} else {
				log::trace!(target: crate::LOG_TARGET, "Log entry {} topic1 hex decode failed", idx);
			}
		} else {
			log::trace!(target: crate::LOG_TARGET, "Log entry {} doesn't have topic1", idx);
		}
	}

	log::trace!(target: crate::LOG_TARGET, "extract_commitment_hashes: extracted {} commitments", hashes.len());
	hashes
}
```

**File:** tesseract/messaging/evm/src/provider.rs (L828-860)
```rust
fn any_frame_has_event(
	frame: &alloy::rpc::types::trace::geth::CallFrame,
	event_in: &CheckTraceForEventParams,
) -> bool {
	use alloy::primitives::LogData;

	if let Some(ref error) = frame.error {
		log::error!(target: crate::LOG_TARGET, "Error in call frame {:?}: {error}", frame.to);
	}

	for log in &frame.logs {
		let topics = log.topics.clone().unwrap_or_default();
		let data = log.data.clone().unwrap_or_default();
		let Some(log_data) = LogData::new(topics, data) else { continue };
		let prim_log =
			alloy::primitives::Log { address: log.address.unwrap_or_default(), data: log_data };
		let matched = match event_in {
			CheckTraceForEventParams::Request => PostRequestHandled::decode_log(&prim_log).is_ok(),
			CheckTraceForEventParams::Response => GetRequestHandled::decode_log(&prim_log).is_ok(),
		};
		if matched {
			return true;
		}
	}

	for child in &frame.calls {
		if any_frame_has_event(child, event_in) {
			return true;
		}
	}

	false
}
```
