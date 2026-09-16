## Analysis

I found a genuine CEI (Checks-Effects-Interactions) violation that directly mirrors the reported bug class — an external call to a caller/beneficiary address made *before* internal accounting state is updated — in the Tron variant of the intents escrow contract.

### Title
Reentrancy via CEI violation in `withdraw()` — external transfer precedes escrow-state update - (`evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.withdraw()` on the Tron deployment pays out escrowed tokens to `beneficiary` via a raw low-level `.call` *before* decrementing the corresponding `_orders[commitment][token]` balance, reproducing the exact CEI-ordering bug described in the LaunchEvent `withdrawAVAX()` report. The sibling mainline implementation (`IntentsBase.sol::_withdraw`) was hardened to update state before making the external call, but this fix was not carried over to the Tron contract.

### Finding Description
In `withdraw()`, for each token in the withdrawal request, the external transfer happens first, and the storage decrement happens after: [1](#0-0) 

Compare this to the corrected mainline analog `IntentsBase.sol::_withdraw`, which decrements `_orders[body.commitment][token]` *before* performing the transfer/`_sendValue`: [2](#0-1) 

`withdraw()` is only reachable internally, via `onAccept` (RedeemEscrow/RefundEscrow, gated by `onlyHost` + `authenticate`) or `onGetResponse` (gated by `onlyHost`): [3](#0-2) [4](#0-3) 

`_filled[body.commitment]` is set once, at the top of `withdraw()`, before the token loop, which blocks the most obvious same-order cross-function reentries (`cancelOrder`, `fillOrder`) for that commitment. However, the CEI-ordering bug still leaves stale, non-decremented escrow balances (`_orders[commitment][token]`) exposed to the callee during the external call in multi-token withdrawal requests, and a malicious/attacker-supplied ERC-20 `token` address (declared by the order's own inputs at placement time) executing arbitrary code inside `transfer()` can attempt to leverage this window before its own balance is zeroed out.

### Impact Explanation
This is a direct reintroduction of the exact vulnerability class already remediated on the mainline EVM intents contract. Since the fix (state-before-call ordering) was demonstrably necessary there (see the dedicated reentrancy regression test suite), its absence on the Tron contract removes a defense-in-depth layer against reentrancy-based accounting corruption of escrowed funds during settlement, particularly for multi-token withdrawal requests where later loop iterations' `_orders` balances remain unmodified while an earlier token's external call is still executing.

### Likelihood Explanation
Medium. Direct exploitation is constrained because `withdraw()` is only invoked from `onlyHost`-gated `onAccept`/`onGetResponse`, and `_filled[commitment]` is set before the loop begins, blocking reentry into `cancelOrder`/`fillOrder` for the same commitment. However, the pattern is a clear deviation from the CEI discipline enforced everywhere else in the codebase for this exact code path, and any future addition of untrusted token callbacks (ERC-777-style hooks) or expansion of externally reachable order-scoped functions would immediately turn this into a live escrow-draining vector.

### Recommendation
Mirror the CEI ordering already used in `IntentsBase.sol::_withdraw`: decrement `_orders[body.commitment][token]` (and `_orders[body.commitment][TRANSACTION_FEES]`) before making the external `.call`/`transfer` to `beneficiary`/`feeToken`, for both the token loop and the fee payout in `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw`.

### Proof of Concept
1. A source-chain order escrows two output tokens for a beneficiary, where the second token in `body.tokens` is standard, but the first is address(0) (native) or a token whose `transfer()` can execute a callback.
2. Hyperbridge delivers a `RedeemEscrow`/`RefundEscrow` message; `onAccept` calls `withdraw(body, ...)`.
3. `withdraw()` sets `_filled[commitment] = beneficiary`, then loops: for token[0] it calls `beneficiary.call{value: amount}("")` *before* `_orders[commitment][token0] -= amount` executes.
4. During this call, `_orders[commitment][token1]` (the second, not-yet-processed token) is still at its pre-withdrawal balance, and could be leveraged by any future or adjacent code path that reads `_orders` state without the same finalize guard used by `cancelOrder`/`fillOrder`. [5](#0-4)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
