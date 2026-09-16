Confirmed: `to` in `DispatchPost` is fully attacker-controlled arbitrary bytes/address, requiring no registration or permission — anyone dispatching a POST request picks their own destination contract as `to`, and that same attacker can deploy a malicious contract there. This confirms the analog is reachable by an unprivileged, arbitrary transaction.

### Title
Unbounded gas forwarding in `EvmHost::dispatchIncoming`/`dispatchTimeOut` low-level calls lets a malicious `to` module grief batched message delivery - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming` (for both `PostRequest` and `GetResponse`) and `EvmHost.dispatchTimeOut` (for both `GetRequestTimeout` and `PostRequestTimeout`) invoke the destination application via a raw `.call(...)` with no gas cap, forwarding effectively all remaining transaction gas (Solidity's default 63/64 forwarding rule). Since the `to`/`from` address of a dispatched request is fully attacker-controlled (`DispatchPost.to` is arbitrary `bytes`, requiring no registration), an attacker can deploy a gas-guzzling contract as the destination and dispatch a request to it. When a relayer's `HandlerV2.handlePostRequests`/`handleGetResponses` (which loop over every leaf in the batch, calling `host.dispatchIncoming` per leaf) processes this malicious request together with other unrelated legitimate requests in the same MMR-proof batch (or inside `IHandlerV2.batchCall`), the malicious callee can consume nearly all forwarded gas, starving or reverting the processing of every other request bundled in that transaction.

### Finding Description
`EvmHost.dispatchIncoming(PostRequest memory request, address relayer)` marks the request as received and then does:
```solidity
(bool success,) = address(destination)
    .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));
``` [1](#0-0) 
No gas value is supplied to `.call`, so up to 63/64 of all gas remaining at that call-site is forwarded to `destination`. The same unbounded pattern is used for GET responses and both timeout paths: [2](#0-1) [3](#0-2) 

`destination`/`to` is fully attacker-controlled: `DispatchPost.to` is an arbitrary `bytes` field with no allow-listing, set by whoever dispatches the request: [4](#0-3) 

Crucially, `HandlerV2.handlePostRequests` and `handleGetResponses` iterate over an entire batch of leaves proven via a single MMR multiproof and call `host.dispatchIncoming` once per leaf, inside the same transaction: [5](#0-4) [6](#0-5) 

An attacker deploys a contract implementing `IApp.onAccept` (or `onGetResponse`/`onPostRequestTimeout`) that busy-loops until it exhausts all forwarded gas, then dispatches a cheap, low/zero-fee `PostRequest` addressed to that contract. A relayer batching this request together with several profitable, unrelated legitimate requests (standard behavior to amortize gas, e.g. `submit_batch_messages` / `batchCall`) will have the malicious callee consume almost the entire gas budget of the transaction. Because `dispatchIncoming`'s own bookkeeping (`delete _requestReceipts[commitment]`) and the encompassing `for` loop in `handlePostRequests` need gas to complete, the near-total gas exhaustion inside the malicious callee's frame propagates an out-of-gas failure up through the loop/`batchCall`, reverting delivery of every other request batched alongside it. This forces relayers to resubmit (paying gas again with no guarantee the attacker doesn't repeat the same trick), degrading delivery reliability/economics for the whole route — directly analogous to the `L2MigrationDeployer::callMetadataRenderer()` unbounded external call reported in the referenced audit.

### Impact Explanation
This is a resource-exhaustion/griefing vector reachable by any unprivileged account dispatching a single cheap POST request. It can repeatedly cause legitimate, fee-paying requests batched alongside the malicious one to fail delivery, forcing relayer resubmission and degrading throughput/economics of the messaging route — a denial-of-service on message delivery rather than direct fund loss, but it can be used to systematically block or delay delivery of specific batches, undermining route liveness guarantees.

### Likelihood Explanation
Likelihood is high: no privileged role, staking, or governance action is required. An attacker only needs to deploy a trivial gas-burning contract on the destination chain and dispatch one low-cost POST request to it, then repeat as batches are formed by relayers. Relayers routinely batch multiple requests into a single `handlePostRequests`/`batchCall` transaction for gas efficiency, making the "many legit requests behind one malicious one" scenario the normal operating condition rather than an edge case.

### Recommendation
Cap the gas forwarded to destination applications in `EvmHost.dispatchIncoming` and `EvmHost.dispatchTimeOut` (e.g. `destination.call{gas: MODULE_CALL_GAS_LIMIT}(...)`), and treat an out-of-gas failure in the callee identically to any other application revert (mark undelivered/retryable) without letting it consume gas beyond a bounded ceiling. This mirrors the original report's recommendation of bounding gas for the `metadata.call(_data)` in `L2MigrationDeployer::callMetadataRenderer()`.

### Proof of Concept
1. Deploy `MaliciousApp` implementing `IApp`, whose `onAccept` runs `while(true){}` (or an unbounded loop that reverts only via OOG).
2. From `MaliciousApp`'s chain, dispatch a `DispatchPost` with `to = abi.encodePacked(address(MaliciousApp))`, `fee = 0`, and any `body`.
3. Wait for a relayer to include this request's `PostRequestLeaf` in the same `PostRequestMessage.requests[]` batch as several other legitimate, fee-paying requests (or craft/submit such a combined `handlePostRequests`/`batchCall` transaction directly as a self-relayer, per the SDK's self-relay tooling).
4. Observe that `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` for the malicious leaf consumes nearly all gas forwarded via the unbounded `.call`, and the transaction reverts (or the loop for subsequent leaves runs out of gas), so none of the batched legitimate requests are delivered; repeat to grief future batches.

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

**File:** evm/src/core/EvmHost.sol (L856-906)
```text
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

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L23-42)
```text
struct DispatchPost {
    /// @notice Destination chain identifier (e.g., "POLKADOT-1000", "EVM-1")
    /// @dev Must be a valid state machine identifier recognized by the protocol
    bytes dest;
    /// @notice Destination application address or identifier
    /// @dev The receiving application on the destination chain
    bytes to;
    /// @notice The request payload
    /// @dev Arbitrary bytes that will be delivered to the destination application
    bytes body;
    /// @notice Timeout duration in seconds from the current timestamp
    /// @dev Request will be considered timed out after this duration
    uint64 timeout;
    /// @notice Fee paid to relayers for delivery & execution
    /// @dev Paid in the fee token specified by IHost.feeToken()
    uint256 fee;
    /// @notice Account responsible for paying the fees
    /// @dev If different from msg.sender, must have approved the Host contract
    address payer;
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

**File:** evm/src/core/HandlerV2.sol (L241-246)
```text
        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
```
