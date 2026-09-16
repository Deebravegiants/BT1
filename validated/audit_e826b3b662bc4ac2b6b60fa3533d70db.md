### Title
Single-message revert inside `HandlerV2.batchCall` blocks delivery of every unrelated message batched with it - ([File: evm/src/core/HandlerV2.sol])

### Summary
`HandlerV2.batchCall` executes a relayer's batched handler calls (`handleConsensus`, `handlePostRequests`, `handleGetResponses`, timeout handlers) via sequential `delegatecall`s and reverts the **entire transaction** if any single inner call fails. `handlePostRequests` itself reverts the whole call if *any one* leaf in the batch fails a per-message check (stale destination, elapsed timeout, duplicate, bad proof). Because the Tesseract relayer packs many unrelated messages — including the destination chain's consensus update — into one `batchCall` transaction to save gas, one poisoned/expired message can permanently block delivery of every other message riding in the same batch, exactly analogous to the Derby `Vault.setDeltaAllocationsInt` bug where one blacklisted allocation blocked the whole rebalance.

### Finding Description
`HandlerV2.batchCall` is atomic by design: [1](#0-0) 

`handlePostRequests` validates every leaf in the batch (`request.requests`) with per-message checks — destination match and timeout — inside a loop, and `revert`s the whole function on the first failing leaf, before any membership-proof verification or dispatch happens: [2](#0-1) 

The Tesseract relayer deliberately batches many unrelated ISMP messages (a consensus update plus N application POST/GET messages targeted at the same destination) into a single `HandlerV2.batchCall` transaction to amortize gas: [3](#0-2) [4](#0-3) 

Because `batchCall` is fully atomic (any inner `delegatecall` failure reverts everything), one message that fails the up-front per-leaf check in `handlePostRequests` — most reliably a `timeout` that has now elapsed by block-inclusion time, since the timeout is fixed at dispatch time and is not attacker-adjustable after the fact but is fully known/controllable by whoever dispatches the original request — causes `revert MessageTimedOut()`, which bubbles up through the `delegatecall` and reverts the **whole** `batchCall`, including the consensus update and every unrelated user's request/response batched alongside it: [5](#0-4) 

This is structurally identical to the referenced Derby bug class: a single item embedded in a shared batch operation (there, an allocation to a blacklisted protocol inside `rebalance`; here, one timed-out/mismatched-destination leaf inside a relayer's `handlePostRequests` batch) causes the entire multi-party operation to revert, rather than being skipped/isolated. Notably, the protocol elsewhere explicitly engineers around this exact class of bug — `EvmHost.dispatchIncoming` intentionally does a low-level `.call()` and swallows failures with an early `return` instead of reverting "the entire batch" so that one bad `onAccept` doesn't brick delivery of the rest: [6](#0-5) 

but that isolation only protects the *destination app's* callback, not the handler-level per-leaf checks (`InvalidMessageDestination`, `MessageTimedOut`, `DuplicateMessage`, `InvalidProof`) that run *before* dispatch inside `handlePostRequests`/`handleGetResponses`, which still `revert` and can now take down an entire `batchCall`.

### Impact Explanation
Any single message that will fail a per-leaf handler check by the time its containing batch lands on-chain (most simply, a short/expired `timeoutTimestamp` set by whoever dispatched it, or a stale duplicate) forces the relayer's entire `batchCall` transaction to revert. If that message is bundled with a consensus update or with other unrelated users' messages (as the relayer code is designed to do for gas efficiency), none of them are delivered in that attempt — this is a "route unable to deliver messages" condition: legitimate requests, responses, and even light-client consensus advancement for the destination chain can be repeatedly blocked until relayers learn to exclude the poisoned message from every batch, which requires off-chain intervention with no on-chain remedy (unlike Vault's guardian who can at least try to fix state, there's no way to selectively "skip" a leaf inside `handlePostRequests`).

### Likelihood Explanation
Likelihood is significant: any unprivileged sender can dispatch a POST/GET request with a short `timeout` (or otherwise doomed to fail a leaf check) to a destination chain that a relayer batches non-atomically-isolated messages for. Since relayers batch multiple pending messages destined for the same chain to save gas (`submit_batch_messages`), a single such message getting caught in a batch with unrelated traffic is a routine occurrence, not a contrived edge case, and requires no special privilege or timing precision beyond setting a tight timeout on an otherwise-ordinary dispatch.

### Recommendation
Make `handlePostRequests` / `handleGetResponses` isolate failures per-leaf instead of reverting the whole call: skip (and optionally emit an event for) any leaf that fails its destination/timeout/duplicate check rather than reverting, mirroring the isolation already applied in `EvmHost.dispatchIncoming` for `onAccept` failures. Alternatively, have the relayer construct batches so that failure-prone messages (e.g., those close to their timeout) are never bundled with consensus updates or other users' messages, and/or have `batchCall` support per-call try/catch semantics (already partially modeled by `BatchCallFailed(index, reason)`) so a single failing call can be reported and excluded without reverting the whole transaction.

### Proof of Concept
1. A user dispatches a `PostRequest` via `IDispatcher.dispatch` with a `timeout` value close to the current block time (e.g., a few seconds in the future).
2. Before the request can be delivered, several other unrelated users dispatch their own requests to the same destination chain; a relayer picks up all of them together with a pending consensus update and packs them into a single `HandlerV2.batchCall([handleConsensus(...), handlePostRequests([...many leaves including the near-expired one...])])`.
3. By the time the batch transaction executes on-chain, the near-expired request's `timeout()` has elapsed; the loop in `handlePostRequests` (`evm/src/core/HandlerV2.sol:181-210`) hits `if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();`.
4. The revert propagates through the `delegatecall` in `batchCall` (`evm/src/core/HandlerV2.sol:129-135`), reverting the entire transaction — the consensus update and every other unrelated user's message in the batch fail to land, even though only one message was actually invalid.

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

**File:** evm/src/core/HandlerV2.sol (L181-210)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

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
    }
```

**File:** tesseract/messaging/evm/src/tx.rs (L441-446)
```rust
/// Submit a full batch of ISMP messages as a single `IHandlerV2.batchCall` transaction.
///
/// One tx replaces what would otherwise be N separate txs (one per message),
/// cutting gas overhead and nonce management complexity. Atomic: if any
/// inner call reverts, the whole transaction reverts.
pub async fn submit_batch_messages(
```

**File:** tesseract/messaging/evm/src/tx.rs (L536-539)
```rust
	// Atomic semantics: if the tx succeeded every inner call did, so no
	// per-message unsuccessful bucket.
	Ok((events, Vec::new(), new_epochs))
}
```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```
