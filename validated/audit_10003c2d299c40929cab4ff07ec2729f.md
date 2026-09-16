## Title
`EvmHost.dispatch()` / `fundRequest()` DOS when the configured Uniswap V2 pool cannot fill the native-ETH fee swap - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` all route native-ETH fee payments through an external Uniswap V2 router swap. If that router/pool cannot satisfy the swap (e.g. the WETH/feeToken pool has insufficient liquidity, is imbalanced, or the exact-output amount cannot be met), the external call reverts and the entire dispatch/fund transaction reverts with it — exactly the same failure pattern as the referenced FRAX `submit()`-pause analog, where an external protocol's normal operating constraints (not malicious behavior) DOS a core user-facing function.

### Finding Description
When a caller pays dispatch fees in native ETH, `EvmHost` unconditionally calls: [1](#0-0) 

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
}
```

The same pattern is repeated for GET dispatch and fee top-ups: [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` is an exact-output swap: if the WETH/feeToken pool's reserves are insufficient to produce `post.fee` (or `amount`) tokens out — which is a routine liquidity condition, not an admin action, and can occur simply from normal AMM trading draining one side of the pool, LPs withdrawing liquidity, or the pool never having enough depth for the configured fee token amounts — the Uniswap V2 library reverts (`UniswapV2Library: INSUFFICIENT_LIQUIDITY` or the constant-product invariant check), which bubbles up and reverts the whole `dispatch`/`fundRequest` call.

This is directly analogous to the FRAX report: a core, unprivileged, single-transaction-reachable function (`dispatch`, the primary way any app or user pushes a cross-chain POST/GET request) unconditionally depends on an external protocol call whose legitimate failure mode (not malicious governance) causes the entire transaction to revert, with no fallback path once ETH is chosen as the payment method.

### Impact Explanation
`dispatch` is the core outbound-messaging entrypoint of `EvmHost` — every app/user that wants to send a cross-chain POST or GET request and pays with native ETH goes through this exact swap. If the configured Uniswap V2 pool lacks liquidity for the requested fee amount (a realistic, non-malicious market condition), all native-ETH-funded dispatches and `fundRequest` fee top-ups revert, DOSing that entire payment path for the router/host until liquidity is externally restored or the pool is reconfigured by governance. Since dispatch is the base primitive that every downstream app (token bridges, intents, HFT) relies on for outbound messages, this can block message submission broadly for the ETH-fee-payment flow.

### Likelihood Explanation
Requires no malicious actor: normal AMM liquidity fluctuation, LP withdrawal, or a pool that was never provisioned deep enough for larger fee amounts is sufficient to trigger `INSUFFICIENT_LIQUIDITY`/invariant reverts on `swapETHForExactTokens`. Any single unprivileged caller supplying `msg.value` with a `post.fee`/`amount` that the pool cannot currently fill will trip this deterministically and repeatedly for as long as the liquidity condition persists.

### Recommendation
Do not hard-fail the whole dispatch on swap failure. Consider wrapping the swap call and, on failure, falling back to `feeToken` transfer from the caller (if pre-approved), or exposing a `getAmountsOut`/liquidity pre-check that reverts with an actionable error before committing native ETH, or allowing the host params to disable native-ETH fee payment gracefully instead of reverting the core dispatch path.

### Proof of Concept
1. Configure `_hostParams.uniswapV2` pointing at a WETH/feeToken pool with shallow liquidity (a realistic, non-adversarial state).
2. Any user calls `dispatch(DispatchPost)` (or `dispatch(DispatchGet)`/`fundRequest`) with `msg.value > 0` and a `post.fee` that exceeds what the pool's current reserves can output via `swapETHForExactTokens`.
3. The router reverts inside `dispatch`, causing the whole POST/GET dispatch (and its commitment creation/event emission) to fail — DOSing the core message-dispatch functionality for any ETH-paying caller until the pool's liquidity recovers.

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
