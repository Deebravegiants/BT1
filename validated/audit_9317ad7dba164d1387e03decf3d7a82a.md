### Title
Forged `PostRequestHandled`/`GetRequestHandled` events from a malicious destination module can trick the relayer into treating undelivered messages as delivered - (File: tesseract/messaging/evm/src/tx.rs)

### Summary
The relayer's `extract_event_commitments` helper decides whether a dispatched cross-chain message was actually delivered by scanning a transaction receipt's logs for `PostRequestHandled`/`GetRequestHandled` events, but it never checks that the log was emitted by the `EvmHost` contract itself. Any contract invoked as the destination module during delivery can emit a log with the identical event signature and an arbitrary `commitment`, causing the relayer to falsely mark an unrelated, still-undelivered request as handled and stop retrying it — a direct structural analog of the ZetaChain `ZetaReceived`/`ZetaReverted` spoofing bug (trusting decoded event data without verifying the emitting contract address).

### Finding Description
`extract_event_commitments` is explicitly documented as the *only* reliable signal for delivery success, precisely because `EvmHost.dispatchIncoming` swallows a reverting module callback instead of reverting the whole transaction: [1](#0-0) 

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

`decode_log` only validates the event's ABI signature (topic0) against the expected type — it does not check `log.address` against the `EvmHost` contract address. During `dispatchIncoming`, the host calls out to the destination module's `onAccept`/`onGetResponse` callback within the same transaction, and that callback's logs land in the same `receipt.logs()` array used here. The same class of bug was previously flagged for the sibling trace-based check `check_trace_for_event`/`any_frame_has_event`, whose comment even documents the exact reason a forged signal is dangerous (dispatchIncoming swallowing reverts), yet also decodes any log in the call tree without checking the emitting address: [2](#0-1) 

An attacker who controls the destination module contract (a normal, permissionless `to` address for a `PostRequest`, or the requester module for a `GetResponse`) can, inside its `onAccept`/`onGetResponse` callback, emit a fabricated `PostRequestHandled(bytes32 commitment, address relayer)` (or `GetRequestHandled`) event carrying the commitment of a **completely different, unrelated pending request** it does not control.

### Impact Explanation
Since `extract_event_commitments` is the relayer's sole mechanism for distinguishing "delivered" from "swallowed/reverted" deliveries in a batched submission, a forged event for a foreign commitment causes the relayer to believe that unrelated request was successfully delivered on-chain, when in reality the host's `_requestReceipts`/`_responseReceipts` for that commitment were never set. The relayer will then stop retrying/resubmitting that legitimate request. Because message delivery on Hyperbridge is retry-driven by off-chain relayers observing on-chain delivery state, this results in a message that can never be delivered — a permanent liveness failure ("a route unable to deliver messages") for the victim's cross-chain request, satisfying the required impact bar (forged message delivery / route unable to deliver messages) at effectively zero cost to the attacker (a single malicious destination contract deployment reachable by any user submitting a message through that module).

### Likelihood Explanation
The attack requires only deploying a malicious destination contract and having any user (or the attacker themselves) route a message to it as the `to` address of a `PostRequest`, or being the requester module of a `GetRequest`/`GetResponse` cycle — both are fully permissionless, single-transaction actions reachable by any unprivileged relayer/dispatcher on Hyperbridge. No governance, admin, or consensus-forging capability is required, making this a High-likelihood issue once a victim's request happens to be batched alongside the attacker's malicious delivery in the same submission the relayer observes.

### Recommendation
When decoding `PostRequestHandled`/`GetRequestHandled` (and similarly in `any_frame_has_event`/`check_trace_for_event`), verify `log.address()` (or the call frame's callee address) equals the known `EvmHost` contract address for the chain before trusting the decoded commitment. Reject or ignore any log/frame whose emitter does not match the host.

### Proof of Concept
1. Deploy a malicious `IsmpModule` contract as the destination (`to`) for a legitimate `PostRequest`, and separately have a second, unrelated legitimate `PostRequest` (commitment `C_victim`) dispatched to the same destination chain and pending delivery.
2. When the relayer submits a batch `handlePostRequests` call that includes the attacker's request, the host calls the attacker's `onAccept`. Inside `onAccept`, the attacker contract emits:
   `emit PostRequestHandled(C_victim, msg.sender)`
   using the identical event signature as `EvmHost.PostRequestHandled`.
3. The relayer's `extract_event_commitments` (tesseract/messaging/evm/src/tx.rs) scans `receipt.inner.logs()` and, since it only ABI-decodes for signature match without checking emitter address, adds `C_victim` to the set of "handled" commitments even though the real `EvmHost` never processed/delivered that request.
4. The relayer treats `C_victim`'s request as delivered and removes it from its retry/tracking set, while on-chain `_requestReceipts[C_victim]` was never set by the host — the victim's message is now permanently stuck and will never be resubmitted.

### Citations

**File:** tesseract/messaging/evm/src/tx.rs (L103-124)
```rust
/// Extract handled-message commitments from a receipt's logs.
///
/// `PostRequestHandled` carries the post request's commitment, `GetRequestHandled` the
/// commitment of the GetRequest that a delivered GetResponse answers. Both are needed:
/// `EvmHost.dispatchIncoming` swallows a reverting module callback rather than reverting
/// the tx, so a mined transaction may not have delivered anything. The presence of the
/// event is what tells the two apart.
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

**File:** tesseract/messaging/evm/src/provider.rs (L828-851)
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
```
