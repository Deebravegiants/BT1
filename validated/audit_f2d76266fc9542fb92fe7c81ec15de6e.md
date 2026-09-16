### Title
Unbounded gas forwarding to attacker-controlled destination module allows griefing of batched `handlePostRequests`/`handleGetResponses` deliveries - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming` for both `PostRequest` and `GetResponse` delivery forwards essentially all remaining transaction gas to an arbitrary, attacker-chosen destination contract via a raw `.call()`, with no gas stipend/cap and no per-call gas isolation (e.g., a fixed `gas:` limit or `try/catch` with bounded gas). `HandlerV2.handlePostRequests` and `handleGetResponses` loop over every leaf in the relayer-submitted batch and invoke `host.dispatchIncoming` for each one in sequence, in the same transaction.

### Finding Description
`dispatchIncoming(PostRequest, address relayer)` resolves the destination module from `request.to` (fully attacker-controlled: any account can dispatch a POST request to any `to` address on the destination chain) and does: [1](#0-0) 

The `.call()` forwards essentially all gas left in the transaction to `destination`. There is no explicit gas cap passed (`.call{gas: X}(...)`), unlike patterns elsewhere in the codebase that isolate untrusted external calls, e.g. the LayerZero endpoint's `onAccept` deliberately isolates the external call with `try/catch` specifically so a malformed/malicious receiver can't propagate a revert/DoS: [2](#0-1) 

`dispatchIncoming` for `GetResponse` has the identical unbounded forwarding pattern: [3](#0-2) 

`HandlerV2.handlePostRequests` and `handleGetResponses` iterate over every leaf in a relayer-submitted batch and call `dispatchIncoming` once per leaf, all within a single transaction and shared gas budget: [4](#0-3) [5](#0-4) 

Any unprivileged user can dispatch a POST request (via `EvmHost.dispatch`, reachable from any account) whose `to` field points at an attacker-deployed contract on the destination chain: [6](#0-5) 

That attacker contract's `onAccept` (or its fallback, since the call target only needs nonzero `extcodesize`) can be written to consume the vast majority of forwarded gas (e.g. an infinite/near-infinite loop bounded only by the gas forwarded). This directly mirrors the reported NFTX bug class: a `.call()` that forwards attacker-controlled gas to an attacker-controlled receiver inside a loop that also has to deliver value/state to *other*, legitimate parties in the same batch.

### Impact Explanation
Because `dispatchIncoming` catches call failure with `success` and does not itself revert the whole `handlePostRequests`/`handleGetResponses` transaction, a single malicious leaf does not automatically brick the entire batch (unlike the raw NFTX case, which reverted the whole `distribute()`), and a failed request/response entry is simply marked retryable (`delete _requestReceipts[commitment]` / `delete _responseReceipts[commitment]`). However, the gas *consumed* by the malicious `to` contract during its execution is not refunded, so a malicious module planted early in a large multi-leaf batch can consume nearly all of the block gas limit / transaction gas, causing all subsequent legitimate requests/responses in the same batch to fail with out-of-gas (also silently marked retryable) or causing the relayer's whole transaction to run out of gas and revert entirely if the griefing contract consumes gas past what's left for outer-loop bookkeeping. This is a denial-of-service on message delivery within a batch: legitimate cross-chain messages (mint/burn instructions, intents fills, relayer fee settlements) bundled with the malicious one fail to deliver and must be resubmitted, at the relayer's gas expense, and can be repeatedly targeted by the same attacker to keep griefing batches that include them. This qualifies as "a route unable to deliver messages" under the validation criteria.

### Likelihood Explanation
Reaching this path requires only: (1) dispatching a POST request from any unprivileged EVM account with `to` set to an attacker-controlled contract deployed on the destination chain — permissionless via `EvmHost.dispatch`; and (2) waiting for/inducing a relayer to batch that request together with other legitimate requests in `handlePostRequests`. Relayers control batch composition and typically deliver requests in bulk for gas efficiency, so an attacker cannot force inclusion in someone else's batch, but can grief the delivery of their own request combined with others whenever relayers batch requests, and can repeatedly submit such requests to degrade batch delivery reliability generally. This does not require any privileged/admin role, matching the allowed unprivileged-relayer/dispatcher threat model.

### Recommendation
Cap the gas forwarded to the destination module in `dispatchIncoming` (both `PostRequest` and `GetResponse` variants) via an explicit `gas:` stipend, sized to accommodate legitimate `onAccept`/`onGetResponse` implementations while bounding worst-case consumption per leaf (analogous to EIP-150 patterns used elsewhere in the codebase, e.g. the LayerZero endpoint's isolated `try/catch` call). This prevents a single malicious destination module from consuming a disproportionate share of the batch's gas budget and protects the delivery of unrelated, legitimately batched requests/responses.

### Proof of Concept
1. Attacker deploys `EvilModule` on the EVM destination chain whose fallback/`onAccept` runs a gas-consuming loop (e.g., `while (true) {}` bounded only by forwarded gas, or repeated `SSTORE`s) sized to burn ~(forwarded gas − 1/64 reserve).
2. Attacker calls `EvmHost.dispatch` on the source chain with `DispatchPost.to = abi.encode(address(EvilModule))`, `dest` = the target EVM chain, and a nominal/zero fee.
3. Once finalized, a relayer batches this request together with N other legitimate pending POST requests and calls `HandlerV2.handlePostRequests` with all N+1 leaves in one `PostRequestMessage`.
4. During the loop in `handlePostRequests`, when `host.dispatchIncoming` reaches the attacker's leaf, the `.call()` forwards remaining gas to `EvilModule`, which consumes nearly all of it.
5. Subsequent iterations of the loop for the legitimate leaves run out of gas mid-execution (or the relayer's whole transaction reverts from out-of-gas depending on remaining headroom), so legitimate requests batched after the attacker's leaf fail to deliver and are left in a retryable state, forcing re-submission and additional relayer gas cost.

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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L384-390)
```text
        // Deliver to the OApp. Isolate the external call so a deterministic revert (zero
        // recipient, over-cap mint, blocklisted recipient, malformed payload, paused OApp, etc.)
        // does not revert `onAccept`. On failure the payload is retained for later retry/recovery
        // via retryPayload/clear/skip/nilify/burn.
        Origin memory origin = Origin({srcEid: srcEid, sender: sender, nonce: nonce});
        try ILayerZeroReceiver(receiverAddr).lzReceive(origin, guid, message, address(0), "") {
            // delivered successfully
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
