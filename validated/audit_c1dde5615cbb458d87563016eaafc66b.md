### Title
Unbounded relayer-controlled loops in `HandlerV2` message batches allow gas-exhaustion DoS of request/response delivery - (File: evm/src/core/HandlerV2.sol)

### Summary
`HandlerV2.handlePostRequests` and `HandlerV2.handleGetResponses` iterate over caller-supplied `PostRequestLeaf[]` / `GetResponseLeaf[]` arrays twice (once for the MMR-leaf/validation pass and once for the dispatch pass) with no upper bound on array length. This mirrors the reported `finalizeSpecimenSession` bug class: an externally supplied, permissionless batch is processed via unbounded loops whose gas cost scales linearly (or worse, given per-item external calls to `host.dispatchIncoming`) with the number of entries, risking exceeding the block gas limit.

### Finding Description
`handlePostRequests` builds an MMR leaf array and loops once to validate destination/timeout for every entry, then loops again to dispatch each request via `host.dispatchIncoming`, an external call into `EvmHost` that itself calls into the destination `IApp` contract: [1](#0-0) 

`handleGetResponses` follows the identical two-pass pattern over `GetResponseLeaf[]`, again dispatching to `host.dispatchIncoming` per entry: [2](#0-1) 

`handlePostRequestTimeouts` also loops over an unbounded `message.timeouts` array, doing a trie non-membership proof verification and a dispatch call per item: [3](#0-2) 

There is no constant or check anywhere in `HandlerV2.sol` (e.g. `MAX_REQUESTS`, `MAX_MESSAGES`, batch-size guard) limiting the size of `request.requests`, `message.responses`, or `message.timeouts`; a search for such bounds across the EVM handler code returned no results. Each iteration performs non-trivial work: a `keccak256`-based `hash()` computation, an MMR leaf array write, and (in the second loop) an external `CALL` into `EvmHost.dispatchIncoming`, which itself forwards to the destination `IApp` via a raw external call. Because these functions are `external` and callable by anyone (`notFrozen(host)` is the only gate — no length restriction), a relayer (or any address, since the function is permissionless) can submit an arbitrarily large batch. Unlike a legitimate relayer who would choose sane batch sizes, the vulnerability class described in the report is about the *protocol construct itself* having no hard ceiling, which becomes exploitable when the number of pending items driving a required state transition grows unbounded due to network activity, making it impossible for anyone to construct a call that fits within the block gas limit.

### Impact Explanation
If the number of leaves/timeouts that must be included in a single call to reach a valid MMR proof root (or to service backlog) grows large enough, gas costs exceed the block gas limit, and the message batch can never be successfully delivered on-chain — a permanent denial of service on the message-delivery path for the affected batch. Since `handlePostRequests`/`handleGetResponses` are the sole entry points by which POST requests and GET responses are delivered to destination applications, an inability to execute them (due to gas exhaustion) blocks message delivery entirely for the affected request set, freezing in-flight funds/fee escrows tied to those requests (relayer fees, payer refunds) until timeout, and in the worst case (if the timeout path is similarly gas-bound) indefinitely.

### Likelihood Explanation
Exploitability depends on whether relayers are forced to include large numbers of leaves in a single proof (e.g., an MMR multiproof potentially requiring inclusion of many sibling leaves for verification, or backlog of many unprocessed requests accumulating faster than they can be cleared in gas-limited batches). Relayer tooling in this codebase (`tesseract/messaging/evm/src/tx.rs`) does chunk batches and estimates gas dynamically (`generate_contract_calls`, `submit_batch_messages`), which mitigates but does not eliminate the underlying unbounded-loop design; it relies entirely on off-chain relayer discipline rather than an on-chain hard limit. This is a lower-likelihood, design-level Medium issue rather than a directly triggerable exploit by an unprivileged single transaction, since off-chain relayer software already imposes practical batch-size limits — but the on-chain contract itself provides no protection if that off-chain assumption is violated or if request backlog outpaces relayer capacity.

### Recommendation
Introduce an explicit maximum batch size (`MAX_REQUESTS_PER_BATCH`, `MAX_RESPONSES_PER_BATCH`, `MAX_TIMEOUTS_PER_BATCH`) enforced via `revert` in `handlePostRequests`, `handleGetResponses`, and `handlePostRequestTimeouts`/`handleGetRequestTimeouts` in `evm/src/core/HandlerV2.sol`, so callers are forced to paginate large batches into multiple transactions rather than relying solely on off-chain gas estimation and chunking in the relayer.

### Proof of Concept
Conceptual: an attacker (or organic network growth) causes a very large number of POST requests to become includable/necessary in a single `PostRequestMessage.requests` array (e.g., because the MMR proof for a target leaf set requires many leaves to be supplied together, or a relayer batches too aggressively). Calling `HandlerV2.handlePostRequests(host, request)` with `request.requests.length` large enough that the combined cost of the destination/timeout-check loop, MMR proof verification, and the per-item `dispatchIncoming` external-call loop exceeds the chain's block gas limit causes every attempt to submit this batch to revert with an out-of-gas condition, permanently preventing delivery of that batch of requests on-chain. No on-chain guard (`MAX_REQUESTS`-style check) exists in `evm/src/core/HandlerV2.sol` to prevent constructing such an oversized batch in the first place.

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
