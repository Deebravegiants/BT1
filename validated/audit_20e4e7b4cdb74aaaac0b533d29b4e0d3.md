### Title
Escrow accounting is credited before, and never verified against, the actual token transfer result — silent-failing ERC20 tokens inflate `_orders` escrow beyond real balance (Tron `IntentGatewayV2`) - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In the Tron variant of `IntentGatewayV2.placeOrder`, when an order has `predispatch` calldata, tokens routed through the `CallDispatcher` are swept back from the dispatcher to the gateway using a raw `IERC20.transfer` selector call (not `SafeERC20.safeTransfer`), and the escrow ledger `_orders[commitment][token]` is incremented **before** that sweep is even dispatched, based only on the dispatcher's pre-transfer balance. Neither the code nor `CallDispatcher.dispatch` verifies the ERC20 boolean return value of the `transfer` call — only that the low-level call did not revert.

### Finding Description
`placeOrder` builds `transferCalls[i]` with a raw encoded `transfer` selector rather than `SafeERC20.safeTransfer`: [1](#0-0) 

The escrow increment `_orders[commitment][token] += reducedInputs[i].amount;` happens inside the same loop that computes `balance` and builds `transferCalls[i]`, i.e. strictly before `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` is even called: [2](#0-1) 

`CallDispatcher.dispatch` only checks that the low-level `.call` did not revert; it never decodes/validates the ERC20 boolean return value in `result`: [3](#0-2) 

For a non-reverting ERC20 that returns `false` on failure (a well-known class of non-compliant tokens), the `to.call{value: 0}(data)` succeeds at the EVM level (`success = true`) even though no tokens moved, so `CallDispatcher` does not revert. Because the gateway's escrow bump already happened before dispatch and is not reconciled against actual balance received afterward (unlike the sibling, non-Tron `IntentGatewayV2.sol`, which measures `balanceOf` deltas before/after the sweep — see lines 260–311 of `evm/src/apps/IntentGatewayV2.sol`), the `_orders` map ends up crediting escrow for tokens that were never actually pulled into the gateway contract.

### Impact Explanation
`_orders[commitment][token]` is the sole bookkeeping the gateway relies on to release funds during fills, cancellations, and refunds via `_withdraw`, which pays out real token balances via `safeTransfer`: [4](#0-3) 

If escrow is credited without a matching real transfer, the gateway's bookkeeping becomes desynchronized from its actual token balance. Subsequent legitimate withdrawals for other orders can then fail (revert, freezing funds) once the real balance is exhausted, or — depending on solver/fill flow ordering — allow one inflated commitment to be paid out of funds that rightfully belong to other users' escrows. This is a fund-loss / insolvency vulnerability directly reachable by any unprivileged user who places an order with `predispatch` calldata pointing at a non-standard ERC20 token.

### Likelihood Explanation
Likelihood is proportional to how many supported input tokens on Tron deployments are non-reverting-on-failure ERC20s (a known real-world token category, e.g. legacy USDT-style tokens returning `false`). Any user or attacker can choose which token address to use for `order.inputs`/`predispatch.assets`, so exploitation only requires selecting or waiting for a supported token with this behavior, or triggering conditions (pause/blacklist) under which a compliant token returns `false` instead of reverting.

### Recommendation
Replace the raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` sweep calls with `SafeERC20.safeTransfer` semantics (or have `CallDispatcher` decode and require `abi.decode(result, (bool))` to be true for calls targeting `transfer`/`transferFrom` selectors), and move the `_orders[commitment][token] += reducedInputs[i].amount` escrow credit to after `ICallDispatcher.dispatch` completes, verified against the gateway's own `balanceOf` delta — mirroring the pattern already used in the non-Tron `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Configure/list a non-compliant ERC20 token `T` (returns `false` on failed `transfer` instead of reverting) as a supported input token, or use a compliant token that can be made to return `false` under some condition (e.g., recipient blacklisted, contract paused mid-tx via reentrancy from `predispatch.call`).
2. Call `placeOrder` with `order.predispatch.call` and `order.predispatch.assets` set so `T` is routed to the `CallDispatcher`, and `order.inputs` includes `T`.
3. During predispatch execution (attacker-controlled call), cause `T.transfer(gateway, balance)` invoked from the dispatcher to return `false` (e.g., token enters a state where transfers to `address(this)` are blocked but don't revert).
4. `CallDispatcher.dispatch` sees `success = true` (call didn't revert) and proceeds; `_orders[commitment][T]` was already incremented by `reducedInputs[i].amount` in the loop prior to dispatch.
5. The gateway now shows escrowed `T` balance for `commitment` that was never actually received, while its real `T.balanceOf(address(this))` is unaffected — a later `_withdraw` call for this or another commitment can pay out `T` it does not have backing for, at the expense of other users' genuine escrow.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-449)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
```

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
