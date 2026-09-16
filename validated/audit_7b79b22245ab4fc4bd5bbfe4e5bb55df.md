### Title
Unbounded gas forwarding to untrusted `onAccept`/`onGetResponse`/timeout callbacks allows a malicious destination module to grief relayers and block batched message delivery - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming` and the timeout dispatch functions invoke the destination application's callback (`IApp.onAccept`, `onGetResponse`, `onGetTimeout`, `onPostRequestTimeout`) via a raw `.call(...)` with no gas stipend, forwarding all gas remaining in the transaction. Because the destination address is fully attacker-controlled (any contract can be registered as a module `to`/`from` in a request), a malicious module can implement its callback to consume attacker-chosen amounts of gas, up to the entire block gas limit. This is the same "gas bomb" pattern flagged in the external report for `SablierV2Lockup`'s recipient/sender callbacks, but here it is reachable by any unprivileged relayer delivering permissionless messages.

### Finding Description
`HandlerV2.handlePostRequests` verifies a batch proof and then, for every request in the batch, calls `host.dispatchIncoming(leaf.request, _msgSender())` in a loop: [1](#0-0) 

`EvmHost.dispatchIncoming` performs the actual delivery with an unbounded, gas-unlimited low-level call: [2](#0-1) 

The same pattern (raw `.call(...)` forwarding all remaining gas, no try/catch gas cap) is repeated for GET responses and both timeout paths: [3](#0-2) [4](#0-3) 

None of these calls specify a `gas:` stipend, and a `grep` for gas-limiting logic (`gasleft`, `gas:`, `GasLimit`) in `evm/src/**` returns no results outside an unrelated paymaster contract, confirming there is no gas cap on any of these external module calls.

Any address can be encoded as the `to` field of a `PostRequest` (or `from` of a response/timeout), and `dispatchIncoming` only checks that the destination has code (`extcodesize`), not that it is a "safe" or registered application: [5](#0-4) 

An attacker can therefore deploy a contract implementing `onAccept`/`onGetResponse`/etc. that intentionally burns gas (e.g., an unbounded loop or deep recursive `SSTORE`s) up to whatever gas is left in the relayer's transaction. Because `handlePostRequests`/`handleGetResponses` process an entire batch of unrelated requests inside one transaction and one `for` loop, a single malicious destination anywhere in the batch can exhaust the relayer's gas, causing the *whole transaction* — including all other legitimate, unrelated requests bundled with it — to revert with out-of-gas. This mirrors the report's core class ("recipient" deliberately consuming excess gas to hinder the "sender"'s action), except the impacted party here is the permissionless relayer/message dispatcher rather than a stream sender, and the blast radius extends to every other request batched in the same delivery transaction.

### Impact Explanation
- Relayers face unpredictable, attacker-inflated gas costs when delivering to a malicious module, or their transaction reverts outright with out-of-gas, wasting gas fees paid to prepare the batch.
- Because `handlePostRequests`/`handleGetResponses` batch multiple independent requests per transaction, one malicious/compromised destination module can block delivery of other legitimate, unrelated requests batched alongside it, effectively making the delivery route unable to deliver those messages until the relayer learns to isolate the poisoned request (increasing operational cost and delaying cross-chain messages/tokens/intents that depend on timely delivery).
- This can be weaponized against fee-sensitive relayers to discourage them from including certain requests, or against the protocol generally as a low-cost, repeatable DoS/griefing vector on message delivery throughput.

### Likelihood Explanation
Any user can permissionlessly dispatch a POST request whose destination module is an arbitrary contract they deploy (subject to the normal ISMP dispatch flow), and relayers process these deliveries without built-in protection against gas griefing since `dispatchIncoming` forwards unlimited gas. No special privilege is required — this is reachable by a single unprivileged sender submitting a request that will later be relayed in a batch with other requests.

### Recommendation
Forward a bounded, explicit gas stipend to `IApp` callbacks in `dispatchIncoming` and the timeout dispatch functions (e.g., `destination.call{gas: gasLimit}(...)`), with `gasLimit` either a protocol-configurable parameter or a fraction of `gasleft()`, consistent with the Sablier team's acknowledged mitigation direction. Additionally, consider processing each request's dispatch with isolated gas accounting (already true per-call via a cap) so that one malicious module cannot cause the entire batch transaction to run out of gas and revert.

### Proof of Concept
1. Attacker deploys `EvilApp` implementing `onAccept(IncomingPostRequest calldata)` that runs an unbounded loop (e.g., repeated `SSTORE`s) to consume as much gas as is supplied.
2. Attacker dispatches a `PostRequest` addressed to `EvilApp` through the normal dispatch path (e.g., `EvmHost.dispatch`), which requires no special privilege.
3. A relayer batches this request together with N other unrelated pending requests and calls `HandlerV2.handlePostRequests`.
4. Inside the loop, `host.dispatchIncoming` for the `EvilApp` request executes `destination.call(...)` with all remaining gas; `EvilApp.onAccept` consumes it all, causing the entire `handlePostRequests` transaction — including the other N legitimate requests — to run out of gas and revert, per [6](#0-5)  and [1](#0-0) .

### Citations

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

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
