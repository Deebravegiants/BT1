Confirmed: `_post` in `evm/src/apps/intentsv2/ExtrinsicIntents.sol` always dispatches with `timeout: 0`, meaning `RedeemEscrow` and `RefundEscrow` messages never expire and cannot be timed out or reissued. This is the key structural fact that supports the analog below.

### Title
Permanent freezing of escrowed input tokens when a solver's `RedeemEscrow` message is never delivered after a cross-chain fill - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
In `_fillCrossChain`, a solver delivers output tokens to the beneficiary on the destination chain and the order is immediately marked filled locally (`_filled[commitment] = msg.sender`), before a Hyperbridge `RedeemEscrow` POST message is dispatched back to the source chain to release the solver's payment (the escrowed input tokens). That dispatch uses `timeout: 0` (never expires) and pays only an optional relayer fee. If the message is never relayed (e.g. no relayer picks it up because the fee is too low, or relaying is otherwise obstructed), the input tokens escrowed on the source chain remain locked forever, with no other function able to release them — mirroring the reported bug class where a "commission" deducted from escrow becomes permanently stranded because only one specific completion path could release it, and no fallback repayment path exists.

### Finding Description
The fill flow is: [1](#0-0) 
`_filled[commitment] = msg.sender` is set unconditionally at the top of `_fillCrossChain`, before any tokens are actually transferred, and before the `RedeemEscrow` message is even dispatched. The message itself is built via `_post`, which hardcodes `timeout: 0`: [2](#0-1) 

Because `timeout` is `0`, the request never becomes eligible for `onPostRequestTimeout`/timeout processing (as documented, timeouts are only processed for requests whose `timeout` has been exceeded — a `0` timeout effectively disables that entirely). This means:

1. The solver has already paid out the beneficiary's output tokens on the destination chain (irreversible).
2. `_filled[commitment]` is already set to the solver's address on the destination chain, so the destination gateway will reject any future fill attempt (`Filled()`), and any user attempting to cancel via `_cancelFromSource`'s GET-based path will find the destination's `_filled` slot non-empty and `onGetResponse` will revert with `Filled()`: [3](#0-2) 
3. On the source chain, the escrowed input tokens (`_orders[commitment][token]`) are only ever released by `_withdraw`, which is only invoked from `onAccept` upon actually receiving the `RedeemEscrow`/`RefundEscrow` message via Hyperbridge, or from the `onGetResponse`/cancel paths (which are now blocked by point 2 above): [4](#0-3) 

If no relayer ever delivers the `RedeemEscrow` message (whether due to economic disincentive from an underpriced/zero relayer fee, relayer censorship, or any operational failure), there is no code path left that can release the source-chain escrow to the solver, nor can the user reclaim it since the destination is already marked filled. The funds are permanently trapped in the `IntentGatewayV2`/`IntentsBase` contract on the source chain, exactly matching the reported bug class: value moved into escrow that only one specific, non-guaranteed completion event can release, with no fallback recovery mechanism.

### Impact Explanation
This results in permanent freezing of user/solver funds — the escrowed input tokens on the source chain become unrecoverable once the destination-side fill is marked complete but the corresponding `RedeemEscrow` message is not relayed. This is a direct, unbacked loss of funds for the solver (who already paid the beneficiary) with no on-chain recourse, satisfying the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Likelihood is proportional to how often a relayer fails to deliver a POST message with `timeout: 0`. Because relaying is permissionless but optional and fee-driven, a solver who sets `options.relayerFee` too low (or a malicious/absent relayer market for a given destination) can cause indefinite non-delivery. Since `timeout` is hardcoded to `0` regardless of the fee configured, there is no protocol-level backstop (e.g., resubmission after a bounded window) to guarantee eventual delivery or refund. Any single cross-chain fill is exposed to this risk, making it a realistically reachable path from an ordinary, unprivileged `fillOrder` transaction.

### Recommendation
- Set a bounded, non-zero `timeout` on the `RedeemEscrow`/`RefundEscrow` dispatch in `_post`, and implement `onPostRequestTimeout` for `IntentGatewayV2` so that a genuinely undelivered message can be recovered (e.g., by allowing the solver to reclaim proof of destination delivery through an alternate GET-based path, similar to `_cancelFromSource`, or by re-dispatching the redemption request).
- Alternatively, allow a permissionless "retry"/"re-dispatch" function that lets the solver resubmit a `RedeemEscrow` request for a commitment already marked filled on the destination, using `fundRequest` semantics to bump the relayer fee if the original message is stuck pending (not timed out).
- Add fuzzing/unit tests that simulate relayer non-delivery of `RedeemEscrow`/`RefundEscrow` messages and assert the escrowed tokens can still be recovered through some path.

### Proof of Concept
1. User places a cross-chain order on chain A (source) escrowing input tokens in `IntentGatewayV2`/`IntentsBase._orders`.
2. Solver calls `fillOrder` on chain B (destination) before the deadline, delivering output tokens to the beneficiary; `_fillCrossChain` sets `_filled[commitment] = solver` on chain B and dispatches a `RedeemEscrow` POST with `timeout: 0` and a low/zero `relayerFee` back to chain A.
3. No relayer ever submits the corresponding proof to chain A's `IHandler` (e.g., because the fee is uneconomical) — the message sits pending indefinitely since `timeout: 0` never triggers a timeout path.
4. The user attempts `cancelOrder` from the source (`_cancelFromSource`); the dispatched `DispatchGet` reads `_filled` on chain B, which is non-empty (`solver`), so `onGetResponse` reverts with `Filled()`.
5. No function on chain A can release `_orders[commitment][token]` to the solver or refund it to the user — the escrowed tokens are permanently stuck in the `IntentGatewayV2` contract balance on chain A.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L126-142)
```text
    /// @dev Posts `body` to the gateway on the order's source chain, paying `nativeFee` in native
    /// tokens when non-zero and in the fee token otherwise.
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-219)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L352-366)
```text
    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```
