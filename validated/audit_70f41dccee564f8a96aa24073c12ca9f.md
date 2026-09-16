Confirmed: no length check exists on `_params.message` in `send()` (lines 262–313), and no `MAX_MESSAGE`/size guard anywhere in the LZ endpoint. This confirms the analog vulnerability.

### Title
Unbounded LZ message body combined with strict sequential inbound nonce enforcement allows permanent DoS of a LayerZero OApp channel via oversized `MsgInitiateTokenDeposit`-style payload - (File: sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol)

### Summary
`HyperbridgeLzEndpoint.send()` accepts an arbitrary-length `_params.message` with no size restriction and embeds it directly into an ISMP `DispatchPost.body`. On the destination chain, `onAccept()` enforces **strict sequential nonce delivery** per `(receiver, srcEid, sender)` lane, rejecting any nonce that isn't exactly `expectedNonce`. If a message body is crafted large enough that the resulting `PostRequest` can never be delivered (its calldata cannot fit within realistic EVM transaction/mempool size or block gas limits when passed through `IHandlerV2.handlePostRequests`/`batchCall`), that nonce can never be consumed, permanently blocking every subsequent message on that channel — mirroring the `OPinit` `MsgFinalizeTokenDeposit` strict-sequence DoS described in the reference report.

### Finding Description
`send()` builds the ISMP body without any bound on `_params.message`: [1](#0-0) 

On the receiving side, `onAccept()` decodes the body and strictly requires `nonce == expectedNonce`, reverting otherwise: [2](#0-1) 

The nonce advance is deliberately decoupled from the inner `lzReceive` call succeeding or reverting (per the `HYPERBR-1939` comment) — but this only protects against `lzReceive` reverting *after* `onAccept` executes. It does **not** protect against `onAccept` (and therefore the enclosing `dispatchIncoming` call) never being invoked at all because the underlying `PostRequest` cannot physically be delivered to the destination chain.

Delivery requires a relayer to submit the request via `IHandlerV2.handlePostRequests` (or `batchCall`), which is a normal EVM transaction subject to node mempool/tx-size limits and block gas limits: [3](#0-2) 

Nowhere in `IDispatcher`/`EvmHost.dispatch(DispatchPost)` is there a bound on `post.body` length: [4](#0-3) 

Unlike the generic ISMP `handlePostRequests` path — where each request is independently keyed by its own commitment hash and a stuck/undeliverable request only affects that single request (no other message depends on it) — the LZ endpoint layers an additional strict-ordering invariant (`_inboundNonce`) on top of Hyperbridge's inherently unordered request delivery model. This re-introduces exactly the sequencing hazard the reference report identified in OPinit's L1→L2 bridge, where one poisoned/oversized message blocks an entire FIFO queue of otherwise-valid messages.

An attacker can call `send()` (it is a public, permissionless entrypoint per `ILayerZeroEndpointV2`) with a payload sized so that the resulting encoded `PostRequest` (guid + eid + sender + nonce + receiver + message) exceeds what any relayer can realistically submit as a single delivery transaction on the destination chain (default node tx-size limits, e.g., ~128KB on go-ethereum, well below the 30M gas block limit), while still being cheap/possible to submit on the source chain (source-side dispatch has no equivalent restrictive limit besides the source chain's own tx size cap, and an attacker can tune the payload size to be just under the source limit but over the destination's practical delivery limit — precisely the asymmetric bypass technique described in the reference report).

### Impact Explanation
Because `_inboundNonce` strictly gates delivery in FIFO order per `(receiver, srcEid, sender)`, one attacker-controlled oversized message permanently freezes that lane: every later legitimate message from that sender to that receiver (e.g., all subsequent bridge transfers through a given OFT) will revert with `InvalidNonce` forever, since the blocking nonce can never be consumed. This is a "route unable to deliver messages" condition affecting any OApp built on this adapter (e.g., OFTs), and during it, users' pending cross-chain transfers are stuck and new transfers cannot complete — a direct availability/funds-lock impact matching the accepted High severity of the analogous OPinit finding.

### Likelihood Explanation
Likelihood is high: `send()` is fully permissionless and unprivileged (any address, or any OApp caller) can invoke it with an oversized `message`; there is no allowlist, size check, or fee-based rate limiting preventing this. The only requirement is being able to afford paying the dispatch fee for a large calldata payload once on the source chain — a one-time, moderate cost compared to the persistent DoS impact of freezing the whole channel.

### Recommendation
Add an explicit maximum length check on `_params.message` in `send()` (and validate the resulting encoded body length against a conservative bound well under standard EVM mempool/tx-size limits) before dispatching. Additionally, consider decoupling the strict per-nonce ordering from delivery success — e.g., allow permissionless "skip" of a nonce (as LayerZero's canonical endpoint supports via `skip`/`nilify` for the *sender*/OApp) so a stuck slot does not require unbounded coordination to unblock, or add a size-based rejection at `onAccept`/dispatch time so an oversized message can never occupy a nonce slot in the first place.

### Proof of Concept
1. Attacker (or any user) calls `HyperbridgeLzEndpoint.send()` with `_params.message` sized just under the source chain's dispatch calldata affordability limit (e.g., several hundred KB), targeting a specific `(receiver, dstEid)`.
2. `send()` assigns the next `_outboundNonce` for `(msg.sender, dstEid, receiver)` and dispatches a `PostRequest` with a very large `body` via `IDispatcher(_host).dispatch()` — no length check rejects it.
3. Relayers/HyperBridge finalize the request, but attempting `handlePostRequests`/`batchCall` on the destination with this oversized request either fails to fit in the local node's default transaction size limits (rejected from mempool) or is prohibitively expensive/impossible to include in a block, so `onAccept` for that nonce is never invoked.
4. `_inboundNonce[receiver][srcEid][sender]` remains stuck one behind `nonce`; every subsequent legitimate message from `sender` to `receiver` reverts with `InvalidNonce(expected, got)` in `onAccept()` at [5](#0-4) , permanently freezing that lane until governance-level intervention (raising node tx-size limits across relayers) occurs.

### Citations

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L262-294)
```text
    function send(
        MessagingParams calldata _params,
        address /* _refundAddress */
    ) external payable override whenNotPaused returns (MessagingReceipt memory) {
        bytes memory dest = _eidToStateMachine[_params.dstEid];
        if (dest.length == 0) revert UnknownEid(_params.dstEid);

        // Track nonce
        uint64 nonce = ++_outboundNonce[msg.sender][_params.dstEid][_params.receiver];

        // Compute globally unique identifier
        bytes32 guid = keccak256(
            abi.encodePacked(nonce, _eid, bytes32(uint256(uint160(msg.sender))), _params.dstEid, _params.receiver)
        );

        // Encode the LZ message into the ISMP body
        bytes memory body = abi.encode(
            guid,
            _eid, // srcEid
            bytes32(uint256(uint160(msg.sender))), // sender
            nonce,
            _params.receiver, // receiver OApp on dest
            _params.message
        );

        DispatchPost memory request = DispatchPost({
            dest: dest,
            to: abi.encodePacked(address(this)),
            body: body,
            timeout: 0,
            fee: relayerFee(_params.dstEid),
            payer: address(this)
        });
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L355-382)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        // Verify source is this adapter on another chain
        if (keccak256(request.from) != keccak256(abi.encodePacked(address(this)))) revert UnknownSource();

        // Decode the LZ message from the ISMP body
        (
            bytes32 guid,
            uint32 srcEid,
            bytes32 sender,
            uint64 nonce,
            bytes32 receiver,
            bytes memory message
        ) = abi.decode(request.body, (bytes32, uint32, bytes32, uint64, bytes32, bytes));

        // Reject `expectedEid == 0` so unconfigured sources don't collide with `srcEid = 0`.
        uint32 expectedEid = _stateMachineToEid[keccak256(request.source)];
        if (expectedEid == 0 || expectedEid != srcEid) revert UnknownSource();

        // Validate and advance the nonce. The nonce is committed BEFORE (and independently of)
        // OApp execution: a reverting `lzReceive` must not roll back this write. Otherwise the
        // message would be retried forever at the same nonce and every later nonce would be
        // permanently rejected, bricking the (receiver, srcEid, sender) channel.
        address receiverAddr = address(uint160(uint256(receiver)));
        uint64 expectedNonce = _inboundNonce[receiverAddr][srcEid][sender] + 1;
        if (nonce != expectedNonce) revert InvalidNonce(expectedNonce, nonce);
        _inboundNonce[receiverAddr][srcEid][sender] = nonce;
```

**File:** evm/src/core/HandlerV2.sol (L181-209)
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
```

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
