## Title
Hardcoded `deadline: block.timestamp` in EvmHost's native-fee swaps enables stale-price/sandwich extraction and unrecoverable ETH loss - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` allow any caller to pay Hyperbridge message fees in native token. When `msg.value > 0`, each function performs an on-chain UniswapV2 swap with the deadline hardcoded to `block.timestamp`, computed at execution time rather than signed at submission time. This is the exact bug class from the referenced report: a deadline set to the current execution time is always trivially satisfied, so it provides no actual protection against the transaction sitting in the mempool and later being mined at a stale/manipulated price.

### Finding Description
In all three unprivileged, fee-paying entry points, the swap call is: [1](#0-0) [2](#0-1) [3](#0-2) 

In each case `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)` is invoked. Because `deadline` is computed inside the same call that performs the check (`deadline >= block.timestamp` at mining time), it is satisfied unconditionally whenever the transaction executes — regardless of how long it sat in the mempool. This nullifies the entire purpose of a swap deadline (bounding the time window during which stale pricing can be exploited), exactly mirroring the audit finding against `IchiSpell._withdraw`.

There is a second, compounding issue: the swap recipient is `address(this)` (the `EvmHost` contract itself), and `swapETHForExactTokens` refunds any unused ETH to the router's caller — which is `EvmHost`, not the original `msg.sender` who funded the call. `EvmHost` has no logic to forward this refund back to the depositor; excess native token becomes trapped in the contract balance, only recoverable later by governance via `IHostManager.withdraw` — i.e., value contributed by ordinary users can be permanently redirected away from them.

Combined, an attacker (or ordinary network congestion) can:
1. Wait for a user's `dispatch`/`fundRequest` transaction with a generous `msg.value` buffer to sit pending in the mempool.
2. Sandwich/manipulate the native-token/feeToken pool price right before inclusion, since the hardcoded deadline never blocks execution.
3. Force the swap to consume a larger portion of `msg.value` to obtain the same fixed `fee` output, extracting the difference as MEV profit, while any leftover/refund ETH goes to the `EvmHost` contract rather than back to the user.

### Impact Explanation
This is a High severity issue: value paid by any unprivileged caller (app developer, relayer, or end user) dispatching a POST/GET request or funding a request with native token can be siphoned via MEV sandwiching with no on-chain protection, and any leftover ETH is unrecoverable by the depositor. Since `dispatch()` and `fundRequest()` are core, frequently used entry points for cross-chain message submission, this affects the core dispatch path of Hyperbridge itself, not a peripheral app.

### Likelihood Explanation
Likelihood is high: any transaction paying with native token during periods of network congestion or low gas price is susceptible, and no user action can mitigate it because the deadline parameter is not exposed to callers — it is fully hardcoded inside `EvmHost`. MEV bots routinely monitor mempools for swap calls with exploitable price windows.

### Recommendation
- Do not hardcode `deadline: block.timestamp`; expose a caller-supplied deadline parameter (validated to be reasonably bounded) in `DispatchPost`, `DispatchGet`, and `fundRequest` so a stale-mempool transaction reverts instead of executing at a stale price.
- Track and refund excess native token from `swapETHForExactTokens` back to the original `_msgSender()` (or `post.payer`) instead of leaving it in the `EvmHost` contract balance.
- Consider adding a slippage/price bound check independent of the deadline (e.g., max native amount the depositor is willing to spend) rather than relying solely on `msg.value` as an implicit cap.

### Proof of Concept
1. Alice calls `EvmHost.dispatch(DispatchPost)` with `msg.value = 1 ETH` intending to pay `post.fee = 100` feeTokens, expecting excess ETH back.
2. Due to low gas price, the transaction sits in the mempool.
3. A searcher observes it and, right before inclusion, manipulates the native/feeToken pool price upward (e.g., via a flash-loan swap) so more ETH is required to buy the fixed `100` feeTokens.
4. Because `deadline: block.timestamp` is computed at the moment of on-chain execution, the swap's deadline check trivially passes — the transaction that would have reverted under a properly signed, earlier deadline instead executes at the manipulated price.
5. `swapETHForExactTokens` consumes more of Alice's `1 ETH` to obtain the `100` feeTokens; the searcher's counter-swap captures the arbitrage profit from Alice's overpayment. Any remaining leftover ETH is refunded to `address(this)` (`EvmHost`), not Alice, and is unrecoverable by her. [1](#0-0)

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

**File:** evm/src/core/EvmHost.sol (L1031-1039)
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
```
