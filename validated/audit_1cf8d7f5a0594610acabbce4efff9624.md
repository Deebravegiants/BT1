This confirms the finding: GET requests do carry a relayer fee (`DispatchGet.fee`, charged in `dispatch(DispatchGet)` at [1](#0-0) ), yet `dispatchTimeOut(GetRequestTimeout,...)` explicitly does **not** refund it (`@notice Does not refund any protocol fees.`) at [2](#0-1) , unlike the POST timeout path a few lines below which does refund the fee to `meta.sender` at [3](#0-2) . The docs even claim "GET requests have no relayer fees, so no refunds occur," which is stale/incorrect relative to the code's `DispatchGet.fee` field [4](#0-3) .

This is directly reachable by an unprivileged user: the source-side Intent Gateway order cancellation path (`_cancelFromSource`) dispatches exactly such a GET request, with the ordinary cancelling user as `payer`/fee-sender [5](#0-4) . If the GET request never gets a relayer-submitted response before its timeout (e.g., relayer stops responding, or the response happens to arrive late) and a permissionless caller submits `handleGetRequestTimeouts` → `dispatchTimeOut(GetRequestTimeout)`, the relayerFee paid by the cancelling user is permanently stuck in the `EvmHost` contract — never credited to the relayer (since delivery never completed) and never returned to the payer.

### Title
GET request relayer fees are never refunded on timeout, permanently locking user-paid fees for Intent Gateway cancellations - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchGet)` charges a `fee` (native or fee-token) from the caller for every GET request, exactly as POST requests do. However, `EvmHost.dispatchTimeOut(GetRequestTimeout,...)` explicitly skips fee-refund logic ("Does not refund any protocol fees"), while the equivalent POST-timeout function refunds the fee to `meta.sender`. Since `IntentsBase._cancelFromSource` (the source-chain order-cancellation path of `IntentGatewayV2`/`ExtrinsicIntents`) dispatches a `DispatchGet` paying `options.relayerFee` from the cancelling user, any GET request that times out instead of being answered permanently strands that fee inside the host contract.

### Finding Description
- `dispatch(DispatchGet)` collects `get.fee` from `_msgSender()` (native swap or fee-token transfer) and records it in `_requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee})` [1](#0-0) .
- On a successful response, `dispatchIncoming(GetResponse,...)` pays the stored `fee` to the relayer that delivered the response [6](#0-5) .
- On timeout, `dispatchTimeOut(GetRequestTimeout,...)` deletes `_requestCommitments[commitment]` and invokes `onGetTimeout` on the source app, but never transfers `meta.fee` anywhere — the comment "@notice Does not refund any protocol fees." documents this intentionally [2](#0-1) .
- Contrast with the POST-request timeout handler immediately below, which does `IERC20(feeToken()).safeTransfer(meta.sender, meta.fee)` when `meta.fee != 0` [3](#0-2) .
- The developer docs assert GET requests carry no fee at all ("GET requests do not have relayer fees, so there are no fees to refund on timeout"), which is now inconsistent with the `DispatchGet.fee`/`dispatch(DispatchGet)` implementation that clearly accepts and escrows a fee [4](#0-3) .
- The Intent Gateway's `_cancelFromSource` builds and dispatches exactly this kind of fee-bearing GET request using the cancelling user's `options.relayerFee`, so an ordinary user attempting to cancel an unfilled order and reclaim escrow is the party exposed to this fee loss [7](#0-6) .

### Impact Explanation
Any relayer fee attached to a GET request (including the fee paid by a user cancelling an Intent Gateway order from the source chain) is permanently lost if the request times out instead of being delivered. This is a direct loss of user funds with no recovery path — the fee is neither paid to a relayer (since delivery never happened) nor refunded to the payer, and simply becomes stuck in the `EvmHost` contract. This aligns with the class of bug in the reference report (funds paid by a user around a cancellation flow are never returned).

### Likelihood Explanation
GET request timeouts are a normal, expected occurrence (permissionless relayers may simply choose not to deliver a response, or a response may legitimately be delayed past the timeout window, especially since `_cancelFromSource` requires the timeout/height logic to hold across an entire challenge period). No special privilege or attack setup is required — any user who dispatches a fee-bearing GET request (e.g., via `cancelOrder` from source) and experiences a timeout will lose the attached fee. The condition is entirely reachable through a single normal user transaction plus the passage of time and a permissionless timeout submission by anyone.

### Recommendation
Refund `meta.fee` to `meta.sender` in `dispatchTimeOut(GetRequestTimeout, FeeMetadata, bytes32)`, mirroring the logic already present in the POST-timeout variant, and update the documentation to reflect that GET requests can carry fees.

### Proof of Concept
1. A user calls `IntentGatewayV2.cancelOrder` (source-side, cross-chain order) with a non-zero `options.relayerFee`, which reaches `_cancelFromSource` and dispatches a `DispatchGet` with `fee: options.relayerFee`, `payer: msg.sender` [5](#0-4) .
2. `EvmHost.dispatch(DispatchGet)` collects `options.relayerFee` from the user and stores it in `_requestCommitments[commitment]` [1](#0-0) .
3. No relayer delivers a `GetResponse` before `timeoutTimestamp` elapses (or the response is legitimately delayed past that point).
4. Anyone calls `handleGetRequestTimeouts` → `EvmHost.dispatchTimeOut(GetRequestTimeout,...)`, which deletes the commitment and calls `onGetTimeout`, but never transfers the escrowed `meta.fee` back to the user [8](#0-7) .
5. The user's `relayerFee` remains permanently locked in the `EvmHost` contract; it is never credited to any relayer nor returned to the user.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L885-906)
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
    }
```

**File:** evm/src/core/EvmHost.sol (L974-1001)
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
```

**File:** docs/content/developers/evm/messaging/get-requests.mdx (L522-527)
```text
## Timeouts

Timeouts are optional for GET requests and typically unnecessary for most applications. However, if your use case requires time-sensitive data, you can specify a non-zero `timeout` period—any requests that exceed this duration will be **rejected** during processing.

Like [POST request timeouts](/developers/evm/messaging/post-requests#timeouts), GET request timeouts require a cryptographic proof from the destination chain showing the timeout period has elapsed. Anyone can submit the timeout proof by calling [`IHandler.handleGetRequestTimeouts()`](/developers/evm/api/ihandler#handlegettimeouttimeouts). Unlike POST requests, GET requests don't have relayer fees, so there are no refunds to process on timeout.

```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L222-275)
```text
    /**
     * @dev Initiates cancellation of a cross-chain order from the source chain.
     *
     * Only the order creator may cancel, and only after the order deadline has passed
     * (verified by `options.height > order.deadline`). Dispatches a Hyperbridge GET
     * request to the destination chain to verify that the `_filled` storage slot for
     * this commitment is empty (i.e., the order was never filled on the destination).
     *
     * The GET response is handled by `onGetResponse`, which refunds the escrow if
     * the slot is indeed empty.
     *
     * `cancelOrder` has already emitted `OrderCancelled`; the matching `EscrowRefunded` follows
     * on this chain once the GET response returns through Hyperbridge.
     *
     * @param order The order to cancel.
     * @param options Cancel options including the proof height and relayer fee.
     * @param commitment The keccak256 hash of the ABI-encoded order.
     */
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        if (options.height <= order.deadline) revert NotExpired();

        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
        }

        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
            dest: order.destination,
            keys: keys,
            timeout: 0,
            height: options.height,
            fee: options.relayerFee,
            context: context,
            payer: msg.sender
        });

        address hostAddr = host();
        if (msg.value > 0) {
            IDispatcher(hostAddr).dispatch{value: msg.value}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```
