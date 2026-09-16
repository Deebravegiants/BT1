### Title
Unspent native ETH/TRX in `IntentGatewayV2.placeOrder` (Tron variant) is never refunded and becomes permanently stuck - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron port of `IntentGatewayV2.placeOrder` accepts native value via `msg.value`, consumes it to cover native-token order inputs, predispatch assets, and solver fees (via a Uniswap V2 `swapETHForExactTokens` call), but — unlike the canonical EVM implementation — never refunds the leftover `msgValue` to the caller at the end of the function. Any native-token overpayment is silently trapped in the contract with no code path to recover it.

### Finding Description
In the canonical EVM `IntentGatewayV2.placeOrder` (`evm/src/apps/IntentGatewayV2.sol`), after the input escrow and fee-swap accounting, unspent `msgValue` is explicitly refunded to the caller: [1](#0-0) 

The Tron variant performs the identical accounting steps — decrementing `msgValue` for native inputs, predispatch native transfers to the `dispatcher`, and the `swapETHForExactTokens` fee payment — but the function ends immediately after the fee-escrow block with no refund of any remaining `msgValue`: [2](#0-1) 

Compounding this, the Tron variant also discards the return value of `swapETHForExactTokens`: [3](#0-2) 

The standard Uniswap V2 router's `swapETHForExactTokens` refunds any leftover ETH after the swap to `msg.sender` of that call — which is the `IntentGatewayV2` contract itself, not the end user, since the contract is the one invoking the router. That refunded ETH lands in the gateway contract's balance with no accounting entry and no subsequent transfer back to the order-placer.

There is no `receive()`/`fallback()` handling that forwards this ETH out, and no `_sendValue`-style refund helper is invoked in `placeOrder`. The only place native tokens leave the contract elsewhere is `onAccept`'s `SweepDust` path, which is driven entirely by a cross-chain governance message and specific `TokenInfo` amounts recorded by `_orders[commitment][...]` — the stray, un-escrowed overpayment is not tracked in that mapping at all, so it can never be swept, refunded, or otherwise withdrawn.

### Impact Explanation
Any user who:
- overestimates `msgValue` relative to `order.inputs` (native-token input) plus `order.fees` swap cost, or
- pays a native `nativeFee`/predispatch value slightly higher than required (common due to slippage buffers recommended in client tooling, e.g. the SDK docs advise sending `nativeValue` plus buffer for solver fees),

will have the excess native token permanently locked in the `IntentGatewayV2` Tron contract with no path to reclaim it. This is a direct, unbounded loss of user funds (in ETH/TRX-equivalent native currency) triggered by a single `placeOrder` transaction from any unprivileged caller — it requires no admin or attacker action, only normal usage patterns illustrated in the SDK's own order-placement flow, which explicitly instructs sending `value + nativeValue` and states "unused native is refunded" (a promise the Tron contract does not keep).

### Likelihood Explanation
High likelihood: this triggers on ordinary use whenever the caller supplies native value that isn't exactly consumed (which is the normal case since callers must estimate `nativeFee`/swap costs off-chain, as documented in `docs/content/developers/evm/intent-gateway/placing-orders.mdx`). No adversarial conditions or governance/admin compromise are required — it's a straightforward missing-refund bug reachable from a single `placeOrder` call.

### Recommendation
Mirror the canonical EVM `IntentGatewayV2.sol` behavior: capture the `amounts[0]` actually spent from `swapETHForExactTokens` and decrement `msgValue` accordingly, then add a final `if (msgValue > 0) { (bool sent,) = msg.sender.call{value: msgValue}(""); require(sent); }` (or an equivalent `_sendValue` helper) at the end of `placeOrder` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to refund any unspent native token to the caller.

### Proof of Concept
1. Caller calls `IntentGatewayV2.placeOrder{value: X}(order, graffiti)` where `order.inputs` contains only ERC-20 tokens (no native-token input) and `order.fees > 0`.
2. Since `order.inputs` has no native token, `msgValue` remains `X` after the input-escrow loop [4](#0-3) .
3. `order.fees > 0` and `msgValue > 0`, so the contract calls `swapETHForExactTokens{value: msgValue}(order.fees, ...)` — the router spends only enough ETH to buy `order.fees` of the fee token and refunds the rest (`X - swapCost`) back to `address(this)` (the gateway contract) [3](#0-2) .
4. The function returns after emitting `OrderPlaced` with no refund step, leaving `X - swapCost` permanently stranded in the contract's balance [5](#0-4) .
5. No other function in the contract (only `onAccept`'s governance-driven `SweepDust` path) can move that untracked balance out, since it was never recorded in `_orders[commitment][...]`.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L375-397)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }

        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L386-506)
```text

        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

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
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }

        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }

        emit OrderPlaced({
            user: order.user,
            source: order.source,
            destination: order.destination,
            deadline: order.deadline,
            nonce: order.nonce,
            fees: order.fees,
            session: order.session,
            predispatch: order.predispatch.assets,
            inputs: reducedInputs,
            beneficiary: order.output.beneficiary,
            outputs: order.output.assets,
            predispatchCall: order.predispatch.call,
            outputCall: order.output.call,
            graffiti: graffiti
        });
    }
```
