### Title
Excess native ETH sent to `EvmHost.dispatch()`/`fundRequest()` is trapped in the Host contract instead of being refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept `msg.value` and forward the *entire* `msg.value` into `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(post.fee, ...)` (or `amount` for `fundRequest`), but never check or reconcile the actual native value sent against the fee/amount that is actually required, and never refund any leftover ETH to the original caller.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 
the function swaps `msg.value` of native ETH for exactly `post.fee` units of `feeToken()` via `swapETHForExactTokens`. The same pattern repeats in `dispatch(DispatchGet)`: [2](#0-1)  
and in `fundRequest()`: [3](#0-2) 

`UniswapV2Router02.swapETHForExactTokens` only consumes the ETH needed to produce the exact output amount and refunds any unused ETH — but it refunds to `msg.sender` of the router call, which here is the `EvmHost` contract itself (since `EvmHost` calls the router directly with `{value: msg.value}`), not the end user who called `dispatch`/`fundRequest`. There is no code path in these three functions (nor evident elsewhere in `EvmHost.sol`, based on available search results) that captures this Uniswap refund and forwards it back to `_msgSender()`/`post.payer`. This differs from the reference report's exact root cause (an unchecked `amount` parameter divorced from `msg.value`), but is the same class of bug: `msg.value` is not correctly synchronized with the actual fee/amount required, and the delta becomes a fund loss rather than being returned to the payer. Contrast this with the pattern implemented correctly elsewhere in the same codebase (e.g. `IntentGatewayV2.placeOrder`, `ExtrinsicIntents._fillCrossChain`, `IntrinsicIntents._fillSameChain`), where `msgValue` is tracked, decremented per use, and any leftover is explicitly refunded via `_sendValue(msg.sender, msgValue)`.

### Impact Explanation
Any user or app who overestimates the native ETH needed to cover a POST/GET dispatch fee or a `fundRequest` top-up (e.g., due to slippage buffering, or simply sending more than the exact `getAmountsIn` quote) permanently loses the difference — it stays stuck as `EvmHost` contract balance with no user-facing withdrawal/refund mechanism identified. Since `dispatch()` is the base entry point used pervasively by all Hyperbridge apps sending POST/GET requests with native payment (including `HyperFungibleToken`/`WrappedHyperFungibleToken.send()` and any `HyperApp`-based integration), this affects a wide surface of unprivileged callers on every dispatch that pays with native token. This is a concrete, reachable fund-loss condition triggered by a single dispatched request.

### Likelihood Explanation
High likelihood of occurrence in practice: the docs explicitly warn against calling `quote()` on-chain due to sandwich-attack risk and recommend off-chain estimation with buffer margin — meaning users/integrators are encouraged to send more `msg.value` than the exact amount needed "to be safe," which is precisely the scenario that causes fund loss here. Any slippage between quote-time and dispatch-time price, or any deliberate over-provisioning, results in ETH being silently retained by the Host contract.

### Recommendation
Track the actual amount consumed by the swap (the return value of `swapETHForExactTokens`, which is `amounts[0]`, the ETH actually spent) and refund `msg.value - amounts[0]` back to `_msgSender()` (or `post.payer`) in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, mirroring the `msgValue` tracking/refund pattern already used in `IntentGatewayV2.sol` and `IntentsBase`/`ExtrinsicIntents.sol`/`IntrinsicIntents.sol`.

### Proof of Concept
1. User calls `EvmHost.dispatch(DispatchPost)` with `post.fee = 100` fee-token-equivalent and sends `msg.value = 2 ETH`, while the actual ETH needed to buy 100 fee-token units is only `0.5 ETH` (e.g., due to conservative off-chain slippage buffering as the docs recommend).
2. `swapETHForExactTokens{value: 2 ETH}(100, path, address(this), ...)` executes: it spends `0.5 ETH`, and refunds the remaining `1.5 ETH` to `msg.sender` of the router call — which is `EvmHost`, not the user.
3. The `1.5 ETH` refund accumulates in `EvmHost`'s balance. Based on the code reviewed, there is no subsequent step that credits or returns this ETH to the user; it is not part of `FeeMetadata`, not part of any withdrawable balance tied to the payer.
4. The user has lost `1.5 ETH` with no recovery path, confirming the fund-loss impact.

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

**File:** evm/src/core/EvmHost.sol (L1031-1042)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }
```
