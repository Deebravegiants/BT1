Confirmed. `EvmHost.dispatchIncoming` (both `PostRequest` and `GetResponse` overloads) forwards to the destination app via an unbounded, un-gas-limited low-level `.call()` [1](#0-0) , and `HandlerV2.handlePostRequests`/`handleGetResponses` invoke `dispatchIncoming` in a tight loop over every leaf in a relayer-submitted batch [2](#0-1) . This is the same shape of bug as the VUSD report: an unmetered `.call` inside a loop over a permissionlessly-submitted, attacker-influenced batch.

### Title
Out-of-Gas Griefing of Batched `handlePostRequests`/`handleGetResponses` via Unmetered `dispatchIncoming` Callback - (File: evm/src/core/EvmHost.sol, evm/src/core/HandlerV2.sol)

### Summary
`EvmHost.dispatchIncoming` forwards to the destination `IApp.onAccept`/`onGetResponse` via a gas-unlimited low-level `.call()`. `HandlerV2.handlePostRequests` and `handleGetResponses` call `dispatchIncoming` once per leaf inside a loop over an entire relayer-submitted batch. Because the destination address and body of each leaf are attacker-controlled (any account can dispatch a `PostRequest`/`GetRequest` whose `to` is a malicious contract), and any address can call `handlePostRequests`/`handleGetResponses` with any valid multiproof of currently pending messages, an attacker can register a malicious destination app with a gas-draining `onAccept` fallback, get it included as one leaf of a batch alongside other unrelated pending messages, and cause the whole batch transaction to run out of gas before the loop reaches the legitimate leaves.

### Finding Description
`dispatchIncoming(PostRequest, address)` does:
```solidity
(bool success,) = address(destination)
    .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));
``` [3](#0-2) 
No gas stipend is specified, so per EIP-150 the callee receives up to 63/64 of all remaining gas. A malicious `to` contract can implement `onAccept` to spend nearly all of the gas it receives (e.g., a busy-loop until `gasleft()` is near zero), leaving only ~1/64 of the gas that was available at the point of the call.

`HandlerV2.handlePostRequests` iterates every leaf of the submitted batch and calls `host.dispatchIncoming(leaf.request, _msgSender())` for each one, sequentially, in the same transaction, after all the leaves have been proof-verified together in a single MMR multi-proof check:
```solidity
for (uint256 i = 0; i < requestsLen; ++i) {
    ...
    host.dispatchIncoming(leaf.request, _msgSender());
}
``` [4](#0-3) 
The identical pattern exists for `handleGetResponses` / `dispatchIncoming(GetResponse,...)` [5](#0-4) [6](#0-5) .

Any account can dispatch an arbitrary `PostRequest` whose `to` targets a contract it controls (the ISMP model treats `to` as an arbitrary destination module address; nothing about `dispatch` restricts `to` to "legitimate" recipients). This request will eventually be delivered via `handlePostRequests` once proven. Since `handlePostRequests` is permissionless and accepts any batch of leaves the caller can supply a valid multiproof for, an attacker (or a relayer acting maliciously, or anyone front-running a relayer's pending batch by resubmitting the same commitments alongside their own poison leaf) can compose a batch that places their gas-draining request among genuine, unrelated in-flight requests destined for other users' apps. When `handlePostRequests` is executed with a bounded gas transaction, the malicious leaf's `.call` drains ~63/64 of the remaining gas; the subsequent loop iterations, and the rest of the function's storage writes, then run out of gas, reverting the *entire* batch transaction — including the legitimate leaves that had nothing to do with the attacker.

This mirrors the report's root cause exactly: an unmetered low-level `.call()` embedded in a loop over externally-influenced batch data, callable by an unprivileged party, where a malicious callee can consume nearly all forwarded gas and force the surrounding batch to revert.

### Impact Explanation
A successful attack does not directly steal or freeze escrowed funds by itself (unlike the VUSD case where `start` only advances on success and funds sit unprocessed indefinitely), because `EvmHost.dispatchIncoming` deletes/doesn't persist the receipt on failure of the callee's `.call` and importantly, a full out-of-gas condition causes revert of the entire transaction rather than the more limited "swallow the failure and continue" pattern seen for a *single* failing call. Since the whole `handlePostRequests`/`handleGetResponses` transaction reverts, **no request receipts are persisted at all** — the batch simply needs to be resubmitted. However:
- It griefs relayers and delays delivery of legitimate, unrelated cross-chain requests batched together with the poisoned leaf, degrading the "a route unable to deliver messages" property whenever an attacker can force inclusion of their poison leaf (e.g., by front-running or colluding within a shared batch construction flow), and can be repeated indefinitely at low cost (the attacker's own request dispatch fee) against any batch a relayer attempts.
- If a relayer's software naively re-tries by resubmitting the exact same batch (including the malicious leaf) without excluding the identified bad leaf, requests could be repeatedly starved of delivery until they time out, causing them to fail closed — this is a liveness/DoS impact on message delivery rather than a direct fund-theft one.

Because the batch is atomic (any leaf failing reverts everything, since a failure inside the loop simply continues on `false` while running out-of-gas reverts the frame entirely), this is best characterized as a griefing/liveness bug rather than a fund-freezing one on its own — the funds/requests are not permanently stuck, only delayed and their delivery cost increased, unlike the referenced VUSD bug where `start` genuinely halts forward progress on a shared FIFO queue.

### Likelihood Explanation
Likelihood is moderate: dispatching an arbitrary `PostRequest`/`GetRequest` destined for an attacker-controlled `to` is trivial and costs only the protocol dispatch fee. Getting that malicious leaf included in the *same* `handlePostRequests`/`handleGetResponses` batch as victim leaves requires either (a) the relayer software batching multiple pending leaves together (which the `tesseract` relayer and `IHandlerV2.batchCall` design encourage for gas efficiency) without per-leaf gas isolation, or (b) the attacker being the one constructing/submitting the batch. Given `handlePostRequests` is explicitly documented as permissionless, an attacker submitting their own crafted batch that mixes a poison leaf with real pending leaves (to grief specific relayers/apps) is straightforward.

### Recommendation
Forward a fixed, bounded gas stipend to each `IApp.onAccept`/`onGetResponse`/`onGetTimeout`/`onPostRequestTimeout` callback in `EvmHost.dispatchIncoming`/`dispatchTimeOut` (e.g., `.call{gas: GAS_LIMIT}(...)`), sized to a documented maximum callback budget, so no single leaf in a batch can consume more than a bounded fraction of the transaction's gas. Additionally, consider isolating each leaf's dispatch (e.g., via a bounded low-level call combined with try/catch-style gas accounting, or processing leaves independently rather than as one atomic loop) so a single malicious/expensive leaf cannot cause every other leaf in the same batch to revert.

### Proof of Concept
1. Attacker deploys `MaliciousApp` with:
```solidity
function onAccept(IncomingPostRequest calldata) external {
    while (gasleft() > 2000) { /* burn gas */ }
}
```
2. Attacker dispatches a `PostRequest` from any source chain with `to = address(MaliciousApp)` via the standard `dispatch` flow — no privileged status required.
3. Once the request is provable via a state/MMR proof, the attacker (or anyone) submits `handlePostRequests` with a batch of leaves containing both the malicious leaf and several legitimate, unrelated pending leaves for other apps [7](#0-6) , sized (via `gas:` on the outer call) such that after the malicious leaf's `dispatchIncoming` call drains ~63/64 of remaining gas, insufficient gas remains for the loop's remaining iterations.
4. The transaction reverts with an out-of-gas error, meaning none of the batched leaves (including the legitimate ones) are delivered in that attempt, forcing a resubmission and wasting the submitter's gas — repeatable at will against any batch containing the attacker's poison leaf.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L824-847)
```text
    function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
        // replay protection
        bytes32 commitment = response.request.hash();
        _responseReceipts[commitment] = ResponseReceipt({
            relayer: relayer,
            responseCommitment: response.hash()
        });

        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

        if (!success) {
            // so that it can be retried
            delete _responseReceipts[commitment];
            return;
        }

        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/HandlerV2.sol (L181-247)
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

    /**
     * @dev check response proofs, message delay and timeouts, then dispatch get responses to modules
     * @param host - Ismp host
     * @param message - batch get responses
     */
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 responsesLength = message.responses.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](responsesLength);

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
    }
```
