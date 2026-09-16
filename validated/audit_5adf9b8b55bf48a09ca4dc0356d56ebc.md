## Analysis Result

### Title
Excess native token sent to `placeOrder` is never refunded, permanently trapping user funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron-targeted `IntentGatewayV2` contract's `placeOrder` function is `payable` and consumes `msg.value` to cover native-token order inputs and/or a native-to-fee-token swap, but unlike the canonical EVM `IntentGatewayV2`, it never returns unspent `msg.value` to the caller. This mirrors the RubiconRouter "excess ether did not return to the user" bug class: any overpayment above what is strictly required is retained by the contract and permanently unrecoverable by the sender.

### Finding Description
`placeOrder` in `evm/tron/contracts/apps/IntentGatewayV2.sol` tracks a local `msgValue` variable that is decremented as native-token legs are consumed (for predispatch assets, for direct native inputs, and for the `swapETHForExactTokens` fee-token purchase), exactly as the canonical `evm/src/apps/IntentGatewayV2.sol` does: [1](#0-0) [2](#0-1) [3](#0-2) 

After the fee-swap block, the function proceeds directly to `emit OrderPlaced(...)` and returns — there is no `msgValue > 0` refund branch anywhere in the function: [4](#0-3) 

This is a direct regression against the canonical, audited EVM implementation, which explicitly refunds any leftover `msgValue` to `msg.sender` at the end of `placeOrder`: [5](#0-4) 

The Tron contract also has no `fillOrder` function at all in this file (only `placeOrder`, `cancelOrder`, `onAccept`, `withdraw`), so the missing-refund issue is confined to `placeOrder`, but that is the primary unprivileged, publicly reachable entry point that accepts native value from ordinary users placing orders.

### Impact Explanation
Any user who overestimates the native-token amount needed for a native input leg or for the ETH→fee-token swap (e.g., due to price movement between quote and execution, or simply sending a safety margin) will have the surplus silently absorbed by the contract with no path to reclaim it — this is a direct, permanent loss of user funds reachable from a single ordinary `placeOrder{value: X}` transaction. There is no owner/admin sweep of ordinary user overpayment visible in this code path (the only sweep mechanism, `SweepDust` in `onAccept`, is driven by a privileged `RequestKind.SweepDust` message and not a self-service user refund).

### Likelihood Explanation
High. `placeOrder` is the primary unprivileged entry point of the intent gateway, callable by any user with attached native value. Any deviation between the amount sent and the exact required amount (e.g., due to swap slippage on `swapETHForExactTokens` consuming less than sent, or a user rounding up the native input amount) triggers the loss. Given that the sibling/canonical EVM contract explicitly implements and tests this refund (`testPlaceOrder_RefundsExcessNativeToken`, `testPlaceOrder_FeeSwap_RefundsExcessNativeToken`), the omission here indicates a genuine drift/regression in the Tron contract rather than an intentional design choice.

### Recommendation
Add the same end-of-function refund found in the canonical implementation: after the fee-token escrow block, if `msgValue > 0`, transfer it back to `msg.sender` (or revert with a strict `msg.value` equality check for stricter safety), consistent with `evm/src/apps/IntentGatewayV2.sol`'s pattern.

### Proof of Concept
1. User calls `placeOrder{value: order.inputs[0].amount + extra}(order, graffiti)` on the Tron `IntentGatewayV2` where `order.inputs[0].token == address(0)` (native ETH input), sending `extra` wei beyond the required input amount.
2. In the non-predispatch branch, only `order.inputs[i].amount` is deducted from `msgValue`; `extra` remains in `msgValue`. [6](#0-5) 
3. If `order.fees == 0`, the fee-escrow branch is skipped entirely, and the function proceeds straight to `emit OrderPlaced` with no refund of the remaining `msgValue`. [7](#0-6) 
4. The `extra` wei stays permanently locked in the contract's balance, with no code path returning it to the user.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-411)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-506)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
