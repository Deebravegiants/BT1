Found it. `EvmHost.dispatch(DispatchPost)` and `dispatch(DispatchGet)` call the standard Uniswap V2 router's `swapETHForExactTokens` with the caller's full `msg.value` as `amountInMax`, but never refund the leftover ETH to the original caller.

### Title
Leftover ETH from native-fee swap is permanently stuck in EvmHost - (File: evm/src/core/EvmHost.sol)

### Summary
When a user dispatches a POST or GET request and pays the relayer fee in native token (`msg.value > 0`), `EvmHost` swaps ETH for the exact `feeToken` amount needed via the standard Uniswap V2 router. The router's `swapETHForExactTokens` refunds unspent ETH to `msg.sender`, which in this call context is `EvmHost` itself (not the original transaction sender), so any overpayment is trapped in the contract with no sweep mechanism, unlike the analogous over-supplied-swap-input dust bug identified in the source report.

### Finding Description [1](#0-0) 
`dispatch(DispatchPost)` calls:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
```
The standard `UniswapV2Router02.swapETHForExactTokens` implementation requires exactly `amountOut` (here `post.fee`) of the destination token and refunds any leftover ETH to `msg.sender` of the call — which, since `EvmHost` is the direct caller of the router, is `EvmHost`, not the original user who supplied `msg.value` to `dispatch()`. The same pattern exists in `dispatch(DispatchGet)` at [2](#0-1) .

Neither function tracks a "balance before" the swap nor forwards the router's refund back to `_msgSender()`. Unlike the IntentGatewayV2 code paths, which carefully snapshot balances and either emit `DustCollected` or refund overpayment (`_sendValue(msg.sender, msgValue)`, as seen in [3](#0-2)  and tested in `testFillOrder_RefundsSolverExcessNativeToken`), `EvmHost.dispatch` has no equivalent refund-to-caller or sweep-to-payer logic. Any ETH sent beyond what the AMM needs to buy `post.fee`/`get.fee` worth of fee token is retained by `EvmHost` and is not attributable to or recoverable by the paying user.

### Impact Explanation
This is directly reachable by any unprivileged user dispatching a POST or GET request and paying in native token — the exact "purchaser of bandwidth" pathway called out in scope. Any overestimate of the required ETH (unavoidable in practice, since callers must estimate `msg.value` against a live AMM price that can move between quote and execution, and Uniswap does not allow supplying an exact amount) results in permanent loss of the difference, with no sweep or refund path, causing permanent freezing/loss of user funds at every single native-fee dispatch call. Given that dispatch is the core, most frequently used function of the entire ISMP messaging system, this could accumulate significant value stuck in the contract over time, unclaimable by both users and the protocol (no sweep function targets this contract's ETH balance is confirmed in the reviewed code).

### Likelihood Explanation
High. This triggers on the ordinary, encouraged usage pattern documented in `docs/content/developers/evm/messaging/post-requests.mdx` — "if native tokens are supplied, it will perform a swap under the hood using the local uniswap router" — and requires no attacker, just a normal user slightly over-supplying `msg.value` to guard against slippage/price movement between fee quoting and transaction execution (a standard and recommended practice for AMM-based swaps that use a maximum-input cap).

### Recommendation
After the `swapETHForExactTokens` call, measure the router's returned "amounts spent" (the router returns `amounts[]` with `amounts[0]` = ETH actually spent) or the pre/post `address(this).balance`, and refund any leftover ETH to `_msgSender()` (or `post.payer`/`get.payer`) at the end of `dispatch(DispatchPost)` and `dispatch(DispatchGet)`, mirroring the sweep/refund pattern already used in `IntentGatewayV2`/`IntentsBase`.

### Proof of Concept
1. Compute `feeToken` amount required for `post.fee` and note the current ETH/feeToken AMM price.
2. Call `dispatch(DispatchPost)` with `msg.value` intentionally higher than the exact ETH needed (e.g., add 20% buffer to protect against slippage, a normal integration pattern since the exact required ETH cannot be known atomically without a prior on-chain quote call).
3. `IUniswapV2Router02.swapETHForExactTokens` executes, buys exactly `post.fee` feeToken, and refunds unspent ETH — but to `msg.sender` of the swap call, i.e., `EvmHost`.
4. Observe `address(EvmHost).balance` increases by the refunded amount and is never returned to the caller; the caller's transaction shows no ETH refund, permanently losing the overpaid amount.

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L139-142)
```text
        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
