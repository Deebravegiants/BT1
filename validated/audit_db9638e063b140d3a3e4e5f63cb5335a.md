### Title
Unvalidated zero-length request body causes out-of-bounds revert in intent/paymaster `onAccept`, permanently bricking message delivery and freezing escrowed relayer fees - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`EvmHost.dispatch` lets any account submit a `PostRequest` to Hyperbridge with an arbitrary, attacker-controlled `body` of any length, including zero [1](#0-0) . Once relayed, `EvmHost.dispatchIncoming` low-level `.call`s the destination module's `onAccept` [2](#0-1) . Several `IApp` implementations — `ExtrinsicIntents.onAccept`, `SimplexPaymaster.onAccept`, and the Tron `IntentGatewayV2.onAccept` — read the very first byte of the body to select a `RequestKind` *before* any authentication or length check: `RequestKind kind = RequestKind(uint8(incoming.request.body[0]));` [3](#0-2) [4](#0-3) [5](#0-4) . This mirrors the reported bug class: unvalidated, attacker-supplied payload data (analogous to Mattermost's unvalidated `RetrospectivePost` props) is parsed before any input validation, causing a crash/DoS instead of a clean rejection.

### Finding Description
`_authenticate`/`_checkRelayer` gates run only *after* `body[0]` is indexed [3](#0-2) ; there is no `body.length != 0` (or minimum-length) check anywhere in these `onAccept` implementations, and none exists in `EvmHost.dispatch`/`dispatchIncoming` either — `body` is forwarded verbatim from the dispatcher [6](#0-5) . In Solidity, indexing a zero-length `bytes calldata` at index 0 reverts with an array-out-of-bounds panic. `dispatchIncoming` treats any revert from the callback as a soft failure — it deletes the request receipt and returns without reverting the batch [7](#0-6)  — so the transaction as a whole succeeds, but the message can *never* be delivered: its commitment/content is fixed once submitted to Hyperbridge, so resubmitting the same request will fail identically every time.

Because the destination address for a Hyperbridge POST request (`to`) is fully attacker-controlled and any account can call `dispatch()`, an unprivileged message dispatcher on any connected chain can address a zero-length-body `PostRequest` at these known gateway/paymaster contracts, permanently jamming that specific message.

### Impact Explanation
- The route to the affected module is permanently unable to deliver that message ("route unable to deliver messages"), since the destination callback will always revert on `body[0]` for that fixed, already-committed request.
- If the request was dispatched with `timeout == 0` (no expiry — an explicitly supported option per `dispatch`'s `timeoutTimestamp = post.timeout == 0 ? 0 : ...` [8](#0-7) ), any relayer fee escrowed in `_requestCommitments` for that request can never be refunded via `onPostRequestTimeout` and never be paid out via successful delivery, resulting in permanent freezing of those escrowed funds.
- The affected module (`ExtrinsicIntents`/`SimplexPaymaster`/tron `IntentGatewayV2`) is left with a permanently stuck, undeliverable request occupying its request-receipt/commitment bookkeeping.

### Likelihood Explanation
Trivial and cheap to trigger: any account can call `IDispatcher(host).dispatch(DispatchPost{...})` with `body: ""` and `to` set to the target module's address, requiring only the (optional) relayer fee. No special privileges, proofs, or governance access are needed — this is reachable from a single submitted transaction by any unprivileged dispatcher, matching the required threat model.

### Recommendation
In every `onAccept`/`onPostRequestTimeout` implementation that indexes into `request.body`, validate `request.body.length != 0` (and any subsequent minimum-length requirements for `abi.decode(body[1:], ...)`) before reading `body[0]`, reverting with a clear, typed error (e.g., `InvalidBody()`) instead of relying on the implicit out-of-bounds panic. Apply this to `ExtrinsicIntents.onAccept`, `SimplexPaymaster.onAccept`, and `IntentGatewayV2.onAccept` (both the main and Tron variants), and audit other `IApp` implementations for the same pattern.

### Proof of Concept
1. Attacker (any EOA) calls `EvmHost.dispatch(DispatchPost{ dest: <chain of ExtrinsicIntents>, to: abi.encodePacked(extrinsicIntentsAddress), body: "", timeout: 0, fee: 0, payer: attacker })` [1](#0-0) .
2. A relayer picks up the committed `PostRequest` and delivers it through `HandlerV2.handlePostRequests`, which calls `host.dispatchIncoming(leaf.request, relayer)` [9](#0-8) .
3. `EvmHost.dispatchIncoming` low-level-calls `ExtrinsicIntents.onAccept(IncomingPostRequest(request, relayer))` [10](#0-9) .
4. Inside `onAccept`, `RequestKind(uint8(incoming.request.body[0]))` reverts with an array-out-of-bounds panic because `body.length == 0` [11](#0-10) .
5. `dispatchIncoming` catches the revert (`success == false`), deletes the request receipt, and returns normally — the outer relayer transaction succeeds, but the request commitment is now permanently stuck: any resubmission decodes the same fixed empty body and reverts identically forever [12](#0-11) .

Note: I could not execute this against a live/forked environment (no filesystem/terminal access in this mode) to confirm the exact panic behavior end-to-end; the analysis is based on static reading of the Solidity semantics for indexing empty `bytes calldata` and the surrounding dispatch/dispatchIncoming/onAccept control flow shown above. A Devin session with repo and toolchain access could add a Foundry test (e.g., extending `evm/tests/foundry/IntentGatewayV2Test.sol`) to confirm the revert and the permanently-stuck commitment.

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

**File:** evm/src/core/EvmHost.sol (L921-944)
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
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L313-320)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) {
            revert UnauthorizedCall();
        }

        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        bytes calldata payload = incoming.request.body[1:];
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
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
