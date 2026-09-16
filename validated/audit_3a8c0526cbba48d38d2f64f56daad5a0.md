### Title
Unspent native token overpayment is not refunded in Tron `IntentGatewayV2.placeOrder`, permanently trapping user funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` accepts `msg.value` to cover order inputs (native token) and the optional `order.fees` swap, but unlike the canonical EVM implementation, it never refunds any leftover native token to the caller after escrow and fee accounting complete. Any ETH/TRX sent above what is strictly required (inputs + fee-swap cost) is silently stranded in the contract, exactly the "extra payment is not returned" fund-loss pattern described in the source report.

### Finding Description
`placeOrder` in `evm/tron/contracts/apps/IntentGatewayV2.sol` tracks a local `msgValue` counter, decrementing it as native-token inputs are consumed [1](#0-0) , and again (partially) if fees are paid via a Uniswap swap of native token to fee token [2](#0-1) . After that, the function directly proceeds to emit `OrderPlaced` and returns — there is no step that returns any remaining `msgValue` to `msg.sender` [3](#0-2) .

This is a direct regression relative to the canonical EVM `IntentGatewayV2.placeOrder`, which performs the identical input/fee accounting but explicitly refunds any unspent native value at the end:
```solidity
// Refund any unspent native tokens to the user.
if (msgValue > 0) {
    _sendValue(msg.sender, msgValue);
}
``` [4](#0-3) 

Additionally, when native token is used to pay `order.fees`, the EVM version tracks the exact Uniswap `amounts[0]` consumed and reduces `msgValue` accordingly before the refund check [5](#0-4) , whereas the Tron version doesn't even bother to compute the residual `msgValue` after the swap — it just leaves whatever `msgValue` held at that point in the contract forever [6](#0-5) .

Because `swapETHForExactTokens` only spends up to `order.fees` worth of native token and refunds any Uniswap-level dust back to the caller of the swap (i.e., the `IntentGatewayV2` contract itself, not the user) [6](#0-5) , that dust is retained by the contract with no user-facing sweep path, permanently freezing the user's overpayment. Any user who over-estimates the fee (a common and expected client-side behavior, since exact quotes are discouraged for on-chain use per the docs' warning about `quote()` being sandwich-vulnerable) loses the difference outright.

### Impact Explanation
Users calling `placeOrder` on the Tron deployment with any native-token overpayment (whether for order inputs when combined with fee-token fees, or for the fee-swap leg) permanently lose the excess — it is neither returned to them nor tracked as recoverable dust tied to their commitment. This is a direct, unconditional loss of user funds triggerable by ordinary usage (not requiring any adversarial third party), matching the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
High likelihood: any Tron user who sends slightly more native token than the exact required inputs/fee (which is the normal client behavior since exact fee quoting is explicitly discouraged on-chain in the project's own documentation) will trigger the loss on every such call. No special conditions or malicious actors are needed.

### Recommendation
Mirror the EVM implementation: track the exact amount consumed by the Uniswap swap (`amounts[0]`) when paying `order.fees` with native token, and after all escrow/fee logic, refund any remaining `msgValue` to `msg.sender` via `_sendValue` (or equivalent), exactly as done in `evm/src/apps/IntentGatewayV2.sol` lines 375–397.

### Proof of Concept
1. User calls `placeOrder` on the Tron `IntentGatewayV2` with a native-token input order and `order.fees > 0`, sending `msg.value = inputAmount + feeSwapEstimate + extra` (`extra > 0`) because exact fee amounts cannot safely be quoted on-chain.
2. The function subtracts `inputAmount` from `msgValue`, then calls `swapETHForExactTokens{value: msgValue}(order.fees, ...)`, which spends only enough native token to acquire `order.fees` fee tokens and returns the rest to the `IntentGatewayV2` contract (not the user) [6](#0-5) .
3. Execution falls through directly to `_orders[commitment][TRANSACTION_FEES] = order.fees;` and the `OrderPlaced` emit — no refund path exists [3](#0-2) .
4. The `extra` native token amount is now permanently stuck in the contract with no mapping back to the user or their commitment, unlike the EVM sibling contract which would have returned it via `_sendValue(msg.sender, msgValue)`.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L375-392)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L393-397)
```text

        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
