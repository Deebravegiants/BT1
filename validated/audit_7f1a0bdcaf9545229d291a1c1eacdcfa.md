### Title
Unbounded `PostRequest.body` size enables unlimited relayer gas-griefing via quadratic `keccak256`/`abi.encode` cost in `HandlerV2.handlePostRequests` - ([File: evm/src/core/HandlerV2.sol])

### Summary
`EvmHost.dispatch(DispatchPost)` accepts a `post.body` of arbitrary size with no length cap, and every relayer that later delivers the resulting `PostRequest` via the permissionless `HandlerV2.handlePostRequests` must re-encode and `keccak256`-hash that same body (via `Message.hash`) for every request in the batch before it can even be included in the MMR proof verification. Because Solidity's `keccak256`/memory-copy cost scales with input size (and EVM memory-expansion cost scales quadratically with total memory used), a malicious dispatcher can force any relayer who tries to deliver the message to burn an attacker-controlled, effectively unbounded amount of gas, while paying only the fixed relayer fee they set themselves.

### Finding Description
`EvmHost.dispatch(DispatchPost memory post)` builds a `PostRequest` directly from the caller-supplied `post.body` and commits to it with `request.hash()`, with no validation of `body.length`: [1](#0-0) 

`Message.hash(PostRequest memory req)` computes `keccak256(abi.encode(req))`, which requires ABI-encoding (a full memory copy) and hashing the entire `body`: [2](#0-1) 

When the request is later relayed to the destination chain, `HandlerV2.handlePostRequests` is invoked by any permissionless relayer. For every leaf in the batch it calls `leaf.request.hash()` to build the MMR leaf used in `MerkleMountainRange.VerifyProof`, and does so again in the dispatch loop before delivering to the destination app: [3](#0-2) 

Since there is no upper bound anywhere in `dispatch`, `PostRequest`, or `handlePostRequests` on `body.length`, an attacker can dispatch a request with a multi-hundred-KB or MB-sized body. The attacker pays for the `dispatch` call on the source chain themselves (a one-time, attacker-controlled cost), but the *relayer* who must call `handlePostRequests` on the destination chain to earn the (attacker-set) relayer fee is forced to pay the quadratic hashing/memory-expansion cost for that oversized body — this is the same root-cause pattern as the referenced `SpecificActionERC20TransferBatchEnforcer` bug: unbounded calldata fed into `keccak256` with no size constraint, fully controlled by an unprivileged party.

### Impact Explanation
This directly targets the reachable, unprivileged "message dispatch and delivery" path (`EvmHost`/`HandlerV2`) called out in scope. The consequences are:
- **Relayer griefing**: the relayer that delivers the message pays gas proportional (quadratically, due to memory expansion) to a body size fully chosen by the attacker, while collecting only the attacker-defined `fee`. Relayers may become unwilling to deliver such requests economically.
- **Route unable to deliver messages**: if the body is large enough that `abi.encode`/`keccak256` and the surrounding batch processing exceed the block gas limit, `handlePostRequests` becomes impossible to execute at all, permanently preventing the request from being delivered on the destination chain and leaving the relayer fee locked in the source `EvmHost` (`_requestCommitments[commitment]`) until a timeout is separately proven, and requiring an additional timeout proof/gas cost to recover funds.
This qualifies as Medium/High severity: it enables an unprivileged dispatcher to weaponize the permissionless relaying path into a denial-of-service and fee-griefing vector against the relayer network, and in the worst case a "route unable to deliver messages" scenario.

### Likelihood Explanation
Likelihood is high: `dispatch(DispatchPost)` is a standard, permissionless, unprivileged entry point exposed to any calling contract/EOA-via-contract, and nothing in `EvmHost.sol` or `Message.sol` restricts `body` size. No special privileges, timing, or race conditions are required — a single transaction with an oversized `body` is sufficient to create the malicious request.

### Recommendation
Enforce a maximum `body` length (and similarly cap other unbounded relayer-hashed fields such as `GetRequest.keys`/`context`) in `EvmHost.dispatch` for both `DispatchPost` and `DispatchGet`, rejecting requests whose size exceeds a configurable `maxRequestBodySize` `HostParam`. Additionally, consider bounding batch sizes and per-request weight/gas accounting in `HandlerV2.handlePostRequests`/`handleGetResponses` so a single oversized request cannot make an entire batch un-deliverable.

### Proof of Concept
1. Attacker calls `EvmHost.dispatch(DispatchPost{ body: <multi-MB bytes>, fee: <minimal>, dest: <victim chain>, ... })` — no revert occurs because `body.length` is unchecked (`evm/src/core/EvmHost.sol` lines 921-959).
2. `PostRequestEvent` is emitted with the oversized `body`; a relayer (or the SDK's self-relay flow) picks up the commitment and constructs a `PostRequestMessage` to submit to the destination chain's `HandlerV2.handlePostRequests`.
3. Inside `handlePostRequests`, `leaf.request.hash()` (`Message.hash` → `keccak256(abi.encode(req))`) is invoked on the full oversized body twice (once for the MMR leaf, once for the duplicate-delivery check), consuming gas that scales with the size of the attacker-controlled body and can approach or exceed the block gas limit — directly analogous to the referenced PoC that measured ~207M gas for a 1MB payload passed into a single `keccak256` call.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-959)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }

        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
        emit PostRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: _msgSender(),
            to: abi.encodePacked(request.to),
            nonce: request.nonce,
            timeoutTimestamp: request.timeoutTimestamp,
            body: request.body,
            fee: post.fee
        });
    }
```

**File:** sdk/packages/core/contracts/libraries/Message.sol (L225-230)
```text
    /**
     * @dev Returns the commitment for the given post request
     */
    function hash(PostRequest memory req) internal pure returns (bytes32) {
        return keccak256(encode(req));
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
