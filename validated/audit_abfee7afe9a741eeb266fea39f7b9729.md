### Title
Excess native token payment in `EvmHost.dispatch()`/`fundRequest()` is refunded to the Host contract instead of the caller, permanently trapping overpaid ETH - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept `msg.value` and swap it for the exact `feeToken` amount required via `IUniswapV2Router02.swapETHForExactTokens`. Any ETH sent in excess of the amount actually consumed by the swap is refunded by the Uniswap router — but the refund is sent to `msg.sender` of the router call, which is the `EvmHost` contract itself, not the original transaction sender. As a result, any user who overpays even slightly ends up permanently losing that excess ETH into the Host's own balance.

### Finding Description
In all three payable entry points, the pattern is identical: [1](#0-0) [2](#0-1) [3](#0-2) 

The call is `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. Uniswap V2's `swapETHForExactTokens` computes the exact input required via `getAmountsIn`, performs the swap, and refunds any leftover ETH (`msg.value - amounts[0]`) to the caller of the router — which, from the router's perspective, is `EvmHost`, since `EvmHost` itself invoked the router with the forwarded `msg.value`. The original user's address is never passed to the router, so the refund cannot reach them; it lands in `EvmHost`'s own native balance.

Because fee estimation is inherently imprecise (the docs explicitly warn `quote()` should only be used off-chain "to avoid sandwich attacks", implying on-chain price can shift between quoting and execution), users routinely cannot send the exact wei amount consumable by the swap. Any surplus — however small — is silently absorbed by the protocol contract with no path back to the payer. [4](#0-3) 

This mirrors the original Gitcoin analog: a payment channel (native ETH) that is accepted by the contract but never correctly routed onward/back out under normal usage, leaving funds stranded in the wrong contract balance.

### Impact Explanation
Every unprivileged caller of `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` who sends `msg.value` slightly greater than the exact amount required by the Uniswap swap permanently loses the difference — it becomes stuck in `EvmHost`'s native balance with no on-chain accounting (`FeeMetadata` only tracks `post.fee`/`amount` in `feeToken`, not leftover ETH) and no refund mechanism to the original sender. This is a direct, protocol-wide fund-loss bug affecting the core dispatch path used by every app built on Hyperbridge (HFT, WrappedHFT, Intent Gateway native-fee flows, and any custom `HyperApp`).

### Likelihood Explanation
High likelihood: any single transaction using native-token fee payment through `dispatch()`/`fundRequest()` that isn't a wei-perfect match to the swap's `amounts[0]` triggers the loss. Given price movement between off-chain `quote()` and on-chain execution (explicitly acknowledged as a slippage/sandwich risk in the docs), overpayment is the expected common case rather than an edge case.

### Recommendation
Capture the router's return value / leftover ETH and refund it to `_msgSender()` (or `post.payer`) instead of leaving it in the Host contract, e.g.:
```solidity
uint256 balanceBefore = address(this).balance - msg.value;
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp);
uint256 leftover = address(this).balance - balanceBefore;
if (leftover > 0) {
    payable(_msgSender()).transfer(leftover);
}
```

### Proof of Concept
1. Off-chain, a caller calls `quote()` to estimate the native cost for a `DispatchPost` with `fee = 100e6` feeToken units, getting `nativeCost = 0.05 ETH`.
2. Due to normal price drift between the quote and the transaction being mined, the actual `amounts[0]` needed by `swapETHForExactTokens` to buy exactly `100e6` feeToken units is `0.048 ETH`.
3. Caller submits `dispatch{value: 0.05 ETH}(post)`.
4. Inside `EvmHost.dispatch`, `swapETHForExactTokens{value: 0.05 ETH}(100e6, path, address(this), block.timestamp)` executes: it uses `0.048 ETH`, and refunds `0.002 ETH` to `msg.sender` of the router call — which is `EvmHost`, not the caller.
5. `EvmHost`'s native balance permanently increases by `0.002 ETH`; the original caller has no way to recover it. [1](#0-0)

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
