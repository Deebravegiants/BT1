Found the analog. The Tron variant of `IntentGatewayV2.sol` (`evm/tron/contracts/apps/IntentGatewayV2.sol`) reproduces exactly the fund-loss pattern described in the report: when a user places an order and pays the solver fee with native token via `swapETHForExactTokens`, the contract never accounts for or refunds unspent `msgValue`. The main EVM contract (`evm/src/apps/IntentGatewayV2.sol`) correctly refunds leftover `msgValue` back to `msg.sender` after the fee swap, but the Tron port omits that refund step entirely.

### Title
Unrefunded excess native token payment causes permanent loss of funds in Tron `IntentGatewayV2.placeOrder()` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
In the Tron variant of `IntentGatewayV2.sol`, `placeOrder()` accepts native token (`msg.value`) to cover native inputs and, optionally, the solver fee via a Uniswap `swapETHForExactTokens` call. Unlike the canonical EVM implementation, the Tron contract never tracks `amounts[0]` returned by the swap nor refunds any leftover `msgValue` to the caller. Any native token sent beyond what is strictly required for inputs plus the exact fee-swap cost becomes permanently stuck in the contract, exactly mirroring the Allo `_createPool` bug class where excess ETH sent alongside a fee payment is silently absorbed rather than returned.

### Finding Description
`placeOrder()` computes `msgValue` from `msg.value` and deducts native input amounts from it: [1](#0-0) 

When `order.fees > 0` and the caller still has `msgValue > 0`, the contract swaps native tokens for the exact fee-token amount needed via Uniswap: [2](#0-1) 

Critically, the call to `swapETHForExactTokens{value: msgValue}(order.fees, ...)` sends the *entire remaining* `msgValue` as the swap's `value`, but `swapETHForExactTokens` only consumes as much ETH as is needed to obtain `order.fees` of the output token (`amounts[0]`), and normally refunds unused ETH to `msg.sender` of the swap call — which here is the `IntentGatewayV2` contract itself, not the original caller. The Tron contract:
1. Never reads the `amounts` return value from the swap.
2. Never reduces `msgValue` by `amounts[0]`.
3. Never checks or refunds any leftover `msgValue`/swap-refunded ETH back to `msg.sender`.

By contrast, the reference EVM implementation in `evm/src/apps/IntentGatewayV2.sol` explicitly captures the swap output and refunds the remainder: [3](#0-2) 

The Tron version is missing both the `msgValue -= amounts[0]` accounting and the final refund block, so any native token sent in excess of the sum of input amounts and the exact wei needed to buy `order.fees` worth of fee tokens is left stranded in the contract balance, unrecoverable by the order placer.

### Impact Explanation
Any user placing an order with a native-token fee payment on the Tron deployment of `IntentGatewayV2` who sends more native token than the exact minimum required (which is the normal case, since callers cannot know the exact swap price in advance and typically send a buffer) will permanently lose the excess. This is a direct, unprivileged loss of user funds triggered by a single `placeOrder()` transaction, matching the "concrete theft or permanent freezing of funds" acceptance criteria. Given `placeOrder` is a primary, frequently-used entry point, this is systemic rather than an edge case.

### Likelihood Explanation
High. This is triggered by ordinary usage: any caller funding the solver fee with native tokens (`msgValue > 0` branch) who doesn't send the exact wei-precise amount for the Uniswap swap will lose funds. Since Uniswap swap costs depend on live pool reserves at execution time, it is effectively impossible for a caller to send the exact amount, making this occur on nearly every native-fee order placement.

### Recommendation
Mirror the reference EVM implementation: capture the `amounts` array returned by `swapETHForExactTokens`, deduct `amounts[0]` from `msgValue`, and refund any remaining `msgValue` to `msg.sender` after all fee/input processing completes, e.g.:
```solidity
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
    order.fees, path, address(this), block.timestamp
);
msgValue -= amounts[0];
...
if (msgValue > 0) {
    _sendValue(msg.sender, msgValue);
}
```

### Proof of Concept
1. Governance configures a native-fee-payable order flow on the Tron `IntentGatewayV2` deployment with `order.fees = X` (some fee-token amount).
2. A user calls `placeOrder{value: Y}(order, graffiti)` where `Y` covers native inputs plus a buffer for the fee swap (e.g., `Y = inputAmount + 1.5 * expectedSwapCost`), since the exact swap cost cannot be predicted precisely on-chain ahead of execution.
3. Inside `placeOrder`, after deducting native inputs, `msgValue = Y - inputAmount` is passed entirely as `value` to `swapETHForExactTokens{value: msgValue}(order.fees, ...)`.
4. The swap only spends `amounts[0] < msgValue` wei to acquire exactly `order.fees` of the fee token; the router refunds the difference to the caller of the swap, which is the `IntentGatewayV2` contract (`msg.sender` in the router's context), not the original user.
5. Because the contract never reads `amounts[0]` nor performs any refund logic, the refunded ETH remains in the `IntentGatewayV2` contract's balance.
6. The user's escrowed order and events reflect only the intended input/fee amounts; the excess native token sent is unaccounted for and cannot be withdrawn by the user, resulting in permanent loss of the surplus funds — directly analogous to the Allo `_createPool` `NOT_ENOUGH_FUNDS` check flaw where excess ETH sent for `baseFee + _amount` was stranded in the `Allo` contract.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-488)
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
```

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
