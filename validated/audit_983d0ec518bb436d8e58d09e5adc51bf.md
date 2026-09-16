### Title
Destination-side order cancellation permanently forecloses the source-side recovery path, risking indefinite freezing of escrowed funds - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`IntentGatewayV2.cancelOrder` on the destination chain (`_cancelFromDest`) irreversibly marks an order's `_filled` slot as "settled" *before* the actual refund has been confirmed to reach the source chain, and the same `_filled` slot is also used by `onGetResponse` to decide whether the order was ever filled by a solver. Once `_cancelFromDest` has run, the only remaining fallback (`_cancelFromSource`) is permanently disabled, because it will always observe a non-empty `_filled` slot and revert with `Filled()` — even though the order was never actually filled, only cancelled. This mirrors the OpenQ finding: a "close"-type state transition is committed before the corresponding balance/settlement is guaranteed, and once closed there is no way back, so funds can become stuck if the cross-chain settlement message never lands.

### Finding Description
`cancelOrder` routes a cross-chain order to `_cancelFromDest` when called on the destination chain: [1](#0-0) 

This immediately sets `_filled[commitment] = order.user` on the destination chain to block future fills, then dispatches a `RefundEscrow` POST request to the source chain with `timeout: 0` (never expires) via `_post`: [2](#0-1) 

Delivery of that message is gated by a single designated relayer once one is configured: [3](#0-2) [4](#0-3) 

If for any reason (relayer outage, selective non-delivery, or the message simply never being picked up since it has no timeout to trigger any alternate handling) that `RefundEscrow` message never reaches `onAccept` on the source chain, the escrowed tokens sitting in `_orders[commitment][token]` on the **source** chain are never released via `_withdraw`.

Critically, the documented "fallback" recovery path — cancelling from the source chain — is a dead end at this point. `_cancelFromSource` dispatches a GET query for the destination's `_filled` slot, and `onGetResponse` treats *any* non-empty value as proof the order was filled by a solver, reverting with `Filled()`: [5](#0-4) [6](#0-5) 

Because `_cancelFromDest` writes the exact same non-empty value into that slot as a genuine fill would, `onGetResponse` cannot distinguish "cancelled from destination" from "filled by a solver." The single `_filled` mapping is overloaded to mean both states, so the moment a user chooses the destination-side cancellation route, the source-side cancellation route is permanently and unconditionally closed off — regardless of whether the refund message ever actually arrives.

This is the same root-cause pattern as the OpenQ report: an irreversible "closed" state is committed on-chain before the corresponding balance movement is guaranteed to complete, with no way to reopen or use an alternate channel to reclaim the still-escrowed funds.

### Impact Explanation
If the single `RefundEscrow` message dispatched by `_cancelFromDest` is never delivered to the source chain (relayer downtime, selective censorship enabled by the `_relayer` allow-list, or any other permanent delivery failure), the user's escrowed input tokens on the source chain remain locked in the `IntentGatewayV2`/`ExtrinsicIntents` contract with no on-chain path to reclaim them: the destination has already committed to "cancelled," and the source-side proof-based fallback interprets that exact same state as "filled," refusing to release funds. This is a permanent freezing-of-funds condition, matching the Medium severity classification of the original report.

### Likelihood Explanation
Reachable by a single unprivileged transaction from the order's own creator (or, after the deadline, from any third party) calling `cancelOrder` with `from: "destination"`. No governance, admin, or validator misbehavior is required to trigger the state transition itself — only ordinary Hyperbridge message-delivery conditions (a relayer that is offline, restricted via `setRelayer`, or otherwise fails to submit the `RefundEscrow` proof) are needed to turn the committed "cancelled" state into a permanently unrecoverable one, since the alternate source-side path is architecturally foreclosed rather than merely delayed.

### Recommendation
Do not let `_cancelFromSource`/`onGetResponse` treat every non-empty `_filled` value identically. Distinguish "filled by a solver" from "cancelled-from-destination, refund message not yet confirmed" — e.g. use a distinct sentinel/tag for the destination-cancelled state, and allow the source-side path to still complete the refund (or retry dispatch of the pending `RefundEscrow`) when the destination slot indicates "cancelled" rather than "filled." Alternatively, keep an explicit escape hatch on the source chain that permits reclaiming escrow once a bounded retry/timeout window has elapsed without a confirmed `RefundEscrow` delivery, instead of relying indefinitely on a single relayer.

### Proof of Concept
1. User places a cross-chain order; escrow held on source chain (`_orders[commitment][token] > 0`).
2. User calls `cancelOrder(order, options)` on the destination chain → `_cancelFromDest` sets `_filled[commitment] = user` and dispatches `RefundEscrow` (`timeout: 0`) to the source chain, gated by `_relayer`.
3. The designated relayer never submits the message to `onAccept` on the source chain (offline, or `_relayer` has been rotated to an address that refuses this specific delivery).
4. User, unaware the refund is stuck, tries the documented fallback: calls `cancelOrder` on the source chain after the deadline → routes to `_cancelFromSource`, dispatches a GET query of the destination's `_filled[commitment]` slot.
5. `onGetResponse` sees a non-empty value (written in step 2) and reverts with `Filled()`.
6. The source-chain escrow remains locked indefinitely — the only remaining hope is the same relayer that already failed to deliver in step 2. [1](#0-0) [6](#0-5)

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L75-78)
```text
    function _checkRelayer(address relayer) internal view {
        address authorised = _relayer;
        if (authorised != address(0) && relayer != authorised) revert Unauthorized();
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L128-142)
```text
    function _post(Order calldata order, bytes memory body, uint256 relayerFee, uint256 nativeFee) internal {
        DispatchPost memory request = DispatchPost({
            dest: order.source,
            to: abi.encodePacked(_instance(order.source)),
            body: body,
            timeout: 0,
            fee: relayerFee,
            payer: msg.sender
        });
        if (nativeFee > 0) {
            IDispatcher(host()).dispatch{value: nativeFee}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-275)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-307)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```
