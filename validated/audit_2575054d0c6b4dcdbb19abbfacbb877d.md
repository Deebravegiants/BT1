### Title
Overpaid native ETH sent to `EvmHost.dispatch()` is refunded to the host contract instead of the caller and becomes permanently stuck - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` forward the caller's entire `msg.value` to `swapETHForExactTokens`, requesting an *exact* fee-token output (`post.fee` / `get.fee`). Uniswap V2's `swapETHForExactTokens` only consumes the ETH required to produce that exact output and refunds any leftover ETH — but since `EvmHost` itself is the immediate caller of the router, the refund lands on `EvmHost`, not on the original transaction sender. This is analogous to the reported `MarginTrading.withdrawETH` bug class: native value enters a contract through a path that has no corresponding, reachable withdrawal mechanism for the original depositor, so it becomes stranded.

### Finding Description
```solidity
function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
    if (msg.value > 0) {
        address[] memory path = new address[](2);
        address uniswapV2 = _hostParams.uniswapV2;
        path[0] = IUniswapV2Router02(uniswapV2).WETH();
        path[1] = feeToken();
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            post.fee, path, address(this), block.timestamp
        );
    } else if (post.fee > 0) {
        IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
    }
    ...
``` [1](#0-0) 

The identical pattern exists in the GET-request dispatch path: [2](#0-1) 

`swapETHForExactTokens` guarantees only that `post.fee` amount of `feeToken` is produced; any unspent portion of `msg.value` is returned by the router to whichever address called it (`address(this)`, i.e. `EvmHost`), not to `_msgSender()`. Every app-level entry point that forwards native value into `dispatch()` (e.g. `IntentGatewayV2.placeOrder`, `WrappedHyperFungibleToken.send`, cross-chain intent fillers, the LayerZero endpoint adapter) sizes `msg.value` as an *upper bound* / fee-quote rather than an exact amount, precisely because the actual swap cost is unknown ahead of time (price impact, slippage) — callers are expected to overpay slightly and get the difference refunded, matching patterns seen elsewhere in the codebase (e.g. `IntentGatewayV2.placeOrder`'s explicit `_sendValue(msg.sender, msgValue)` refund after its own `swapETHForExactTokens` call). [3](#0-2) 

`EvmHost.dispatch()` performs no equivalent refund step and has no `receive()`-triggered accounting that credits the refunded ETH back to `_msgSender()`. Any leftover wei is simply absorbed into `EvmHost`'s balance with no on-chain record of who is owed it, and — unlike the `MarginTrading.withdrawETH` case where at least an owner-only withdrawal existed for WETH-backed balances — there is no code path in `EvmHost` that reconciles or returns this specific stray native balance to the original payer.

### Impact Explanation
Any unprivileged caller that dispatches a POST or GET request through `EvmHost.dispatch()` with `msg.value` even slightly larger than what the underlying Uniswap V2 swap consumes for the exact fee amount loses the difference permanently. Because virtually every fee-paying entry point in the system (`IntentGatewayV2`, `WrappedHyperFungibleToken`, LayerZero adapter, cross-chain intents) ultimately routes native-fee payments through this exact `EvmHost.dispatch()` call, this is a systemic freezing-of-funds bug reachable by ordinary users on every single dispatched cross-chain message paid for in native token. Given routine price movement/slippage between fee-quote time and execution time, overpayment is the expected common case, not an edge case.

### Likelihood Explanation
High likelihood — this triggers on the ordinary "pay dispatch fee with native token" path used throughout the protocol whenever a caller cannot predict the exact swap execution price and pads `msg.value`, which is standard practice for any exact-output-swap-based fee flow.

### Recommendation
After the `swapETHForExactTokens` call, compute the leftover ETH via `address(this).balance` (or track pre/post balance) and refund the excess to `_msgSender()` (or `post.payer`/`get.context`'s sender) via a safe ETH transfer, mirroring the refund logic already implemented in `IntentGatewayV2._sendValue` and `IntentsBase._sendValue`. Alternatively, switch to `swapExactETHForTokens`-style accounting with an explicit `amountInMax` and refund the delta, or expose a per-payer withdrawable-balance mapping if refunding synchronously is not feasible.

### Proof of Concept
1. A user (or app such as `IntentGatewayV2`/`WrappedHyperFungibleToken`) calls `EvmHost.dispatch(DispatchPost)` with `msg.value = X`, where `X` comfortably covers `post.fee` worth of fee-token via the configured Uniswap V2 pool.
2. Internally, `IUniswapV2Router02.swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` executes: it only spends `amountIn < X` ETH to produce exactly `post.fee` fee tokens, and refunds `X - amountIn` ETH to `msg.sender` of the router call, which is `EvmHost`.
3. `EvmHost`'s balance increases by `X - amountIn`; the original caller who supplied `X` receives no refund and has no function available on `EvmHost` to reclaim this ETH.
4. Repeating this across normal usage (any slight overpayment on any POST/GET dispatch) accumulates stranded native ETH inside `EvmHost` indefinitely.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-932)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L974-985)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
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
