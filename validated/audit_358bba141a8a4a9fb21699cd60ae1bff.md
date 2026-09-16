### Title
Missing validation of `DispatchPost.to` length at dispatch time reverts and blocks entire batched message deliveries - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost memory post)` accepts an arbitrary-length `post.to` field with no validation and stores it verbatim into the committed `PostRequest`. On the destination chain, `HandlerV2.handlePostRequests` calls `host.dispatchIncoming(leaf.request, relayer)` as a *direct* external call (not a low-level `.call` wrapped in a try/success check). Inside `dispatchIncoming`, the very first operation is `_bytesToAddress(request.to)`, which reverts with `InvalidAddressLength` if `request.to.length != 20`. Because this call is unprotected, a single malformed request anywhere in a relayed batch reverts the *entire* `handlePostRequests` transaction, blocking delivery of every other (legitimate) request batched alongside it.

### Finding Description
`dispatch(DispatchPost memory post)` in `evm/src/core/EvmHost.sol` performs no validation on `post.to` before committing/emitting the request: [1](#0-0) 

The `to` bytes are propagated unchanged into the `PostRequest.to` field and emitted in `PostRequestEvent`, with no length check enforced at dispatch time.

On the receiving side, `HandlerV2.handlePostRequests` verifies the MMR proof for the whole batch and then, in a loop, calls `host.dispatchIncoming(leaf.request, _msgSender())` directly for every request in the batch: [2](#0-1) 

`EvmHost.dispatchIncoming` immediately calls `_bytesToAddress(request.to)`: [3](#0-2) 

and `_bytesToAddress` explicitly reverts when the byte length isn't exactly 20: [4](#0-3) 

Unlike the subsequent `onAccept` invocation—which is wrapped in a low-level `.call` with an explicit `success` check so that a failing app callback doesn't revert the whole batch (comment: "instead of reverting the entire batch, early return here")—the `_bytesToAddress` conversion is *not* protected. Since `dispatchIncoming` itself is called as a normal (not low-level) external call from `handlePostRequests`, any revert inside it propagates all the way up and reverts the whole `handlePostRequests` transaction, undoing delivery of every other request batched in that same call.

Because `post.to` is fully attacker-controlled input from any application/EOA that calls `dispatch`, an attacker can dispatch a POST request with a `to` field of any length other than 20 bytes (e.g., 0, 1, 32 bytes). Once this malformed request becomes finalized on Hyperbridge and is grouped by a relayer into a batch with other, unrelated legitimate requests (batching is the normal/expected behavior for `handlePostRequests`, and the interface documentation explicitly supports batching many requests in one MMR-proof call), the resulting `handlePostRequests` call reverts entirely, and none of the batched requests are delivered.

### Impact Explanation
This directly matches the "route unable to deliver messages" impact class explicitly in scope: a single unsanitized `to` field poisons an entire relayed batch, causing legitimate cross-chain messages (token transfers, governance updates, app calls) bundled with it to fail delivery. Relayers must then discover the poisoned commitment out-of-band and manually exclude it from every future batch attempt, and any messages with a timeout can be timed out or delayed by this griefing, degrading protocol liveness and reliability of the messaging bridge for arbitrary third parties whose requests happen to be batched together. This is a systemic denial-of-service on the dispatch/delivery path, reachable from a single unprivileged `dispatch()` call.

### Likelihood Explanation
Likelihood is high: `dispatch(DispatchPost)` is a fully permissionless, unprivileged entry point on `EvmHost`, requiring no special role — any contract or EOA that can pay the (optional) relayer fee can call it. Crafting a `to` value of the wrong byte length costs nothing extra beyond the normal dispatch fee. The only variable is whether/when a relayer happens to batch it with other requests, but batching multiple pending requests together for gas efficiency is the very use case `handlePostRequests`/`PostRequestMessage`/`MerkleMountainRange.VerifyProof` batch verification is designed for, so this scenario is a normal and expected relayer optimization, not a contrived edge case.

### Recommendation
Validate `post.to.length == 20` (or the appropriate destination-address encoding length) inside `EvmHost.dispatch(DispatchPost memory post)` before committing/emitting the request, with a clear revert reason (e.g., `InvalidAddressLength`), so malformed requests can never be committed in the first place. Alternatively/additionally, make `dispatchIncoming`'s handling of `_bytesToAddress` failure non-fatal to the batch (e.g., wrap the address decode in a try/catch equivalent or pre-validate length and `return` early like the zero-`extcodesize` case) so that one malformed request cannot revert delivery of the rest of a batch.

### Proof of Concept
1. Attacker calls `EvmHost.dispatch(DispatchPost({dest: <validChain>, to: hex"1234" /* 2 bytes, not 20 */, body: ..., timeout: 0, fee: 0, payer: attacker}))` on the source chain. The call succeeds because no length check exists (see `evm/src/core/EvmHost.sol:921-959`).
2. This request is picked up by Hyperbridge, finalized, and a relayer later builds a `PostRequestMessage` batch that includes this malformed request together with N other legitimate, unrelated pending requests destined for the same chain (normal batching behavior supported by `PostRequestLeaf[]` in `handlePostRequests`).
3. Relayer submits `HandlerV2.handlePostRequests(host, batch)`. The MMR proof verifies successfully (the malformed request is a legitimately committed leaf). The loop reaches `host.dispatchIncoming(leaf.request, relayer)` for the malformed leaf (`evm/src/core/HandlerV2.sol:204-209`).
4. `dispatchIncoming` calls `_bytesToAddress(request.to)` on the 2-byte `to` value, which reverts with `InvalidAddressLength` (`evm/src/core/EvmHost.sol:794-795`, `evm/src/core/EvmHost.sol:1071-1077`).
5. Because `dispatchIncoming` is invoked as a direct external call (not `.call` with a success check), the revert bubbles up through `handlePostRequests`, reverting the entire transaction — none of the N legitimate requests in the batch are delivered, even though their proofs were valid and they were not malformed.

### Citations

**File:** evm/src/core/EvmHost.sol (L794-803)
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

**File:** evm/src/core/EvmHost.sol (L1066-1077)
```text
    /**
     * @dev Converts bytes to address.
     * @param _bytes bytes value to be converted
     * @return addr returns the address
     */
    function _bytesToAddress(bytes memory _bytes) internal pure returns (address addr) {
        if (_bytes.length != 20) revert InvalidAddressLength();

        assembly {
            addr := mload(add(_bytes, 20))
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```
