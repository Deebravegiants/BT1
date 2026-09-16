## Vulnerability Confirmed: No Expiration Deadline for Uniswap Swaps in `EvmHost`

### Title
No expiration deadline protection for native-token fee swaps in `EvmHost::dispatch()` and `EvmHost::fundRequest()` - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch()` and `EvmHost.fundRequest()` allow any unprivileged caller to pay dispatch/funding fees in native token, which is internally converted to `feeToken()` via `IUniswapV2Router02.swapETHForExactTokens`. Both call sites pass `block.timestamp` as the swap `deadline` argument, which provides no real expiration protection.

### Finding Description
In `dispatch()`, when `msg.value > 0` the contract swaps native ETH for an exact amount of fee tokens through the configured Uniswap V2 router, using `block.timestamp` as the deadline: [1](#0-0) 

The same pattern exists in `fundRequest()`: [2](#0-1) 

Because `deadline` is set to `block.timestamp` rather than to a caller-supplied, bounded future timestamp, Uniswap's `require(deadline >= block.timestamp, 'EXPIRED')` check is evaluated against the *executing* block's own timestamp — it trivially always passes no matter how long a miner/validator withholds the transaction in the mempool before including it. This is exactly the anti-pattern described in the referenced report: the deadline offers no actual freshness guarantee for the swap.

Both `dispatch()` and `fundRequest()` are `external payable` and reachable by any unprivileged caller (any address dispatching a cross-chain POST/GET message or funding an existing request), matching the allowed "EvmHost dispatch and delivery" attack surface.

### Impact Explanation
Because the deadline check can never actually expire the transaction, a block producer (or any actor able to delay/reorder mempool transactions, e.g. via private order flow, MEV bundles, or simply natural mempool latency across congested blocks) can hold a user's `dispatch`/`fundRequest` transaction until market conditions are most unfavorable to the user, then include it. Since the swap is `swapETHForExactTokens` (exact-output, `amountInMaximum = msg.value`), the practical outcomes are:
- The trade executes at a stale/manipulated price within the user's ETH budget, i.e. the user pays the maximum possible ETH for the required fee-token amount, effectively conceding on-chain a possible sandwich/price movement.
- If price moves too far, the call reverts (`INSUFFICIENT_INPUT_AMOUNT`), a griefing/DoS on the fee-payment path for `dispatch`/`fundRequest`.

This causes direct value loss to unprivileged callers paying protocol dispatch fees in native token — a concrete instance of "loss of funds due to no expiration deadline," matching the reported bug class, reachable through the core message-dispatch entrypoint of `EvmHost`.

### Likelihood Explanation
Likelihood is moderate: it requires an adversarial or MEV-aware block producer/relay to intentionally delay inclusion of the `dispatch`/`fundRequest` transaction to a less favorable price point. This is a well-known and economically motivated MEV pattern (time-bandit/deadline-manipulation sandwich), and both functions are freely callable by any address supplying native token as `msg.value`, so the attack surface is broad (every fee-paying dispatcher/relayer using native-token payment).

### Recommendation
Add a caller-supplied `deadline` parameter (bounded to a reasonable near-term window, e.g. `block.timestamp + maxSlippageWindow`) to `DispatchPost`/`fundRequest` inputs, and pass that value to `swapETHForExactTokens` instead of `block.timestamp`, so the Uniswap deadline check provides genuine protection against delayed/held transactions.

### Proof of Concept
1. Caller A calls `dispatch(post)` with `msg.value = X` ETH, expecting a swap to `post.fee` fee-tokens at current market price.
2. The transaction sits in the mempool; a block producer or searcher delays inclusion, allowing price to move (e.g. via a sandwich attack on the same pool) so that the exchange rate becomes maximally unfavorable within `X` ETH.
3. When finally included, `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` passes the router's deadline check trivially (deadline equals the block's own timestamp), executing at the worse price and consuming the caller's full ETH budget, or reverting if price moved beyond `X`. [1](#0-0) [2](#0-1)

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
