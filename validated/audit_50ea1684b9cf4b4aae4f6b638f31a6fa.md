## Title
Blacklisted fee payer/relayer can force reversion of an entire batched timeout/GET-response delivery, blocking unrelated message delivery — (`evm/src/core/EvmHost.sol`, `evm/src/core/HandlerV2.sol`)

### Summary
`EvmHost.dispatchTimeOut` (both the `GetRequestTimeout` and `PostRequestTimeout` overloads) and `EvmHost.dispatchIncoming(GetResponse, ...)` perform an unguarded `IERC20(feeToken()).safeTransfer(...)` to the request's original fee payer or to the delivering relayer. These functions are invoked directly (without `try/catch` or low-level `.call`/success-check wrapping) inside `HandlerV2`'s batch-processing loops. If the fee token supports blacklisting (e.g. USDC/USDT, which the docs explicitly recommend as the `feeToken`), a single blacklisted fee-payer or relayer address included anywhere in a submitted batch causes the fee transfer to revert, which reverts the *entire* handler transaction — including delivery of every other, unrelated timeout/response bundled in that same call.

### Finding Description
`HandlerV2.handlePostRequestTimeouts` and `HandlerV2.handleGetRequestTimeouts` iterate over an array of timeouts and call `host.dispatchTimeOut(...)` directly for each one: [1](#0-0) [2](#0-1) 

`EvmHost.dispatchTimeOut` refunds the relayer fee to `meta.sender` (the account that originally paid for/dispatched the request) with a direct `safeTransfer`, after a successful `onPostRequestTimeout`/`onGetTimeout` callback: [3](#0-2) [4](#0-3) 

Similarly, `HandlerV2.handleGetResponses` calls `host.dispatchIncoming(leaf.response, _msgSender())` directly in a loop: [5](#0-4) 

and `EvmHost.dispatchIncoming(GetResponse, ...)` rewards the relayer fee via an unguarded `safeTransfer(relayer, fee)` after the destination module callback succeeds: [6](#0-5) 

None of these three call sites is wrapped with a try/catch or low-level `.call` with a success check the way the module callback itself is (contrast with `dispatchIncoming(PostRequest, ...)`, which does swallow module-callback failures via `.call`/`success`, at [7](#0-6) ). Because Solidity reverts unwind the entire call stack of a transaction unless explicitly caught, a revert in any single iteration's `safeTransfer` (e.g. because the recipient is blacklisted by USDC/USDT) reverts the whole `handlePostRequestTimeouts`/`handleGetRequestTimeouts`/`handleGetResponses` transaction — undoing delivery of every unrelated timeout/response batched alongside it.

This is the same bug class as the referenced report: a third party (here, the original request's fee payer, or the relayer itself) being blacklisted on the fee token blocks a shared/batched operation that other, uninvolved parties depend on to receive their funds/messages.

### Impact Explanation
Any relayer that batches multiple pending timeouts or GET responses into a single `handlePostRequestTimeouts`/`handleGetRequestTimeouts`/`handleGetResponses` call is exposed to a single poisoned entry (a blacklisted `meta.sender` fee payer or a blacklisted relayer address) causing the entire batch to revert. This:
- Prevents timely delivery of unrelated apps' timeout notifications and GET responses (funds/state releases gated on `onPostRequestTimeout`/`onGetTimeout`/`onGetResponse` are delayed indefinitely as long as batching includes the poisoned request).
- Can be weaponized by any user: dispatch a request (or otherwise become the fee payer of one), get blacklisted by the fee-token issuer (a self-inflicted, permissionless action such as interacting with a sanctioned contract), then ensure that request times out — any relayer who bundles that timeout with others will have their batch permanently fail, degrading the reliability/throughput of the messaging route (falls under "route unable to deliver messages").
- For the relayer-fee case (`dispatchIncoming(GetResponse,...)`), a relayer that becomes blacklisted on the fee token can never again have any of its batched GET-response deliveries succeed, even for otherwise-valid, unrelated requests bundled together.

### Likelihood Explanation
The `feeToken` is host-configured and, per project documentation, DAI/USDC-style ERC-20 stablecoins are the expected choice for EVM hosts. Any of these tokens with blacklist functionality (USDC/USDT) makes this reachable by an ordinary unprivileged actor: dispatch a request, pay the relayer fee in the blacklist-capable fee token, get the payer address blacklisted, let the request time out. No special privileges are required beyond submitting a normal ISMP request and having (or causing) the sender/relayer address to end up on the token issuer's blacklist.

### Recommendation
Wrap the relayer/fee-payer reward transfers in `EvmHost.dispatchTimeOut` (both overloads) and `EvmHost.dispatchIncoming(GetResponse, ...)` in a try/catch (or low-level `.call`) so that a failed transfer does not revert the entire batch; instead, credit the amount to an internal withdrawable balance for the intended recipient (pull-payment pattern), consistent with how module-callback failures are already isolated via `.call`/`success` in `dispatchIncoming(PostRequest, ...)`.

### Citations

**File:** evm/src/core/HandlerV2.sol (L241-246)
```text
        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
```

**File:** evm/src/core/HandlerV2.sol (L267-285)
```text
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
```

**File:** evm/src/core/HandlerV2.sol (L303-320)
```text
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
```

**File:** evm/src/core/EvmHost.sol (L809-817)
```text
        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
```

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

**File:** evm/src/core/EvmHost.sol (L849-877)
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
```

**File:** evm/src/core/EvmHost.sol (L885-905)
```text
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
```
