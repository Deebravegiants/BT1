## Analysis

The Apple CVE describes a **use-after-free**: a value is freed but a stale reference to it is later dereferenced by another code path, causing incorrect/unsafe behavior. The closest reachable analog in Hyperbridge is a **stale storage-commitment reuse bug in `EvmHost`**: the fee metadata backing an outgoing GET request (`_requestCommitments[commitment]`) is never cleared once "consumed" by a successful response delivery, so the timeout path can later "use" that same freed/consumed record to pay out the relayer fee a second time.

### Title
Stale `_requestCommitments` entry after successful GET response delivery enables double relayer-fee payout - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse, ...)` pays the relayer fee out of `_requestCommitments[commitment].fee` on a successful response delivery but never deletes that mapping entry [1](#0-0) . Every sibling consumer of the same mapping (`dispatchTimeOut` for both GET and POST timeouts) does delete the entry before paying out, precisely to prevent reuse [2](#0-1) . Because the GET-response success path is the odd one out, the commitment metadata (`sender`, `fee`) remains "alive" in storage after it has already been logically consumed, exactly like a freed object whose dangling pointer is later dereferenced.

### Finding Description
- `dispatch(DispatchGet)` records `_requestCommitments[commitment] = FeeMetadata({sender, fee})` when a GET request is sent from this host [3](#0-2) .
- When the response is relayed back, `HandlerV2.handleGetResponses` verifies the response proof and calls `host.dispatchIncoming(leaf.response, _msgSender())`, guarded only by a **response**-receipt duplicate check (`responseReceipts`), not by any check on `_requestCommitments` [4](#0-3) .
- `dispatchIncoming(GetResponse,...)` sets `_responseReceipts[commitment]`, invokes `onGetResponse` on the destination app, and on success pays the relayer from `_requestCommitments[commitment].fee` — **without deleting `_requestCommitments[commitment]`** [5](#0-4) .
- Later, `HandlerV2.handleGetRequestTimeouts` reads `meta = host.requestCommitments(commitment)`, and — because `meta.sender` was never cleared — treats the already-answered request as still pending, then calls `host.dispatchTimeOut(GetRequestTimeout(...), meta, commitment)` as long as a non-membership proof for the response receipt can be produced for *some* stored height [6](#0-5) .
- `dispatchTimeOut(GetRequestTimeout,...)` deletes `_requestCommitments[commitment]` and refunds `meta.fee` to `meta.sender` a **second time**, or invokes `onGetTimeout` on the app a second time for an already-fulfilled request [7](#0-6) .

The root cause is that the "freed" (already-spent) fee-metadata record is not invalidated after being consumed by the response path, so a second, unrelated consumer (the timeout path) can dereference and reuse it — the same class of bug as a use-after-free.

### Impact Explanation
This allows theft of `feeToken` funds held by `EvmHost`: the same relayer fee tied to a single GET request commitment can be paid out twice — once via normal response delivery and once via a timeout claim against a stale/earlier accepted state commitment height where the response receipt had not yet been written. This directly drains protocol-held fee reserves that back other users' pending requests, a concrete theft/loss of funds reachable by any relayer or unprivileged party who can submit a valid (but stale-height) non-membership proof through the permissionless `handle_unsigned`/`handleGetRequestTimeouts` paths.

### Likelihood Explanation
Both `handleGetResponses` and `handleGetRequestTimeouts` are permissionless entry points reachable directly from `HandlerV2`, callable by anyone with a valid proof [8](#0-7) . The host retains state commitments per historical height (`stateMachineCommitment(height)`) rather than only the latest, so an attacker only needs one accepted height at which the response-receipt trie entry was not yet present to construct a valid non-membership proof, which is realistic given ordinary relaying/timeout races.

### Recommendation
Delete `_requestCommitments[commitment]` in `dispatchIncoming(GetResponse memory response, address relayer)` immediately after a successful `onGetResponse` call (mirroring the existing pattern in `dispatchTimeOut`), so the fee metadata cannot be dereferenced again by the timeout path once the response has been delivered.

### Proof of Concept
1. Dispatch a `DispatchGet` request from `EvmHost`, recording `_requestCommitments[c] = {sender, fee}` [3](#0-2) .
2. Relay a valid `GetResponseMessage` for it through `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse,...)`; `onGetResponse` succeeds and the relayer is paid `fee`, but `_requestCommitments[c]` remains unchanged [5](#0-4) .
3. Submit a `GetTimeoutMessage` for the same request referencing an earlier accepted state-machine height whose trie proof shows non-membership of the response receipt (predates the response's inclusion) through `HandlerV2.handleGetRequestTimeouts` [6](#0-5) .
4. `EvmHost.dispatchTimeOut` finds `meta.sender != 0`, deletes the entry, and pays `meta.fee` again to `meta.sender` (or replays `onGetTimeout` on the app), completing a double payout of the same fee [9](#0-8) .

### Citations

**File:** evm/src/core/EvmHost.sol (L820-847)
```text
    /**
     * @dev Dispatch an incoming GET response to source module
     * @param response - get response
     */
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

**File:** evm/src/core/EvmHost.sol (L849-906)
```text
    /**
     * @dev Dispatch an incoming GET timeout to the source module.
     * @notice Does not refund any protocol fees.
     * @param timeout - timed-out get request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
    function dispatchTimeOut(
        GetRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }

    /**
     * @dev Dispatch an incoming POST timeout to the source module
     * @param timeout - timed-out post request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
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

**File:** evm/src/core/EvmHost.sol (L974-1013)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }

        uint64 timeoutTimestamp = get.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(get.timeout);
        GetRequest memory request = GetRequest({
            source: host(),
            dest: get.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            timeoutTimestamp: timeoutTimestamp,
            keys: get.keys,
            height: get.height,
            context: get.context
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
        emit GetRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: request.from,
            keys: request.keys,
            nonce: request.nonce,
            height: request.height,
            context: request.context,
            timeoutTimestamp: request.timeoutTimestamp,
            fee: get.fee
        });
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

**File:** evm/src/core/HandlerV2.sol (L293-321)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            GetRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            bytes32 commitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(commitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(RESPONSE_RECEIPTS_STORAGE_PREFIX, commitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(GetRequestTimeout(request, _msgSender()), meta, commitment);
        }
    }
```
