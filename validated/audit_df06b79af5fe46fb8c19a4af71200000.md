## Analysis

I compared the ERC20-vs-native-token handling in `placeOrder()` across the two EVM `IntentGatewayV2` implementations. Both accept a mix of native-token and ERC20 `order.inputs`/`order.predispatch.assets`/`order.fees` and track a running `msgValue` counter to know how much of `msg.value` has been consumed.

In the canonical implementation, after escrowing inputs and (optionally) swapping leftover ETH for the fee token, any leftover native value is explicitly swept back to the caller: [1](#0-0) 

The Tron port implements the exact same fee/escrow accounting logic (`msgValue` tracking, `swapETHForExactTokens`, `_orders[commitment][TRANSACTION_FEES]`), but the function ends immediately after emitting `OrderPlaced` — there is no equivalent refund step: [2](#0-1) 

### Title
Unrefunded excess native-token value permanently stuck in `IntentGatewayV2.placeOrder()` (Tron) - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`placeOrder()` in the Tron `IntentGatewayV2` accepts `msg.value` to cover native-token order inputs, predispatch assets, and fees, tracking consumption via a local `msgValue` counter. Unlike the canonical EVM implementation, it never returns any unconsumed portion of `msg.value` to the caller.

### Finding Description
Both `IntentGatewayV2.placeOrder()` implementations decrement a local `msgValue` variable as native-token inputs/predispatch assets are consumed [3](#0-2) , and optionally consume more of it via `swapETHForExactTokens` to pay `order.fees` in the fee token [4](#0-3) . `swapETHForExactTokens` only spends the exact ETH amount required to obtain `order.fees` output tokens; any excess ETH sent for the swap, plus any leftover `msgValue` that was never consumed by an input or fee (e.g., an all-ERC20 order where the user mistakenly attaches `msg.value`, or a native-token order where the user overpays), is retained in the contract's balance. The canonical (non-Tron) contract explicitly sweeps this remainder back to `msg.sender` (`_sendValue(msg.sender, msgValue)`), but this step is absent from the Tron contract's `placeOrder()` — execution falls straight through to `emit OrderPlaced(...)` with no accounting or return of the leftover value. Since `_orders[commitment][...]` only records amounts actually required for escrow, this residual native balance is never tracked anywhere and becomes permanently unrecoverable by the depositor, mirroring the `receiveFunds()` root cause in the referenced report: value sent that does not match the code path that "spends" it is silently stranded in the contract.

### Impact Explanation
Any unspent/overpaid native token (TRX) sent with a `placeOrder()` call is permanently locked in the `IntentGatewayV2` contract with no path to recovery for the depositor — a direct, unbacked loss of user funds. This can be triggered unintentionally (e.g., a wallet/dApp integration that always attaches a fee buffer in native currency, or a user overestimating the Uniswap swap cost for `order.fees`), so it is reachable by any ordinary order-placing user, not just an attacker.

### Likelihood Explanation
High likelihood of accidental triggering: any caller who slightly overestimates the native-token amount needed for the swap-based fee payment, or who sends `msg.value` for an order whose inputs/fees are entirely ERC20-denominated, loses that value with no revert and no refund. No malicious actor is required.

### Recommendation
Add the same refund step present in the non-Tron implementation: after settling inputs and fees, if `msgValue > 0`, return it to `msg.sender` via a low-level `call`/`_sendValue`, mirroring: [1](#0-0) 

### Proof of Concept
1. Caller invokes `placeOrder(order, graffiti)` on the Tron `IntentGatewayV2` with `order.inputs` entirely ERC20 (no `address(0)` token entries) and `order.fees == 0`, but attaches `msg.value = 1 TRX` by mistake (or a wallet UI always includes a small native buffer).
2. In the "no predispatch" branch, the loop only decrements `msgValue` for `token == address(0)` entries — since there are none, `msgValue` remains `1 TRX` throughout [5](#0-4) .
3. `order.fees == 0` skips the fee-swap branch entirely [4](#0-3) .
4. Execution proceeds directly to `emit OrderPlaced(...)` with no refund of the `1 TRX` [6](#0-5) .
5. The `1 TRX` remains in the contract's balance, uncredited to any `_orders[...]` slot and with no function exposed to recover it — it is permanently lost.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L388-411)
```text
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
