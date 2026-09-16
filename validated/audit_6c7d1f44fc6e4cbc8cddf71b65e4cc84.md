### Title
Per-item validation failures inside batched message loops revert the entire batch instead of skipping the offending element - (File: evm/src/core/HandlerV2.sol)

### Summary
`HandlerV2.handlePostRequests()`, `handleGetResponses()`, `handlePostRequestTimeouts()`, and `handleGetRequestTimeouts()` each iterate over an array of requests/responses supplied in a single relayer transaction and `revert` the whole call the moment any single element fails a per-item check, instead of skipping that element and continuing to process the rest of the batch. The same all-or-nothing pattern exists on the Substrate side in `pallet-ismp`'s `execute()` and the ISMP core `request::handle`/`response::handle` functions.

### Finding Description
In `handlePostRequests`, the first loop checks destination and timeout per-leaf and reverts the entire call on the first bad leaf: [1](#0-0) 
and the second loop (post-proof-verification) reverts the entire call if any single leaf is a duplicate: [2](#0-1) 

The identical shape recurs in `handleGetResponses` (revert on `UnknownMessage`/`DuplicateMessage` for a single response in the batch): [3](#0-2) 
and in the timeout handlers (`handlePostRequestTimeouts`, `handleGetRequestTimeouts`), which revert the whole call if any single timeout entry is not yet timed out or unknown: [4](#0-3) [5](#0-4) 

The same design exists in the Substrate implementation. `pallet_ismp::Pallet::execute` maps every message in the batch through `handle_incoming_message` and short-circuits the whole unsigned extrinsic (`handle_unsigned`) on the first error via `collect::<Result<Vec<_>, _>>()`: [6](#0-5) 
and within a single `RequestMessage`, `request::handle` reverts the whole message the first time any request in the batch is a duplicate, timed out, or misdirected: [7](#0-6) 

This is precisely the bug class from the referenced report: a loop whose body can revert for a single element aborts the entire operation rather than using `continue`/`break`/graceful-skip semantics for just that element.

### Impact Explanation
Because relayers batch multiple independent cross-chain requests/responses from potentially unrelated applications into one MMR-proved transaction (`PostRequestMessage.requests`, `GetResponseMessage.responses`, etc.), a single bad element — a request that a competing relayer already delivered (`DuplicateMessage`), or one that has crossed its `timeout` between proof construction and inclusion (`MessageTimedOut`) — reverts delivery of every other, still-valid request/response in that same batch. Since POST requests carry a hard timeout after which they can only be timed-out/refunded rather than delivered, repeated batch failures near the timeout boundary (whether from relayer race conditions or an adversary padding a batch, or simply included stale entries) can push otherwise-valid, legitimate cross-chain messages past their timeout, permanently preventing their delivery and forcing the source-side timeout/refund path instead of the intended cross-chain action. This matches the accepted impact category of "a route unable to deliver messages" for the batch's other, valid entries.

### Likelihood Explanation
This is reachable by any permissionless relayer submitting a `handlePostRequests`/`handleGetResponses`/timeout batch — the handler functions are explicitly documented as "permissionless" and callable by anyone. Duplicate-delivery races are expected in a multi-relayer network (Hyperbridge itself relies on competing relayers), and timeout-proximity batches are a normal relayer optimization to save gas, so the triggering condition (one bad element among many good ones) is a routine, not a contrived, operational scenario rather than requiring privileged access.

### Recommendation
Change the per-item validation loops in `HandlerV2.sol` (and the analogous Rust batch handlers) to skip only the offending request/response (e.g. `continue`) rather than reverting the entire call, and emit a per-item failure event so relayers/observers can react. Where dispatch-order/proof-membership constraints make skipping harder (e.g., the MMR multiproof is built against the full leaf set), consider separating "proof verification" (which must cover exactly the supplied leaves) from "per-leaf validity" (timeout/duplicate/destination), and allow the latter to mark individual leaves as failed/skipped post-verification instead of aborting dispatch for the whole batch.

### Proof of Concept
1. A relayer observes N valid POST requests destined for chain X, all close to their timeout, and constructs a single `PostRequestMessage` with an MMR multiproof covering all N leaves via `HandlerV2.handlePostRequests`.
2. Before this transaction lands, a competing relayer delivers one of the N requests in a separate, faster transaction (or one of the N requests' `timeout` elapses by the time this tx is mined).
3. When the batched transaction executes, the first loop or the duplicate-check loop in [8](#0-7)  hits `MessageTimedOut()` or `DuplicateMessage()` for that one request and reverts the entire call.
4. All N−1 otherwise-valid, non-expired, non-duplicate requests fail to be dispatched in this attempt; if this repeats until each request's own timeout elapses, those requests become permanently undeliverable and can only be resolved via `handlePostRequestTimeouts`, i.e., the intended cross-chain action never executes.

### Citations

**File:** evm/src/core/HandlerV2.sol (L190-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

**File:** evm/src/core/HandlerV2.sol (L226-246)
```text
        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // don't check for timeouts because it's checked on Hyperbridge

            // known request? also serves as source check
            FeeMetadata memory meta = host.requestCommitments(leaf.response.request.hash());
            if (meta.sender == address(0)) revert UnknownMessage();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.response.hash());
        }

        bytes32 root = host.stateMachineCommitment(message.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
```

**File:** evm/src/core/HandlerV2.sol (L267-285)
```text
        for (uint256 i = 0; i < timeoutsLength; ++i) {
            PostRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            // known request? also serves as source check
            bytes32 requestCommitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(requestCommitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(REQUEST_RECEIPTS_STORAGE_PREFIX, requestCommitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(PostRequestTimeout(request, _msgSender()), meta, requestCommitment);
        }
```

**File:** evm/src/core/HandlerV2.sol (L303-320)
```text
        for (uint256 i = 0; i < timeoutsLength; ++i) {
            GetRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            bytes32 commitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(commitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(RESPONSE_RECEIPTS_STORAGE_PREFIX, commitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(GetRequestTimeout(request, _msgSender()), meta, commitment);
        }
```

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
