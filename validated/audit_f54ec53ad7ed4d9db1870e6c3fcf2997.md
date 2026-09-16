### Title
Relayer gas drained with no refund when `HandlerV2.batchCall()` PTB-style atomic batch reverts due to one racing/failing message - (File: `evm/src/core/HandlerV2.sol`)

### Summary
Hyperbridge's `IHandlerV2.batchCall()` bundles multiple independent handler calls (`handleConsensus`, `handlePostRequests`, `handleGetResponses`, timeout handlers) into a single atomic transaction via `delegatecall`, exactly like a SUI PTB bundles `withdraw()` with `on_call()`. If any single call in the batch reverts, the entire batch reverts and none of the relayer's gas expenditure on the other, otherwise-valid messages is compensated — mirroring the SUI M-5 root cause of "atomicity without a corresponding refund path."

### Finding Description
`HandlerV2.batchCall` explicitly documents and enforces full-batch atomicity: [1](#0-0) 

Each per-message handler (`handlePostRequests`, `handleGetResponses`, timeout handlers) performs several hard `revert`s that are unrelated to the module's own callback outcome, e.g. duplicate detection and proof validity checks: [2](#0-1) [3](#0-2) 

Note that the module-callback failure path itself (`dispatchIncoming`, `dispatchTimeOut` in `EvmHost.sol`) was deliberately designed to *not* propagate a revert — it uses a low-level `.call` with a `success` check and simply rolls back the receipt for retry instead of reverting the whole transaction: [4](#0-3) 

This is precisely the mitigation the SUI report recommends (isolate the fallible callback from the refund/payment logic). However, that isolation is only applied to the *module callback*. It is not applied to the outer batching layer: `DuplicateMessage()` and `InvalidProof()` checks inside `handlePostRequests`/`handleGetResponses` are hard reverts, and since `batchCall` wraps everything in one atomic transaction, one bad/raced message anywhere in the batch reverts delivery (and any relayer-fee reward transfer inside `dispatchIncoming`) for every other valid message bundled alongside it.

The relayer client itself batches multiple messages for gas efficiency and documents this atomicity: [5](#0-4) [6](#0-5) 

There is no on-chain or off-chain mechanism that refunds the submitting relayer's spent gas when the whole `batchCall` reverts. The protocol's only "refund" is the relayer-fee reward paid inside `dispatchIncoming` on success (`EvmHost.sol` lines 841-847, 901-905) — and that reward path is never reached if the surrounding batch transaction reverts.

### Impact Explanation
An honest relayer that batches N messages to save gas can lose 100% of the gas paid for the whole transaction — including gas for verifying and would-be-successful delivery of the other N-1 valid messages — because of a single message in the batch failing a hard check such as `DuplicateMessage` or `InvalidProof`. This is directly and repeatedly triggerable by a competing relayer (or attacker) racing to deliver one of the same messages first, or by transient proof staleness from a light-client update race, causing the batch relayer's gas to be burned with zero relayer-fee compensation. Repeated over many batches, this creates a real gas-drain/insolvency and DoS vector against relayer operators, analogous to the SUI TSS gas drain in the referenced report, and directly reachable by any unprivileged relayer submitting proofs through `EvmHost`/`HandlerV2`.

### Likelihood Explanation
Likelihood is meaningful but not universal: it requires either (a) natural races between multiple relayers delivering the same messages (common in a permissionless relayer network where multiple parties monitor the same events) or (b) an adversary deliberately front-running a single cheap message inside a relayer's pending batch to force a `DuplicateMessage`/`InvalidProof` revert and destroy the honest relayer's gas spend on the rest of the batch. Because `batchCall` is permissionless and the relayer client (`tesseract/messaging/evm/src/tx.rs`) actively groups multiple messages together for gas efficiency, larger batches increase the blast radius of a single failing message, making this an economically incentivized griefing vector against competing relayers rather than a purely theoretical issue.

### Recommendation
Do not let a single message's hard revert (duplicate detection, proof staleness) abort delivery of unrelated valid messages in the same batch. Either: (1) make `handlePostRequests`/`handleGetResponses`/timeout handlers tolerant of individual duplicate/already-processed entries by skipping them instead of reverting the whole call (mirroring the "isolate the fallible step" pattern already used for module callbacks in `dispatchIncoming`), or (2) require relayers to simulate/pre-filter batches so that provably-failing entries are excluded before submission, or (3) provide a compensating relayer-gas-refund mechanism paid from protocol fees when a submitted batch reverts due to a race with another relayer, so gas loss from unavoidable races does not fall entirely on the submitting relayer.

### Proof of Concept
1. Relayer A observes N pending messages for a destination chain and builds `batchCall([handleConsensus, handlePostRequests(msg_1..msg_N)])` per `build_batch_inner_calls` / `submit_batch_messages` in `tesseract/messaging/evm/src/tx.rs`.
2. Relayer B (or an attacker) submits and lands `handlePostRequests(msg_k)` for one message `msg_k` inside A's pending batch, first.
3. A's batch transaction lands afterward; the loop in `handlePostRequests` hits `if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();` for `msg_k` (`evm/src/core/HandlerV2.sol` line 207).
4. Because `batchCall` delegatecalls sequentially and reverts the whole batch on any failure (`evm/src/core/HandlerV2.sol` lines 129-135), A's entire transaction reverts — the consensus update and all N-1 otherwise-valid message deliveries (and their relayer-fee rewards) are lost, and A has paid full gas for the reverted transaction with zero compensation.

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

**File:** evm/src/core/HandlerV2.sol (L204-210)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L241-247)
```text
        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
    }
```

**File:** evm/src/core/EvmHost.sol (L885-906)
```text
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
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

**File:** tesseract/messaging/evm/src/tx.rs (L536-538)
```rust
	// Atomic semantics: if the tx succeeded every inner call did, so no
	// per-message unsuccessful bucket.
	Ok((events, Vec::new(), new_epochs))
```
