## Title
Single duplicate/timed-out/misdirected request reverts an entire batched delivery, denying message delivery to all other valid requests in the same proof - (File: `evm/src/core/HandlerV2.sol`, `modules/ismp/core/src/handlers/request.rs`)

### Summary
`HandlerV2.handlePostRequests` (and its pallet-ismp analogue, the request `handle` function) validates every leaf in a batched `PostRequestMessage` in a single pass and hard-`revert`s the whole call if *any one* leaf fails a per-element check (wrong destination, timed out, or already delivered). This mirrors the Celo `revokeVotes` defect: a function meant to act on a *batch* of independent items requires *every* item to satisfy a precondition, and reverts the entire operation instead of treating the offending item as a no-op. Because Hyperbridge batches many independent, unrelated requests behind one Merkle-Mountain-Range multiproof, one bad element can block delivery of an arbitrary number of otherwise-valid requests.

### Finding Description
`handlePostRequests` loops over `request.requests` twice: [1](#0-0) 

```solidity
for (uint256 i = 0; i < requestsLen; ++i) {
    PostRequestLeaf memory leaf = request.requests[i];
    if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
    if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
    leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
}
...
for (uint256 i = 0; i < requestsLen; ++i) {
    PostRequestLeaf memory leaf = request.requests[i];
    if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
    host.dispatchIncoming(leaf.request, _msgSender());
}
```

Any single leaf that is (a) not destined for this chain, (b) past its timeout, or (c) already delivered (has a receipt) causes `revert`, unwinding the entire transaction — including the membership-proof verification and delivery of every other, valid leaf in `requestsLen`. The identical structural flaw exists in the Substrate handler: [2](#0-1)  uses `Err(...)? ` inside a `for` loop over `msg.requests`, so a single `DuplicateRequest`, `RequestTimeout`, `InvalidRequestDestination`, or `RequestProxyProhibited` condition on any one request aborts the whole `handle` call before any request in the batch is dispatched — even though the up-front check in the original report explicitly recommends treating a failing element as a no-op for the loop iteration rather than reverting the entire batch operation.

This differs from the intentionally atomic `HandlerV2.batchCall` (which documents "any failure reverts the entire batch" as a deliberate, opt-in relayer convenience, see [3](#0-2) ): `handlePostRequests` is a single dispatched message containing many logically-independent requests bound together only by the relayer's choice of MMR multiproof, not a relayer-composed batch of arbitrary calls. A relayer (or an attacker racing a relayer's pending transaction) can cause a "poison pill" request to make it into the leaf set, and the entire proof — potentially carrying many legitimate, still-undelivered requests to many different destination applications — fails to deliver.

### Impact Explanation
Since `handlePostRequests` is permissionless and reachable by any relayer/caller, an attacker who observes a pending `handlePostRequests`/`batchCall` transaction in the mempool can front-run delivery of just one of its constituent requests (permissionless per-request replay is possible since `dispatchIncoming`/receipts are keyed per request hash), causing the whole subsequent multi-request delivery to revert with `DuplicateMessage()`. Similarly, an attacker can simply wait until one request in a soon-to-be-relayed batch crosses its timeout to force a revert of the entire batch via `MessageTimedOut()`. This is a repeatable griefing/denial-of-service vector against message delivery — the exact "route unable to deliver messages" outcome called out as an acceptable impact — and can be used to indefinitely stall delivery of unrelated applications' requests bundled in the same MMR proof, forcing relayers into costly per-request resubmission or enabling deliberate delay/timeout-forcing of targeted requests.

### Likelihood Explanation
Likelihood is high in adversarial conditions because: (1) all preconditions (destination check, timeout check, receipt/duplicate check) are evaluated purely from public on-chain/committed data, so an attacker can always find or engineer a poisoning leaf; (2) delivering (or waiting out) a single leaf ahead of a pending relayer transaction is a normal permissionless action requiring no special access; (3) batching is the expected/efficient mode of operation for relayers submitting many requests via one MMR multiproof, so the attack surface (batches with >1 request) is the common case, not an edge case.

### Recommendation
Change the per-request validation loops in both `HandlerV2.handlePostRequests` (`evm/src/core/HandlerV2.sol`) and the pallet-ismp `request::handle` (`modules/ismp/core/src/handlers/request.rs`) so that a request failing an individual precondition (wrong destination, timed out, duplicate) is skipped/excluded from dispatch (treated as a no-op for that element, optionally emitting an event/error result for that specific leaf) rather than causing the entire message to revert. The membership-proof verification should still cover all originally committed leaves, but delivery/dispatch should proceed for every leaf that independently satisfies its own preconditions.

### Proof of Concept
1. Relayer observes N pending POST requests (from N unrelated applications) committed to the source chain's outgoing MMR, all destined for chain B.
2. Relayer builds one `PostRequestMessage` with a multiproof covering all N leaves and submits `handlePostRequests(host, request)` on chain B.
3. Attacker, watching the mempool, submits a separate transaction that independently delivers (or has already delivered) exactly one of the N leaves before the relayer's transaction lands, so that leaf's `host.requestReceipts(hash)` is non-zero when the relayer's tx executes — or simply waits until one leaf's timeout has elapsed.
4. When the relayer's transaction executes, the loop in `evm/src/core/HandlerV2.sol` lines 204-209 hits `revert DuplicateMessage()` (or the timeout check at line 195 hits `revert MessageTimedOut()`), reverting delivery of all N requests, not just the poisoned one.
5. Repeat against any batch to indefinitely delay/deny delivery of otherwise valid, unrelated application messages bundled in the same proof.

### Citations

**File:** evm/src/core/HandlerV2.sol (L123-135)
```text
    /**
     * @dev Process a batch of encoded handler calls in a single transaction.
     * Uses delegatecall to self so msg.sender is preserved and storage writes
     * happen in this contract's context. Atomic, any failure reverts the entire batch.
     * @param calls - array of ABI-encoded handler function calls
     */
    function batchCall(bytes[] memory calls) external {
        uint256 len = calls.length;
        for (uint256 i = 0; i < len; ++i) {
            (bool success, bytes memory returnData) = address(this).delegatecall(calls[i]);
            if (!success) revert BatchCallFailed(i, returnData);
        }
    }
```

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

**File:** modules/ismp/core/src/handlers/request.rs (L55-84)
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

		// either the host is a router and can accept requests on behalf of any chain
		// or the request must be intended for this chain
		if req.dest_chain() != host.host_state_machine() && !host.is_router() {
			Err(Error::InvalidRequestDestination { meta: req.clone().into() })?
		}

		let source_chain = req.source_chain();

		// in order to allow proxies, the host must configure the given state machine
		// as it's proxy and must not have a state machine client for the source chain
		let allow_proxy = host.is_allowed_proxy(&msg.proof.height.id.state_id) &&
			check_state_machine_client(source_chain);

		// check if the request is allowed to be proxied
		if source_chain != msg.proof.height.id.state_id && !allow_proxy {
			Err(Error::RequestProxyProhibited { meta: req.clone().into() })?
		}
	}
```
