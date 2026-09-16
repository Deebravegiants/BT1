## Title
Excess ETH from Uniswap swap is not returned to the caller in `EvmHost.dispatch`/`fundRequest` — trapped in `EvmHost` instead of refunded to `msg.sender` - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all accept native token payment and swap it for the exact fee-token amount needed via Uniswap V2's `swapETHForExactTokens`. Any leftover ETH from that swap is refunded by the Uniswap router to `msg.sender` of the swap call — which is `EvmHost` itself, not the original user who sent the `msg.value`. This is the exact bug class from the external report: excess funds sent by the caller are not returned to them.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

and identically in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

In all three functions, when `msg.value > 0`, the contract calls:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    fee, path, address(this), block.timestamp
);
```
`swapETHForExactTokens` requires only `amounts[0]` (the exact ETH needed to buy `fee` fee-tokens) of the supplied `msg.value`; per the standard Uniswap V2 periphery implementation, any leftover ETH (`msg.value - amounts[0]`) is refunded via `TransferHelper.safeTransferETH(msg.sender, ...)`. Since `EvmHost` itself is the caller of the router (`msg.sender` from the router's perspective is `EvmHost`, not `_msgSender()`/the end user), the refund lands in `EvmHost`'s own balance rather than being returned to the user who supplied the excess ETH. There is no code path in `EvmHost.sol` that forwards this refunded ETH back to `_msgSender()`.

This mirrors the reported `AvailBridge.sendMessage` pattern exactly: a user sends `msg.value` intending to cover a fee, but any amount over the exact required cost is not returned to them — it is unconditionally retained by the protocol contract.

### Impact Explanation
Any user calling `dispatch()` (POST/GET) or `fundRequest()` with native token and providing more ETH than is exactly required by the Uniswap swap (which is the common case, since the exact `amounts[0]` needed can rarely be known precisely in advance, and slippage/gas-price estimation naturally leads to overpayment) permanently loses the excess ETH to the `EvmHost` contract. This is a direct loss of user funds with no recovery path exposed to the user — meeting the "concrete theft or permanent freezing of funds" bar. Because this is reachable by any unprivileged message dispatcher or bandwidth/fee payer sending a single transaction with native token payment, it is broadly exploitable (or rather, broadly damaging) across normal usage of the dispatch entry points.

### Likelihood Explanation
High likelihood: this triggers on ordinary use of the natively-funded dispatch path, not an edge case or attacker-crafted input. Every caller using `dispatch{value: msg.value}(...)` with `msg.value` not exactly equal to the swap's required input amount will lose the difference. Given that `getAmountsIn` calculations are sensitive to pool state at execution time (front-run/slippage), users are effectively forced to overpay to guarantee the swap succeeds, guaranteeing this leftover-fund loss occurs regularly in practice.

### Recommendation
After calling `swapETHForExactTokens`, check `address(this).balance` (or track the ETH balance before/after the call) and refund any residual ETH to `_msgSender()` (or the designated payer) with a low-level call, mirroring the fix recommended in the analog report. Apply this fix uniformly to `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`.

### Proof of Concept
1. Alice calls `EvmHost.dispatch(DispatchPost)` with `post.fee = 100` (fee-token units) and sends `msg.value = 1 ether` to safely cover slippage on the ETH→feeToken swap.
2. `EvmHost` calls `swapETHForExactTokens{value: 1 ether}(100, path, address(this), deadline)`.
3. Suppose only `0.01 ether` was actually required to obtain `100` fee tokens. The Uniswap router refunds `0.99 ether` to `msg.sender` of the swap call, i.e. `EvmHost`.
4. `EvmHost` never forwards this `0.99 ether` back to Alice; it simply sits in the `EvmHost` contract's balance.
5. Alice has permanently lost `0.99 ether` with no function in `EvmHost.sol` allowing her to reclaim it.

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
