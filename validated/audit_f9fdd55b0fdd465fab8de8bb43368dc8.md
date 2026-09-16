### Title
EvmHost dispatch/fundRequest fail to return unused native token after `swapETHForExactTokens`, permanently trapping user overpayment - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` accept native token via `msg.value` and swap it for the exact `feeToken` amount needed using `swapETHForExactTokens`. Like the DODORouteProxy finding, any unused native token from this exact-out swap is not returned to the original caller — it is refunded by the Uniswap router to `msg.sender` of the swap call, which is `EvmHost` itself, not the end user who paid the extra ETH.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

and identically in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

All three functions call `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`. The standard UniswapV2Router02 implementation of `swapETHForExactTokens` refunds any unspent ETH (`msg.value - amounts[0]`) via `TransferHelper.safeTransferETH(msg.sender, ...)`, where `msg.sender` from the router's perspective is `EvmHost`, not the EOA/contract that originally called `dispatch`/`fundRequest`. Unlike `IntentGatewayV2`'s `placeOrder`/`fillOrder` — which explicitly track `msgValue` and refund the remainder to the original caller via `_sendValue(msg.sender, msgValue)` (see `evm/src/apps/intentsv2/IntrinsicIntents.sol:139-142` and `evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2313-2347`) — none of `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest` perform any post-swap accounting or forwarding of the refunded ETH back to `_msgSender()`. There is no tracking of `amounts[0]` (actual ETH spent) and no subsequent transfer of the difference to the caller.

### Impact Explanation
Any caller of `dispatch()`/`fundRequest()` who overestimates the native token needed to cover `post.fee`/`get.fee`/`amount` (a common and expected pattern, since callers must send enough ETH to survive slippage in the exact-out swap) permanently loses the unused ETH: it lands in the `EvmHost` contract's own balance instead of returning to the caller. Since `EvmHost` has no mechanism shown here to return this ETH to depositors, and any accumulated balance would be indistinguishable from legitimate protocol funds, this constitutes a permanent, unrecoverable loss of user funds for every over-funded `dispatch`/`fundRequest` call — directly reachable by any unprivileged relayer, app, or user dispatching a POST/GET request or funding a pending request with native token.

### Likelihood Explanation
Likelihood is high: `dispatch()` is the primary, permissionless entry point for posting cross-chain messages and is documented as accepting native token payment (see `evm/src/core/EvmHost.sol:908-920` docstring: "If native tokens are supplied... Will revert if enough native tokens are not provided."). Since the exact amount needed by the exact-out swap fluctuates with AMM price/slippage, callers routinely must send more ETH than the minimum to avoid reverts, guaranteeing dust/excess on nearly every native-token dispatch, compounding into a systemic drain.

### Recommendation
Snapshot `EvmHost`'s ETH balance (or capture `amounts[0]` returned by `swapETHForExactTokens`) before and after the swap in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, and forward the unspent remainder (`msg.value - amounts[0]`) back to `_msgSender()`, mirroring the pattern already used in `IntentGatewayV2`'s `placeOrder`/`fillOrder` (`_sendValue(msg.sender, msgValue)`).

### Proof of Concept
1. A user calls `EvmHost.dispatch(DispatchPost{..., fee: 100e18})` sending `msg.value = 1 ether` to cover the fee-token swap, expecting slippage protection.
2. Inside `dispatch`, `EvmHost` calls `swapETHForExactTokens{value: 1 ether}(100e18, [WETH, feeToken], address(this), deadline)`.
3. Suppose only `0.05 ether` is actually needed to obtain `100e18` feeToken; the router refunds `0.95 ether` — but to `msg.sender` of the router call, i.e., `EvmHost`, not the original user.
4. `dispatch` completes and returns; the user has spent `1 ether` from their wallet but the request is only funded with `100e18` feeToken plus receives no ETH back. The `0.95 ether` remains in `EvmHost`'s balance with no code path returning it to the user.
5. Repeating this across all `dispatch`/`fundRequest` calls accumulates trapped ETH permanently, unlike `IntentGatewayV2.placeOrder`, whose analogous test `testPlaceOrder_RefundsExcessNativeToken` (`evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2313-2347`) proves the correct behavior is expected elsewhere in the codebase but is missing here.

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
