## Analog Found

### Title
Permanent freezing of escrowed intent-order funds when a beneficiary is blacklisted by a token (e.g. USDC) - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
The Dinari report shows that `cancelOrder()` fails permanently if the refund recipient is on the USDC blacklist, because the refund uses a direct `safeTransfer` to a fixed, un-substitutable address. The same pattern exists in Hyperbridge's Intent Gateway: `_withdraw()` sends escrowed input tokens (which can be USDC or any blacklist-capable ERC20) directly to a hardcoded beneficiary with no fallback/claim mechanism.

### Finding Description
`IntentsBase._withdraw()` is the single settlement/refund routine used by every cancellation and fill-settlement path in the Intent Gateway. It transfers escrowed tokens straight to `beneficiary` via `safeTransfer`: [1](#0-0) 

This function is reached from:
- `_cancelSameChain()`, where `beneficiary = order.user` [2](#0-1) 
- `onAccept()` handling `RefundEscrow`/`RedeemEscrow` cross-chain messages, where `beneficiary` is `order.user` (refund) or the filling solver (settlement) [3](#0-2) 

If the input token is USDC (or any blacklist-capable stablecoin) and the beneficiary address is later added to the issuer's blacklist, `safeTransfer` reverts unconditionally, with no alternate recipient or claim path.

For the cross-chain routes, the incoming message is delivered through `EvmHost.dispatchIncoming`, which calls `onAccept` via a low-level `.call` and, on failure, deletes the request receipt "so that it can be retried": [4](#0-3) 

This confirms the failure is retryable — but retrying with the identical fixed beneficiary always fails again once that address is permanently blacklisted, so the escrow becomes permanently stuck (unlike a temporary/relayer-side issue, this is a protocol-level dead end since there is no way to redirect the refund to a different address).

### Impact Explanation
Once an order's `user` (or a filling solver) is blacklisted by the escrowed token's issuer, that specific order's escrowed funds become permanently unrecoverable:
- Same-chain cancellation (`_cancelSameChain`) reverts forever for that order.
- Cross-chain `RefundEscrow`/`RedeemEscrow` messages can never be successfully delivered/finalized on the source chain, since `onAccept` will always revert at the `safeTransfer` step.
- This is a genuine "permanent freezing of funds" scenario for the affected order — the escrowed input tokens are stuck in the `IntentGatewayV2`/`IntentsBase` contract indefinitely with no protocol-level recovery mechanism (no claim-later pattern, no beneficiary override, no sweep path for refunds).

The blast radius is scoped to individual orders (other orders/messages are unaffected, per the retryable per-request semantics in `dispatchIncoming`), consistent with a Medium severity classification.

### Likelihood Explanation
Any order whose `user` (source-chain cancel/refund beneficiary) or filling solver becomes blacklisted by USDC/Circle (or any other centrally-blacklistable ERC20 used as an order input) after placing/filling an order will trigger this. Since USDC is an explicitly supported/expected input token in the Intent Gateway (used throughout the test suite), and blacklisting is outside the protocol's control, this is a realistic, externally-triggerable condition — not a contrived edge case.

### Recommendation
Do not force-push refunds/settlements to a fixed beneficiary via `safeTransfer` inside `_withdraw`. Instead:
- Wrap the token transfer in a try/catch and, on failure, credit the amount to an internal per-beneficiary claimable balance that can be withdrawn later (e.g., to a different address the beneficiary designates), similar to the "pull over push" pattern recommended in the original Dinari report.
- Alternatively, allow the beneficiary (or a delegate) to specify an alternate receiving address for the refund at cancellation/settlement time.

### Proof of Concept
1. User places a same-chain or cross-chain order with USDC as an input token via `IntentGatewayV2.placeOrder` (escrow held under `_orders[commitment][usdc]`).
2. `order.user`'s address is added to USDC's blacklist by Circle (e.g., flagged for unrelated compliance reasons).
3. User (or, after the deadline, any relayer) calls `cancelOrder()`:
   - Same-chain: routes to `_cancelSameChain` → `_withdraw` → `IERC20(usdc).safeTransfer(order.user, amount)` reverts, so `cancelOrder()` always reverts. [5](#0-4) 
   - Cross-chain from destination: `_cancelFromDest` marks the order filled and dispatches `RefundEscrow`; when relayed to the source chain, `onAccept` → `_withdraw` reverts at the `safeTransfer`, and `EvmHost.dispatchIncoming` silently deletes the receipt so the message stays "retryable" forever, but every retry hits the same blacklisted address and reverts identically. [3](#0-2) [6](#0-5) 
4. The escrowed USDC for this order remains locked in the gateway contract permanently, with no path to recovery.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
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
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
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

**File:** evm/src/core/EvmHost.sol (L806-817)
```text
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
```
