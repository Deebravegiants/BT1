## Analog Found

### Title
IntentGateway V2 escrow withdrawals permanently revert (and lock funds) if the beneficiary is blacklisted by the escrowed ERC20 - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw`, the single code path that releases escrowed order funds (fill, refund, and cancel), transfers tokens directly to a `beneficiary` address that is baked into the cross-chain message/commitment. If that token is a blacklist-capable stablecoin (USDC/USDT-style) and the beneficiary gets blacklisted, the transfer reverts every single time the message is (re)delivered, permanently freezing the escrowed input tokens with no way to redirect funds to a different address.

### Finding Description
`_withdraw` iterates the withdrawal request's tokens and unconditionally calls `IERC20(token).safeTransfer(beneficiary, amount)`, where `beneficiary` is decoded straight from the `WithdrawalRequest.beneficiary` field embedded in the original `Order`/message: [1](#0-0) 

This is reached from two unprivileged, relayer-driven callback paths:
- `onAccept` for `RedeemEscrow` (solver fill settlement) and `RefundEscrow` (destination-side cancellation), authenticated only against the registered peer gateway, not against the beneficiary: [2](#0-1) 
- `onGetResponse` for the source-chain cancel path, which also calls `_withdraw` with the fixed `beneficiary` from the stored `WithdrawalRequest`: [3](#0-2) 

In all three paths the beneficiary is fixed at order-fill/cancel time (`msg.sender` for the filler, or `order.user` for the refund) and cannot be changed later: [4](#0-3) 

If `token` is a blacklist-capable stablecoin and `beneficiary` becomes blacklisted (by the token issuer, independent of Hyperbridge or the gateway), `safeTransfer` unconditionally reverts. Since `onAccept`/`onGetResponse` failures leave no delivery receipt on the host (confirmed by the analogous `BridgeToken` test showing a reverted delivery is retryable), the message can be resubmitted indefinitely, but every resubmission hits the exact same fixed `beneficiary` and will revert again forever. There is no parameter, admin override, or alternate-recipient mechanism to redirect the payout — the escrowed tokens for that commitment are permanently stuck in the gateway contract.

This mirrors the tron variant of the same contract, which shows the identical fixed-beneficiary pattern using a raw `.call` with a still-reverting `TransferFailed()` check: [5](#0-4) 

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by any unprivileged solver or user who places or fills an order using a blacklist-capable ERC20 (e.g., USDC) as an input token. A user's escrow (refund case) or a solver's earned settlement (redeem case) can become permanently trapped in the `IntentGatewayV2`/`ExtrinsicIntents` contract if the corresponding beneficiary address is later blacklisted by the token issuer — a condition entirely outside the control of Hyperbridge, the gateway, or the relayer. Because `_withdraw` also finalizes order state (`_filled[commitment] = beneficiary`) only inside the same reverting call, the order remains stuck in limbo with no recovery path.

### Likelihood Explanation
Likelihood is realistic given Hyperbridge's IntentGateway explicitly targets stablecoin swaps (USDC/DAI are the documented example tokens), and USDC/USDT blacklisting is an established real-world occurrence. No malicious governance, admin, or relayer behavior is required — a single normal order combined with an ordinary blacklist event on the token issuer's side is sufficient to trigger permanent fund lock.

### Recommendation
Decouple beneficiary authorization from the transfer destination: if `safeTransfer`/`.call` to `beneficiary` fails, fall back to escrowing the amount in a per-beneficiary claimable balance (pull-payment pattern) rather than reverting the whole settlement, and expose a separate `claim`/`redirect` function allowing the beneficiary (or, after some recovery mechanism, the original order owner) to specify an alternate receiving address for that specific token.

### Proof of Concept
1. User places a cross-chain order with `inputs = [USDC]`, expecting a refund path or a solver fill.
2. Solver fills the order on the destination chain; `RedeemEscrow` is dispatched back to source with `beneficiary = solver`.
3. Before the message is relayed and executed, USDC blacklists the solver's address (e.g., due to unrelated OFAC/compliance action).
4. Relayer delivers the proof; `EvmHost` calls `ExtrinsicIntents.onAccept` → `_authenticate` succeeds → `_withdraw` is invoked with `beneficiary = solver`.
5. `IERC20(USDC).safeTransfer(solver, amount)` reverts because `solver` is blacklisted; the entire `onAccept` call reverts, so the host records no delivery receipt.
6. Any relayer resubmission of the identical message reproduces the same revert forever — the escrowed USDC is permanently locked in the gateway contract, with the order neither finalized nor refundable to a different address.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
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
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L301-306)
```text

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
