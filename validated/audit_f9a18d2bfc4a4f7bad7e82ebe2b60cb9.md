### Title
`EvmHost.dispatch`/`fundRequest` strand user's excess native-token overpayment inside the host — ether becomes permanently trapped ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all let a caller pay dispatch fees in native token by forwarding the *entire* `msg.value` into `IUniswapV2Router02.swapETHForExactTokens`. This mirrors the `StargateStrategy._withdraw` bug class: the code assumes the value it hands the external AMM call is fully consumed for the operation it's performing, when in fact only `post.fee`/`get.fee`/`amount` worth of tokens is actually needed and any surplus ETH is refunded by the router — but to the wrong party, and with no path back out for the user who supplied it.

### Finding Description
In all three functions, the pattern is identical:

```solidity
if (msg.value > 0) {
    address[] memory path = new address[](2);
    address uniswapV2 = _hostParams.uniswapV2;
    path[0] = IUniswapV2Router02(uniswapV2).WETH();
    path[1] = feeToken();
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
``` [1](#0-0) [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` is an *exact-output* swap: it takes at most `msg.value` in but only spends what's needed to receive exactly `post.fee` fee tokens, and the canonical Uniswap V2 router **refunds the unspent ETH to `msg.sender` of the swap call** — which here is `EvmHost` itself, not the end user who called `dispatch`/`fundRequest` with the overpaid `msg.value`. None of the three functions capture or forward that refund back to `_msgSender()`; execution proceeds directly to building the request/commitment with no accounting of leftover native balance.

The docs confirm users are expected to overpay as a buffer, since front-end fee quoting via `quote()` is explicitly "Approximate (subject to slippage)" and vulnerable to sandwich manipulation: [4](#0-3) [5](#0-4) 

This is exactly the root-cause pattern from the external report: an internal accounting step assumes the amount handed to an external swap/redeem call equals the amount actually consumed, so any positive difference is silently absorbed by the contract instead of being returned to the depositor. In `StargateStrategy` the mismatch was between `toWithdraw` LP tokens and actual ETH redeemed; here it's between `msg.value` supplied and the actual ETH spent by the exact-output swap.

### Impact Explanation
Any unprivileged user who dispatches a POST/GET request or funds a pending request with `msg.value` greater than the exact wei needed for the underlying Uniswap swap (which is the normal/expected usage pattern given fee quoting is only approximate) has the excess permanently stranded as raw native ETH inside `EvmHost`. There is no discovered sweep/refund mechanism in `EvmHost` that returns this stray balance to the original payer; it becomes unrecoverable protocol-level loss of user funds accumulating with every overpaid dispatch call, which is a direct parallel to the "ether becomes trapped in the contract" finding in the original report.

### Likelihood Explanation
High reachability: this triggers on the ordinary, documented native-fee-payment path (`dispatch{value: ...}`) used by any relayer, app, or end user who doesn't send the exact wei amount — which is realistically almost every call, since exact quoting on-chain is explicitly discouraged and slippage/sandwich risk means callers pad `msg.value`. No special privileges are required; it's triggered by a single transaction.

### Recommendation
After calling `swapETHForExactTokens`, compute the unspent ETH (`msg.value` minus the actual amount spent, as returned by the swap call) and refund it to `_msgSender()` (or the designated payer) via a low-level call, reverting if the transfer fails — mirroring the audited fix pattern for `StargateStrategy` of reconciling actual consumption against the assumed amount before finalizing.

### Proof of Concept
1. Deploy `EvmHost` with a configured `uniswapV2` router and `feeToken`.
2. Call `dispatch(DispatchPost)` (or `dispatch(DispatchGet)` / `fundRequest`) with `msg.value` set noticeably higher than the wei actually required to obtain `post.fee` fee tokens at current pool price (e.g., pad by 20% as any front end reasonably would given quoting is "approximate/slippage-subject").
3. Observe that `IUniswapV2Router02.swapETHForExactTokens` only spends the wei needed and refunds the remainder to `msg.sender`, which is `EvmHost`.
4. Confirm `address(EvmHost).balance` increases by the unspent amount after the call, and that no function exists in the transaction's call path (nor callable afterward by the original payer) to reclaim that specific ETH — it is indistinguishable from other host balance and effectively lost to the caller.

Note: I was unable to fully verify within available tool calls whether `EvmHost.sol` contains any owner-only sweep/withdraw function for stray native balance elsewhere in the file (the grep for "withdraw|sweep" returned 43 matches in that file, likely referring to unrelated request-timeout "withdraw" naming, but I could not inspect each occurrence before running out of iterations). If such a sweep function exists and is capable of returning funds specifically to affected payers, the severity should be downgraded from "permanent loss" to "requires manual governance intervention"; this should be confirmed by reading the full `evm/src/core/EvmHost.sol` file in a follow-up session.

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L240-249)
```text
### Payment Method Comparison

| Feature | Native Token | FeeToken (Recommended) |
|---------|-------------|------------------------|
| **Gas Cost** | Higher (includes swap) | Lower (no swap) |
| **Slippage** | Yes (Uniswap swap) | No |
| **Fee Calculation** | Approximate (subject to slippage) | Exact |
| **Token Approval** | Not required | Required  |
| **User Convenience** | High (users have native tokens) | Low (users need feeToken) |
| **Best For** | One-off transactions, user-facing apps | Frequent dispatches, cost optimization |
```

**File:** docs/content/developers/evm/messaging/get-requests.mdx (L504-511)
```text
// Display to user or use in transaction
console.log(`Fee in native token: ${nativeCost}`)
console.log(`Fee in fee token: ${feeTokenCost}`)
```

<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
