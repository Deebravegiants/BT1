Based on my investigation, this is a valid analog in `IntentGatewayV2.sol`, reachable directly from the unprivileged `placeOrder` entry point (an intent solver/order-placer path).

### Title
Deadline parameter set to `block.timestamp` in `placeOrder`'s Uniswap V2 fee swap enables MEV/sandwich exploitation of the fee-token swap - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
When a user places an order with `order.fees > 0` and pays with native token (`msgValue > 0`), `placeOrder` swaps native token for the protocol fee token via `IUniswapV2Router02.swapETHForExactTokens`, passing `block.timestamp` directly as the swap `deadline` argument.

### Finding Description
In `placeOrder`, the fee-collection branch performs:
```solidity
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
    order.fees, path, address(this), block.timestamp
);
``` [1](#0-0) 

Using `block.timestamp` as the swap deadline provides no real protection: the deadline is evaluated against the timestamp of the block the transaction ultimately lands in, which is always equal to (or effectively concurrent with) the value passed. This means a validator/block-builder who can control the ordering or timing of transaction inclusion (e.g., holding the transaction, or a searcher sandwiching it) is never blocked by this deadline check, since it trivially always passes regardless of how long the transaction sat pending. This is the exact bug class from the referenced Vyper `SwapRouter._direct_swap` report, transplanted here into the EVM intent gateway's Uniswap V2 fee swap.

Note that `amountOut` (`order.fees`) is fixed and `amountInMaximum` is the full `msgValue` sent by the user (there is no explicit maximum input cap chosen by the user beyond whatever native value they attach), so the user has no way to bound how much ETH they might be forced to spend if the swap is delayed and pool price has moved unfavorably; this exacerbates the missing-deadline defect. This code path is reachable by any unprivileged user calling `placeOrder` directly.

### Impact Explanation
A user placing an order with native-token fee payment can receive a worse execution price on the fee-token swap than intended (spending more ETH than expected, up to the full `msgValue`, for the fixed `order.fees` amount of fee tokens) if a validator/searcher delays or sandwiches the transaction. This directly diminishes user funds during otherwise-legitimate order placement, satisfying "concrete theft ... of funds" via price manipulation. It's scoped to the fee-swap sub-amount of a transaction rather than a systemic protocol break, which is why this remains Medium severity, consistent with the original report's rating.

### Likelihood Explanation
Likelihood is moderate: this branch triggers on every `placeOrder` call where `order.fees > 0` and the user pays fees in native token — a common path for cross-chain intent creation. Exploitation requires a searcher/validator capable of observing the pending transaction and sandwiching the embedded Uniswap V2 swap, which is a well-established and low-cost MEV technique on public EVM chains.

### Recommendation
Add a user-supplied `deadline` (or a bounded max-input) parameter to the `Order` struct or as a `placeOrder` argument, and pass that value to `swapETHForExactTokens` instead of `block.timestamp`, enforcing `require(deadline >= block.timestamp)` semantics as recommended in the original report. Additionally, consider letting the caller specify an explicit `amountInMaximum` for the fee swap rather than implicitly using the entire `msgValue`.

### Proof of Concept
1. User calls `placeOrder` with `order.fees = X` (fee-token amount) and attaches `msg.value` in native token, with no predispatch calldata.
2. The transaction reaches the mempool; a validator/MEV searcher observes it and either delays inclusion or sandwiches the pending Uniswap V2 pool with buy/sell trades that move the ETH/feeToken price against the user.
3. When `placeOrder`'s internal `swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)` executes, `block.timestamp` at execution time trivially satisfies the deadline check regardless of the delay, so the swap proceeds at the manipulated price.
4. The user pays more ETH (up to the full `msgValue`) than they would have at the original quoted price for the same `order.fees` amount of fee token, with the excess captured by the attacker via the sandwich, and only the leftover `msgValue - amounts[0]` refunded. [2](#0-1)

### Citations

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
