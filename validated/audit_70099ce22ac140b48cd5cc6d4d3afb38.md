### Title
Front-runnable duplicate-check after expensive MMR proof verification allows griefing of `HandlerV2.handlePostRequests` / `handleGetResponses` batches - (File: `evm/src/core/HandlerV2.sol`)

### Summary
`HandlerV2.handlePostRequests` and `HandlerV2.handleGetResponses` are permissionless functions that verify a Merkle-Mountain-Range multiproof covering an entire batch of leaves *before* checking whether any individual leaf in that batch has already been delivered. Because the per-leaf "already delivered" check only runs in a second loop *after* the (expensive) proof verification, an attacker can front-run a large, expensive relayer batch by delivering just one of its constituent requests/responses on its own. The legitimate batch then pays the full MMR-verification gas cost and reverts with `DuplicateMessage`, wasting the relayer's gas and delaying delivery of every other request bundled in that batch.

### Finding Description
`handlePostRequests` builds the leaf set, verifies the whole batch's MMR multiproof against the state commitment, and only then loops a second time to check each leaf against `host.requestReceipts`: [1](#0-0) 

The same pattern repeats in `handleGetResponses`, which verifies the MMR proof for the full batch of responses before checking `host.responseReceipts` per leaf: [2](#0-1) 

Both handler entry points are explicitly permissionless — "All handler methods are permissionless - anyone can call them to relay messages," and duplicate-message prevention is documented as one of the handler's responsibilities: [3](#0-2) 

Because a relayer's `PostRequestMessage`/`GetResponseMessage` (including its multiproof) is visible in the mempool before inclusion, and because delivering a single request/response is itself a cheap, unprivileged call to the same functions (with a one-element batch), an attacker can:
1. Observe a pending large batch transaction containing many `PostRequestLeaf`/`GetResponseLeaf` entries and its MMR proof.
2. Extract just one of the leaves whose `PostRequest`/`GetResponse` and a valid single-leaf multiproof can be constructed (or simply relay it ahead using the same underlying data the honest relayer already possesses/broadcasts), and submit it in a separate, cheap transaction that lands first.
3. This causes `host.requestReceipts` (or `host.responseReceipts`) to be set for that one leaf.
4. When the legitimate large batch lands afterward, it correctly performs the destination/timeout checks and the (potentially very large, multi-leaf) MMR `VerifyProof` — this is the expensive part, proportional to the number of leaves in the batch — and only then discovers the duplicate in the second loop and reverts the *entire* transaction via `DuplicateMessage`.

This is the same root-cause bug class as the `NodeOperatorManager.initializeOnUpgrade()` finding: a costly, multi-entry batch operation performs its expensive per-batch work first, then fails atomically on a single already-registered/already-delivered entry that an unprivileged actor can pre-seed via a normal, permissionless call, so the victim (here, the relayer) pays the batch's full gas cost with no state change and must retry — and can be griefed again on every retry attempt if the attacker keeps front-running one leaf out of the resubmitted (still-large) batch.

### Impact Explanation
This is a gas-griefing / relayer DoS against message delivery on Hyperbridge. A relayer that batches many `PostRequestLeaf`/`GetResponseLeaf` entries into one `handlePostRequests`/`handleGetResponses` call to amortize MMR-proof-verification gas across many messages can be repeatedly forced to pay for the (batch-size-proportional) proof verification without the batch ever completing, if an attacker keeps extracting and pre-delivering a single leaf from each resubmitted batch. This degrades the economics and reliability of the message-delivery route (repeated reverts, wasted gas, delayed delivery of every other request/response bundled with the griefed one), which is squarely in the "route unable to deliver messages" category. It does not directly cause fund loss but can materially delay or discourage batched relaying, especially for high-leaf-count batches where MMR verification cost dominates.

### Likelihood Explanation
Likelihood is non-trivial: `handlePostRequests`/`handleGetResponses` calldata (including the MMR multiproof and full leaf set) is public once broadcast/pending, and delivering a single message via the same functions is a normal, permissionless, inexpensive operation requiring no special privilege — any relayer or observer can do it. The attacker does not need to break any cryptography; they only need to notice a pending large batch and beat it to inclusion with a cheap single-leaf delivery for one of its member requests/responses, which is a standard front-running scenario on any public mempool chain that Hyperbridge's EVM hosts are deployed on.

### Recommendation
Move the duplicate-delivery check ahead of, or interleaved with, the MMR proof verification rather than after it, so an already-delivered leaf is filtered out (or the whole call cheaply reverts) before the expensive multiproof verification runs. Concretely: perform the `requestReceipts`/`responseReceipts` existence check in the same first loop that builds `leaves[]`, and either (a) revert early (cheap failure, no MMR cost paid) if any leaf is already delivered, or (b) skip already-delivered leaves when building the leaf set/dispatch loop so a single stale/duplicate leaf cannot force the entire batch — including all the other, still-undelivered leaves — to revert after the expensive verification has already run.

### Proof of Concept
1. Relayer A observes state commitment height `H` is available and submits `handlePostRequests(host, msg)` with `msg.requests` containing N `PostRequestLeaf`s (e.g., N=50) and a valid MMR multiproof for all 50, as a pending transaction.
2. Attacker B, seeing this pending transaction, extracts `msg.requests[k]` for some `k`, builds/obtains a valid single-leaf MMR proof for that same request at height `H` (which any relayer with access to the offchain MMR data — the same data broadcast/available to Relayer A — can construct), and submits a smaller `handlePostRequests(host, singleLeafMsg)` transaction with higher gas/priority so it lands first.
3. B's transaction succeeds: `host.dispatchIncoming` is called for `msg.requests[k]`, setting `host.requestReceipts[msg.requests[k].request.hash()]` to a non-zero relayer address.
4. Relayer A's original transaction is included next: it passes the destination/timeout checks, calls the potentially gas-heavy `MerkleMountainRange.VerifyProof` over all 50 leaves, then in the second loop hits `if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();` for `msg.requests[k]`, reverting the entire transaction and burning all the gas spent on the destination checks and the 50-leaf MMR verification, while none of the other 49 requests get delivered.

### Citations

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

**File:** docs/content/developers/evm/api/ihandler.mdx (L16-24)
```text
The Handler is responsible for:
- Verifying consensus proofs from Hyperbridge
- Processing and validating incoming POST requests
- Processing and validating GET responses
- Handling timeout proofs for POST requests and GET requests
- Ensuring messages haven't timed out before delivery
- Preventing duplicate message delivery

All handler methods are **permissionless** - anyone can call them to relay messages.
```
