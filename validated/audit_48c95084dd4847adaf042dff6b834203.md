## Finding

### Title
`IntentGatewayV2.placeOrder` performs an uncapped-price ETH→feeToken swap with a meaningless deadline, exposing order fee payments to sandwich attacks - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
When a user places an order and pays `order.fees` in native ETH, `placeOrder` swaps ETH for the exact fee-token amount via Uniswap V2, but the swap's implicit price bound and deadline provide no real MEV protection, letting a searcher sandwich the transaction and capture value that would otherwise be refunded to the user.

### Finding Description
In `placeOrder`, when `order.fees > 0` and the caller sent native value, the contract swaps ETH for feeToken using `swapETHForExactTokens`: [1](#0-0) 

The `amountOut` is fixed (`order.fees`), and the router treats the forwarded `msg.value` (here, the leftover `msgValue` after predispatch consumption) as the implicit maximum input; any unspent ETH is later refunded to the user: [2](#0-1) 

Two properties make this a sandwich vector analogous to the referenced yAxis finding (calling a Curve/Uniswap-style swap without computing/enforcing an estimated fair return):
1. `deadline` is passed as `block.timestamp`, which is always satisfied within the same block and provides no protection against the transaction sitting in the mempool while a searcher front-runs it.
2. The effective "slippage bound" is not derived from any on-chain price check or a caller-supplied `amountOutMinimum`/`amountInMaximum` computed against a fair quote — it is simply whatever native value happens to remain in `msgValue`. A searcher can front-run the swap to push the ETH/feeToken price up (within the router's constant-product curve) right up to the edge of `msgValue`, then back-run to restore price, extracting the difference between the fair market price and the buffered `msgValue` as MEV profit. That value comes directly out of what the user would otherwise have received back as a refund.

This mirrors the reported bug class precisely: the protocol interacts with an AMM router on behalf of a user-funded action without computing and enforcing an actual minimum-return / maximum-cost bound tied to a live quote, relying only on an incidental value (`msgValue`) and a no-op deadline.

### Impact Explanation
Any user placing an order with `order.fees` paid in native ETH is exposed to value extraction by MEV searchers during order placement — a single, unprivileged transaction path (`placeOrder`) reachable by any user. The leaked value scales with how much ETH buffer the caller sends above the fair-market fee cost, and is captured entirely by the sandwiching searcher rather than being refunded to the user. This is a direct, protocol-level fund-loss vector for any of the many orders that pay fees in native token, consistent with the "Medium" severity assigned to the original analog finding (value leakage via MEV sandwich, acknowledged and judged valid by the original protocol team).

### Likelihood Explanation
Likelihood is high: `placeOrder` is a permissionless, frequently-used entry point, ETH-fee payment is an explicitly documented and supported flow (fees can be "paid in native ETH"), and sandwiching Uniswap V2 swaps sized in the block is a well-established, low-cost MEV strategy requiring no special access — only observing the mempool for `placeOrder` calls with `msg.value` and a non-trivial `order.fees`.

### Recommendation
- Replace `swapETHForExactTokens(order.fees, path, address(this), block.timestamp)` with a call that uses a real, short-lived `deadline` (e.g., `block.timestamp + maxSwapWindow`), not `block.timestamp` itself.
- Compute an actual maximum acceptable input (`amountInMax`) from an on-chain quote (e.g., `getAmountsIn`) plus an explicit, governance-configured slippage tolerance, and revert if `msgValue` is insufficient to cover it safely — rather than letting the entire leftover `msgValue` act as an implicit, unbounded price ceiling.
- Alternatively, let the caller supply an explicit `amountInMax`/slippage parameter for the fee swap (similar to how `IntentGatewayV2Test.sol` computes `minUsdcAmount` off-chain with a slippage tolerance for user-supplied predispatch swaps), so the contract can reject unfavorable executions instead of silently consuming excess value.

### Proof of Concept
1. User calls `placeOrder` with `order.fees = F` (in `feeToken`) and sends `msg.value = V` in native ETH, where `V` is sized to cover `F` plus a reasonable buffer for normal price movement, expecting the unused remainder to be refunded per [2](#0-1) .
2. A searcher observes the pending transaction, front-runs it with a large ETH→feeToken swap on the same Uniswap V2 pool used by `IDispatcher(hostAddr).uniswapV2Router()` to push the ETH price of `feeToken` up.
3. The `placeOrder` transaction executes `swapETHForExactTokens{value: V}(F, [WETH, feeToken], address(this), block.timestamp)` at [3](#0-2) ; because the price is inflated, `amounts[0]` (actual ETH spent) is much closer to `V` than it would be absent manipulation, shrinking the refund at line 396.
4. The searcher back-runs to sell the `feeToken`/buy back cheap ETH, restoring the pool price and pocketing the difference — value that came out of the user's expected refund, with no revert or protection triggered since `block.timestamp` always satisfies the deadline check and `V` was never tied to a real fair-price bound.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L375-391)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
