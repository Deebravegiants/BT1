### Title
Atomic batch reverts in `HandlerV2` allow griefing that blocks delivery of valid cross-chain messages - (File: `evm/src/core/HandlerV2.sol`)

### Summary
`HandlerV2.handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` each batch-verify a Merkle Mountain Range proof for multiple leaves and then dispatch them in a loop. Because the dispatch loop reverts the *entire* transaction if any single leaf in the batch is already processed (`DuplicateMessage`) or otherwise invalid (`UnknownMessage`), an unprivileged actor can grief relayers by pre-submitting one of the batched requests individually, forcing the relayer's larger batch to revert and blocking delivery of every other legitimate message bundled with it.

### Finding Description
`handlePostRequests` builds `leaves` from `request.requests`, verifies the MMR proof once for the whole array, and then iterates a second time to dispatch: [1](#0-0) 

The same batch-verify-then-dispatch-all-or-nothing pattern exists for `handleGetResponses`: [2](#0-1) 

for `handlePostRequestTimeouts`: [3](#0-2) 

and for `handleGetRequestTimeouts` (same structure, `UnknownMessage`/`DuplicateMessage`-style guards inside a shared loop).

Since `handlePostRequests`, `handleGetResponses`, etc. are all permissionless (`notFrozen` is the only modifier) and any single POST request or GET response can be submitted individually through the same handler functions (or via `batchCall`), an attacker can:
1. Observe a relayer's pending large batch transaction in the mempool (containing many valid, unrelated requests/responses meant for various destination apps).
2. Front-run it with a single-element call delivering (or timing out) one of the same leaves.
3. When the relayer's batch lands, `host.requestReceipts(...)` (or `responseReceipts`) for that one leaf is now non-zero, so the dispatch loop hits `revert DuplicateMessage()` and the *entire* batch transaction reverts — none of the other, unrelated messages in that batch get delivered.

This mirrors the analog report's DoS class: an unprivileged party can force costly transaction failure for a batch operation due to one bad/duplicate element, delaying or blocking message delivery for a route that depends on timely batched submission (`executeBatch`-equivalent for Hyperbridge is `handlePostRequests`/`handleGetResponses` batches or `batchCall`).

### Impact Explanation
This does not directly cause theft, but it can block delivery of legitimate cross-chain messages processed in the same batch, delaying application-level effects (fee refunds, escrow releases, bridged token deliveries, intent fills) that depend on timely message/response/timeout dispatch. Because relayers commonly batch several `PostRequestLeaf`/`GetResponseLeaf` entries per MMR proof to amortize proof-verification cost, griefing one leaf can stall an arbitrarily large set of unrelated, legitimate messages, which functionally is "a route unable to deliver messages" until relayers adapt by shrinking batch sizes or filtering already-processed leaves before submission.

### Likelihood Explanation
Likelihood is limited by the fact that the underlying leaves (`PostRequestLeaf`, `GetResponseLeaf`, timeout entries) must already be committed/timed-out state that the attacker can observe on-chain or in the mempool, and the attacker must front-run with their own transaction (gas cost, but generally cheap relative to disruption caused). Any relayer batching multiple messages in a single `handlePostRequests`/`handleGetResponses`/timeout call is exposed. This is a persistent, repeatable griefing vector rather than a one-off exploit, and requires no privileged role.

### Recommendation
Make dispatch resilient to individual already-processed or invalid leaves within a batch rather than reverting the whole transaction: skip (and emit an event for) leaves that fail the duplicate/unknown checks in the dispatch loop instead of calling `revert`, so the rest of the batch still delivers. Alternatively, expose a way for relayers to pre-filter already-delivered leaves cheaply (e.g., a batched view function) before constructing the MMR proof, and/or cap batch sizes so a single griefed leaf has bounded blast radius.

### Proof of Concept
1. Relayer constructs `handlePostRequests(host, msg)` with `msg.requests` containing leaves `[L1, L2, ..., Ln]` and submits it to the mempool.
2. Attacker observes the pending tx, extracts `L1` (a `PostRequestLeaf`), and submits their own `handlePostRequests` call (or via `batchCall`) containing only `L1` with a valid proof, with higher gas price so it lands first.
3. `host.dispatchIncoming(L1.request, attacker)` succeeds in the attacker's tx, setting `requestReceipts(L1.request.hash())` to a non-zero value: [4](#0-3) 
4. The relayer's original batch now executes; in the second loop, `host.requestReceipts(leaf.request.hash()) != address(0)` is true for `L1`, so `revert DuplicateMessage()` is triggered, unwinding the entire transaction and failing to deliver `L2...Ln` even though they were valid and untouched.

### Citations

**File:** evm/src/core/HandlerV2.sol (L187-209)
```text
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
```

**File:** evm/src/core/HandlerV2.sol (L217-247)
```text
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

**File:** evm/src/core/HandlerV2.sol (L254-286)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

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
    }
```
