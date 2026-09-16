### Title
Excess native-token payment in `EvmHost.dispatch()`/`increaseFee()` is permanently locked in `EvmHost` instead of being refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and the relayer-fee top-up path all accept `msg.value` and swap it for the exact fee-token amount required via `IUniswapV2Router02.swapETHForExactTokens`. Uniswap V2's router refunds unspent ETH to its immediate caller — here that is `EvmHost` itself, not the end user who originated the transaction. Because `EvmHost` never forwards or accounts for this refunded ETH, any native-token overpayment is silently and permanently stranded in the `EvmHost` contract, exactly analogous to the Flayer M-6 finding where leftover tokens from a Uniswap V4 liquidity/price computation were never returned to the caller.

### Finding Description
`dispatch(DispatchPost)` and `dispatch(DispatchGet)` both contain this pattern: [1](#0-0) [2](#0-1) 

In both functions, the full `msg.value` is forwarded to `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. The Uniswap V2 Router's `swapETHForExactTokens` implementation computes the exact ETH amount needed for `post.fee`/`get.fee` output tokens and, if `msg.value` exceeds that amount, refunds the difference to `msg.sender` of the router call — which, since `EvmHost` is the direct caller of the router, is `EvmHost` itself, not the original transaction sender (`_msgSender()`).

Nothing in `dispatch()` reads back this refund or forwards it to the caller: the function proceeds directly to building the request/commitment and emitting events, with no ETH accounting, no `_msgSender().call{value:...}` refund step, and no reconciliation of `address(this).balance` before/after the swap. Any ETH sent in excess of the exact swap requirement is therefore trapped in `EvmHost`'s balance with no code path to recover it for the payer.

This directly mirrors the audited Flayer bug: a swap/liquidity-sizing operation consumes only part of the caller-supplied token/ETH, and the excess is left on the contract with no refund logic — the same root cause (`LiquidityAmounts.getLiquidityForAmounts` leaving dust vs. `swapETHForExactTokens` leaving unspent ETH), just in a different subsystem.

### Impact Explanation
Any unprivileged user who calls `dispatch()` (to submit a POST or GET request) with `msg.value` greater than what is strictly required for the underlying `swapETHForExactTokens` call permanently loses the difference — it becomes stuck in the `EvmHost` contract with no sweep/refund mechanism visible in the surrounding code. This is a direct, permanent freezing-of-funds bug reachable by any single unprivileged dispatch transaction (the entry point explicitly documented for message dispatch: "Payment for the request can be made with either the native token or the feeToken... it will perform a swap under the hood using the local uniswap router"). Given that users must estimate slippage/gas price fluctuations for the swap and typically over-supply `msg.value` as a safety margin, overpayment is a realistic, common occurrence, not an edge case.

### Likelihood Explanation
High. Any caller who is not able to compute the exact required ETH-for-fee-token amount at the block being mined (due to price movement between quote and execution, or simply sending a round/rounded-up `msg.value` for safety) will trigger this loss on every such call. No special privileges, timing, or adversarial setup are required — a normal `dispatch()` call with a slightly generous `msg.value` reproduces the bug.

### Recommendation
After the `swapETHForExactTokens` call, compute the actual ETH refunded to `EvmHost` (e.g., by snapshotting `address(this).balance` before and after the swap, or reading amounts returned by the swap) and immediately forward it back to `_msgSender()` via a low-level call, mirroring the refund pattern already used elsewhere in the codebase (e.g., `IntentGatewayV2`/`IntentsBase` explicitly refunds unspent native token: `if (msgValue > 0) { _sendValue(msg.sender, msgValue); }`, and the `UniV3UniswapV2Wrapper`/`UniV4UniswapV2Wrapper` contracts explicitly refund unspent ETH after swaps). Apply the same fix to both `dispatch(DispatchPost)` and `dispatch(DispatchGet)`, and audit `increaseFee()` (and any other `EvmHost` function using the same swap-with-native-token pattern) for the identical issue.

### Proof of Concept
1. Any user calls `EvmHost.dispatch(DispatchPost memory post)` with `msg.value = X` where `X` is intentionally or accidentally greater than the ETH amount required to obtain `post.fee` fee-tokens via the configured Uniswap V2 pool.
2. Inside `dispatch()`, `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` executes; the router uses only `amountIn <= X` ETH to buy exactly `post.fee` fee tokens, and refunds `X - amountIn` ETH to its caller, `EvmHost`.
3. `EvmHost`'s balance increases by `X - amountIn` with no code reading or forwarding this amount to `_msgSender()`.
4. The request is committed and the function returns normally; the caller has irrecoverably lost `X - amountIn` ETH, now sitting in `EvmHost`'s balance with no sweep/withdraw function reachable by the original payer. [1](#0-0)

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
