### Title
Escrowed Funds Permanently Locked with No Recovery when `RedeemEscrow`/`RefundEscrow` Delivery Fails, Because `_post` Hardcodes `timeout: 0` - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`IntentGatewayV2`/`ExtrinsicIntents` locks a user's input tokens in escrow on the source chain when an order is placed, and only releases them when a `RedeemEscrow` (solver payment) or `RefundEscrow` (cancellation) POST message is successfully delivered back from the destination chain via `onAccept`. The dispatch of these release messages hardcodes `timeout: 0`, meaning ISMP never expires them, so there is no timeout-based recovery path if delivery permanently fails (e.g. the destination-side registered gateway `_instance` mapping is stale, unregistered, or misconfigured relative to the source chain's expectations). This mirrors the reported `oft_adapter_fa.move` issue: assets are locked in an escrow whose only release path depends on a cross-chain message that can become permanently undeliverable, with no fallback recovery mechanism.

### Finding Description
When a solver fills a cross-chain order, `_fillCrossChain` transfers output tokens to the beneficiary and then calls `_post` to dispatch a `RedeemEscrow` message back to the order's source chain gateway to release the input tokens escrowed there: [1](#0-0) 

Note that `_post` unconditionally sets `timeout: 0` on the `DispatchPost` regardless of caller-supplied fill/cancel options: [2](#0-1) 

The same `_post` helper is reused for `RefundEscrow` when cancelling from the destination chain: [3](#0-2) 

On the receiving (source) side, `onAccept` gates both `RedeemEscrow` and `RefundEscrow` bodies behind `_authenticate`, which requires that the sender module matches the chain's own registered `_instance(request.source)`: [4](#0-3) [5](#0-4) 

Escrowed tokens are only ever released via `_withdraw`, which is reachable exclusively through this `onAccept`/`onGetResponse` message path: [6](#0-5) 

If the `_instances` mapping for the relevant chain on the source side is not yet registered, becomes stale after a `NewDeployment` update, or the relayer gate (`_checkRelayer`) blocks delivery indefinitely, `_authenticate` (or `onlyHost`/relayer checks) will permanently revert on every delivery attempt of the `RedeemEscrow`/`RefundEscrow` message. Because these dispatches use `timeout: 0`, the ISMP host never lets the source chain time the request out and re-open an alternate recovery path — there is no `onPostRequestTimeout` handler wired into `ExtrinsicIntents`/`IntentsBase` for these release messages that would refund/unlock the escrow. The escrow accounting in `_orders[commitment][token]` (used by `_withdraw`) thus has no code path to release the funds once the message is undeliverable, exactly analogous to `oft_adapter_fa.move`'s `debit_fungible_asset`/`credit` pattern where escrow is only released by a successful remote-triggered credit with no fallback.

### Impact Explanation
If the destination-chain-to-source-chain gateway registration or relayer authorization ever falls out of sync at the moment a solver fills an order or a user cancels an order from the destination chain, the escrowed input tokens on the source chain become permanently frozen: the solver who already paid out the output tokens to the beneficiary loses their entitlement to the escrowed reimbursement, or a cancelling user's refund can never be delivered. Since `timeout: 0` explicitly disables the only other exit mechanism (timeout-based reversal) available elsewhere in the protocol (e.g., `HyperFungibleToken.onPostRequestTimeout` re-mints on timeout), there is no way — administrative or otherwise — within these contracts to reclaim the locked escrow. This is a permanent freezing-of-funds condition reachable from ordinary, unprivileged solver/user actions (`fillOrder`, `cancelOrder`).

### Likelihood Explanation
Likelihood is low-to-moderate: it requires the source-side `_instances` mapping to be unset/mismatched for the relevant chain, or the relayer gate to be misconfigured, at the exact time a solver fills an order or a user cancels a cross-chain order — a narrow but plausible operational window (e.g., gateway redeployment, `NewDeployment` update in flight, or relayer rotation). Unlike order placement/fill flows that support GET-request-based cancellation with proofs, the `RedeemEscrow`/`RefundEscrow` release message has no analogous fallback because of the hardcoded zero timeout.

### Recommendation
Do not hardcode `timeout: 0` for `RedeemEscrow`/`RefundEscrow` dispatches in `_post`. Give these messages a bounded timeout and implement an `onPostRequestTimeout` handler in `ExtrinsicIntents` that releases the escrowed funds (to the solver for `RedeemEscrow`, to the user for `RefundEscrow`) directly on the source chain when the message times out, mirroring the pattern already used in `HyperFungibleToken.onPostRequestTimeout`. Alternatively, add an explicit, permissioned recovery/emergency-unlock function gated by a timelock or multisig, consistent with the acknowledged trade-off in the original report.

### Proof of Concept
1. User places a cross-chain order via `IntentGatewayV2.placeOrder`, escrowing input tokens on the source chain in `_orders[commitment][token]`.
2. Before the solver fills the order, the source chain's gateway `_instances` mapping for the destination chain is changed/rotated via a `NewDeployment` `onAccept` call (or the relayer is rotated via `setRelayer`), so the previously valid destination gateway address no longer matches `_instance(order.destination)`.
3. Solver calls `fillOrder` on the destination chain; `_fillCrossChain` transfers output tokens to the beneficiary and dispatches a `RedeemEscrow` POST with `timeout: 0` back to the source chain [2](#0-1) .
4. When the relayer delivers this message on the source chain, `onAccept` calls `_authenticate`, which now fails permanently because `_instance(request.source)` no longer matches the sender module [4](#0-3) .
5. Because `timeout` was `0`, the ISMP host never allows this request to be timed out, and `_withdraw` is never invoked for this commitment — the solver's escrowed reimbursement (`_orders[commitment][token]`) remains permanently stuck with no code path to release it.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L63-67)
```text
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
    }
```

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-485)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
    }
```
