### Title
Excess native-token payment on `EvmHost.dispatch`/`dispatchGet`/`fundRequest` is refunded to the Host contract instead of the caller, permanently trapping user ETH - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)` and `fundRequest` accept native token payment and swap it through UniswapV2 for an exact amount of `feeToken` using `swapETHForExactTokens{value: msg.value}`. Any unused ETH from that swap is refunded by the router to its immediate caller — which is `EvmHost` itself, not the original transaction sender. There is no rescue/withdraw path in `EvmHost` for recovering this residual native balance, so any user who overestimates the required native fee permanently loses the excess ETH, mirroring the "any ETH transfer to timelock will be locked forever" bug class where value sent to a contract cannot subsequently be extracted because the withdrawal logic never accounts for balances already resident on that contract.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 
the function swaps `msg.value` of native token for an exact `post.fee` amount of `feeToken` via `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. The same pattern recurs in `fundRequest`: [2](#0-1) 

The standard Uniswap V2 Router `swapETHForExactTokens` implementation computes the exact ETH input required for the requested output and, if `msg.value` exceeds that amount, refunds the difference to `msg.sender` of the router call. Here, the router's `msg.sender` is `EvmHost` (since `EvmHost` is the one invoking the router), not the externally-owned account or contract that originally called `dispatch`/`fundRequest`. Consequently, any ETH sent in excess of the exact fee requirement is credited back into `EvmHost`'s own balance rather than returned to the caller who supplied it.

Unlike the intents/apps contracts in this same repo (e.g., `IntentGatewayV2`, `ExtrinsicIntents._sendValue`), which explicitly track `msgValue` and refund unspent native tokens to `msg.sender` after execution, `EvmHost.dispatch`/`dispatchGet`/`fundRequest` perform no such accounting or refund step. No search of `EvmHost.sol` (nor the module directory that would host `HostManager`) turned up a withdraw/rescue/sweep function capable of moving this stranded native ETH balance back out — the only governance-callable withdrawal path documented is over the `feeToken`, not raw native balance accrued this way.

### Impact Explanation
Any unprivileged caller (an app contract or EOA) dispatching a POST/GET request or funding a pending request with native token, who supplies more ETH than the router's exact-input requirement for the target `feeToken` amount, has that surplus permanently trapped in `EvmHost` with no recovery mechanism identified. Since `dispatch`/`fundRequest` are the primary entry points used by every app and end user paying fees natively (as documented throughout the messaging/post-requests guide), this is a broadly reachable freezing-of-funds condition, not a hypothetical edge case — small overestimation of native fee (common, since users are guided to "estimate fees ... before submitting" and gas/price fluctuation makes exact-amount computation unreliable) results in permanent loss for the caller.

### Likelihood Explanation
High reachability: this occurs whenever `msg.value` supplied to `dispatch`/`dispatchGet`/`fundRequest` is not exactly equal to the router's computed input for `post.fee`/`get.fee`/`amount`. Since callers are expected to estimate the fee off-chain, exact equality is unlikely in practice, making the surplus-refund misdirection trigger on essentially every native-fee payment that isn't perfectly tuned.

### Recommendation
Track `msg.value` similarly to how `IntentsBase`/`ExtrinsicIntents` do, or use `swapETHForExactTokens` return value / router refund by explicitly forwarding any residual `address(this).balance` delta back to `_msgSender()` after the swap in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`. Alternatively, snapshot `address(this).balance` before/after the swap and immediately transfer the difference to the caller instead of allowing it to accumulate as an unrecoverable Host balance.

### Proof of Concept
1. Caller invokes `EvmHost.dispatch(post)` with `post.fee = X` and `msg.value = X + Δ` where `Δ` is a small overestimate of required native input.
2. `IUniswapV2Router02.swapETHForExactTokens{value: X + Δ}(X, path, address(this), block.timestamp)` computes the exact ETH input `Y ≤ X + Δ` needed to obtain `X` fee tokens and refunds `(X + Δ) - Y` to `msg.sender` of the router call, i.e., to `EvmHost`.
3. `EvmHost`'s native balance permanently increases by `(X + Δ) - Y`; the original caller receives nothing back and has no function on `EvmHost` to reclaim it. [1](#0-0)

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
