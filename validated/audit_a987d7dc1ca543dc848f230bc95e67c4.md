### Title
Excess `msg.value` sent to `EvmHost.dispatch()`/`fundRequest()` is not refunded to the caller, causing permanent loss of native tokens - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all forward the entire `msg.value` to Uniswap V2's `swapETHForExactTokens`, but any ETH refunded by the router for unused input is sent back to `address(this)` (the `EvmHost` contract), not to the original caller. This is the same root cause as the reported Avail `sendMessage` issue — excess native-token payment is silently absorbed instead of refunded — and here it results in permanent, unrecoverable loss of user funds rather than just an accounting error.

### Finding Description
In `EvmHost.sol`, the native-payment path for dispatching messages is: [1](#0-0) 

and identically for GET requests and fee top-ups: [2](#0-1) [3](#0-2) 

In each case, `swapETHForExactTokens{value: msg.value}(feeAmount, path, address(this), block.timestamp)` is called with the entire `msg.value` as the maximum input, but the desired *output* amount is `post.fee` / `get.fee` / `amount`. Uniswap V2's `swapETHForExactTokens` only consumes the ETH actually required to produce the exact output amount and refunds any leftover ETH — but that refund goes to `msg.sender` as seen by the router, which in this call context is `EvmHost` itself (since `EvmHost` is the one invoking the router), not the original end-user (`tx.origin` / `_msgSender()`).

Because `EvmHost` has no logic to capture or forward this Uniswap refund back to the user, and no documented public function exists here to sweep/refund arbitrary leftover ETH to the paying user, any ETH sent above the exact amount needed for the swap becomes stuck in the `EvmHost` contract, permanently inaccessible to the user who overpaid. This differs from — and is more severe than — the original Avail bug, where excess `msg.value` merely inflated an internal `fees` counter; here it results in unrecoverable native-token loss for any user who does not compute the exact optimal `msg.value` (which is inherently hard to predict precisely due to Uniswap pool slippage between quote-time and execution-time).

### Impact Explanation
Any user calling `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` with native token payment and providing `msg.value` greater than the exact amount the Uniswap pool consumes to produce the required fee-token output will permanently lose the excess ETH — it is not returned to them and there is no visible mechanism to reclaim it for the depositor specifically. Given that fee estimation off-chain (`quote()`) is inherently imprecise due to price movement (the docs themselves warn `quote()` is subject to sandwich/slippage effects), users are structurally likely to over-provide `msg.value`, making this a broadly reachable, direct loss-of-funds condition for ordinary bridge users. This qualifies as concrete unbacked loss of user funds.

### Likelihood Explanation
High likelihood: this triggers on the default/documented usage path (native token payment for `dispatch`/`fundRequest`), requires no privileged role, and is reachable by any unprivileged user submitting a normal cross-chain message or funding a pending request with native tokens. The documentation itself instructs developers to send `msg.value` for `dispatch`, and any imprecision in the amount sent (which is expected in practice) will trigger fund loss.

### Recommendation
After calling `swapETHForExactTokens`, compute how much ETH was actually spent (e.g., via the returned `amounts` array from the swap, `amounts[0]`) and refund the difference (`msg.value - amounts[0]`) back to `_msgSender()`. Alternatively, use `swapExactETHForTokens` with a `msg.value`-based minimum-out check, or explicitly track and forward the router's refund (which currently lands as `address(this).balance`) to the correct end user rather than leaving it in the contract.

### Proof of Concept
1. Caller invokes `host.dispatch{value: 1 ether}(DispatchPost{... fee: 10e18 feeToken ...})` intending fee token amount `10e18`.
2. `EvmHost.dispatch` calls `swapETHForExactTokens{value: 1 ether}(10e18, [WETH, feeToken], address(this), deadline)`.
3. Suppose the pool only requires `0.8 ether` to produce `10e18` fee tokens; Uniswap V2 router refunds the remaining `0.2 ether` to `msg.sender` of the swap call, which is `EvmHost` (`address(this)`), not the original caller.
4. The caller's transaction succeeds, the message is dispatched, but the caller's `0.2 ether` overpayment remains stuck in the `EvmHost` contract balance with no code path returning it to them. [1](#0-0)

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
