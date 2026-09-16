This is a valid analog. `EvmHost` is configured with a `uniswapV2` router address that can point at `UniV3UniswapV2Wrapper`, a Uniswap-V2-interface-compatible contract that internally routes through Uniswap V3's `exactOutputSingle`. This wrapper's `swapETHForExactTokens` hardcodes `sqrtPriceLimitX96: 0` [1](#0-0) , and this is precisely the function `EvmHost.dispatch`, `fundRequest`, `IntentGatewayV2.placeOrder` call when a caller pays with native token [2](#0-1) [3](#0-2) [4](#0-3) .

### Title
Uniswap V3 `sqrtPriceLimitX96` hardcoded to `0` in `UniV3UniswapV2Wrapper` exposes unprivileged native-fee payers to sandwich/slippage risk - (File: `evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol`)

### Summary
`UniV3UniswapV2Wrapper` is a V2-router-compatible facade over Uniswap V3, deployable as the `uniswapV2` address stored in `EvmHost`'s `HostParams` and consumed by `IDispatcher.uniswapV2Router()`. Its `swapETHForExactTokens` (used for native-token fee payment) and `swapExactTokensForETH` both build V3 swap params with `sqrtPriceLimitX96: 0`, disabling the one on-chain guard against price-impact/MEV during the swap.

### Finding Description
Any unprivileged account calling `EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, `EvmHost.fundRequest`, or `IntentGatewayV2.placeOrder` with `msg.value > 0` triggers a call into `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(...)` [2](#0-1) . When the deployment's configured `uniswapV2` router is `UniV3UniswapV2Wrapper` (as provided by `evm/script/DeployUniV3Wrapper.s.sol`), that call resolves to:

```solidity
IV3SwapRouter.ExactOutputSingleParams memory params = IV3SwapRouter.ExactOutputSingleParams({
    tokenIn: weth,
    tokenOut: path[1],
    fee: _params.maxFee,
    recipient: recipient,
    amountOut: amountOut,
    amountInMaximum: msg.value,
    sqrtPriceLimitX96: 0
});
``` [5](#0-4) 

`sqrtPriceLimitX96 = 0` disables Uniswap V3's built-in price-limit protection for the swap leg, meaning the pool can be pushed to any price during execution as long as `amountInMaximum` (== the caller's `msg.value`) is not exceeded. The only slippage bound present is `amountInMaximum = msg.value`, which the caller sets based on an off-chain quote taken before submission — the same pattern flagged in the original Opyn `CrabNetting` finding, where `amountOutMinimum`/`amountInMaximum` alone was deemed an insufficient substitute for a real `sqrtPriceLimitX96`.

The paired `swapExactTokensForETH` function has the identical pattern [6](#0-5) , reachable via `SimplexPaymaster.swapAndDeposit` — though that entry point is treasury-gated and out of scope for this dispatcher-reachability analysis — the `dispatch`/`fundRequest`/`placeOrder` paths through `swapETHForExactTokens` are directly reachable by any unprivileged message dispatcher or order placer.

### Impact Explanation
A caller paying dispatch/order fees in native token via a `UniV3UniswapV2Wrapper`-backed host has no on-chain protection against the pool being pushed to an unfavorable price mid-swap (e.g., a sandwich attacker front-running the swap to move the price, then back-running to profit). Because the swap uses `exactOutputSingle` (fixed `feeToken` output, variable native input up to `amountInMaximum`), a sandwiched transaction could consume up to the full `amountInMaximum` in native token for the same fixed fee-token output, meaning the dispatcher/order-placer overpays native token to an MEV searcher rather than losing dispatch functionality outright. This is a fund-loss (excess value extraction) issue for the fee-payer on every native-paid dispatch, get, fundRequest, or order-placement call routed through this wrapper.

### Likelihood Explanation
Likelihood is contingent on a specific host deployment configuration: the `uniswapV2` address in `HostParams` must point at `UniV3UniswapV2Wrapper` rather than a genuine Uniswap V2 router. The repository ships a dedicated deploy script for this wrapper (`evm/script/DeployUniV3Wrapper.s.sol`), indicating it is an intended, supported production configuration on chains lacking sufficient V2 liquidity. Every native-token dispatch/get/fundRequest/order-placement call on such a deployment triggers the vulnerable path, and MEV searchers on public mempools routinely sandwich unprotected swaps, so likelihood is Medium-to-High wherever this wrapper is actually deployed as the router.

### Recommendation
Add a caller-supplied (or oracle-derived, conservatively bounded) `sqrtPriceLimitX96` parameter to `swapETHForExactTokens` and `swapExactTokensForETH` in `UniV3UniswapV2Wrapper`, analogous to the Opyn fix: extend the function signatures (or an auxiliary params struct) to accept a price limit and thread it into `IV3SwapRouter.ExactOutputSingleParams`/`ExactInputSingleParams` instead of hardcoding `0`. Since these wrapper functions preserve the legacy V2 ABI (constrained by `IUniswapV2Router02` compatibility) for `EvmHost`, consider deriving a bounded default limit on-chain from `IQuoterV2`/pool state at call time, or expose it via a settable wrapper-level parameter with sane bounds, rather than leaving it fully permissive.

### Proof of Concept
1. Deploy `EvmHost` with `HostParams.uniswapV2` set to a `UniV3UniswapV2Wrapper` instance (per `evm/script/DeployUniV3Wrapper.s.sol`).
2. An attacker observes a pending `EvmHost.dispatch{value: msg.value}(DispatchPost{...})` transaction from a victim in the mempool.
3. Attacker front-runs with a large swap in the same V3 pool (WETH/feeToken) to move the price against the victim, then back-runs to restore it.
4. Because `sqrtPriceLimitX96 = 0`, the victim's `exactOutputSingle` call at `evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol:125-133` executes at the manipulated price, consuming a larger portion of the victim's supplied `msg.value` (up to `amountInMaximum`) for the same fixed `post.fee` output — the attacker profits the price-impact difference while the victim's dispatch still succeeds but at increased native-token cost.

### Citations

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L114-133)
```text
    function swapETHForExactTokens(uint256 amountOut, address[] calldata path, address recipient, uint256 deadline)
        external
        payable
        returns (uint256[] memory)
    {
        address weth = _params.WETH;
        if (path[0] != weth) revert InvalidWethAddress();

        (bool sent,) = weth.call{value: msg.value}("");
        if (!sent) revert DepositFailed();

        IV3SwapRouter.ExactOutputSingleParams memory params = IV3SwapRouter.ExactOutputSingleParams({
            tokenIn: weth,
            tokenOut: path[1],
            fee: _params.maxFee,
            recipient: recipient,
            amountOut: amountOut,
            amountInMaximum: msg.value,
            sqrtPriceLimitX96: 0
        });
```

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L181-189)
```text
        IV3SwapRouter.ExactInputSingleParams memory params = IV3SwapRouter.ExactInputSingleParams({
            tokenIn: token,
            tokenOut: weth,
            fee: _params.maxFee,
            recipient: address(this),
            amountIn: amountIn,
            amountOutMinimum: amountOutMin,
            sqrtPriceLimitX96: 0
        });
```

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

**File:** evm/src/core/EvmHost.sol (L1031-1041)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L375-386)
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
```
