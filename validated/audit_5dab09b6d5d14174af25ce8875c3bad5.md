### Title
Excess native-token overpayment in `EvmHost.dispatch`/`fundRequest` is trapped in the Host instead of being refunded to the payer - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept `msg.value` as native-token fee payment and swap it via `swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`. None of these functions capture the router's return value or otherwise handle leftover ETH from the swap.

### Finding Description
In each of these functions the pattern is identical: [1](#0-0) [2](#0-1) [3](#0-2) 

Uniswap V2's `swapETHForExactTokens(amountOut, path, to, deadline)` only spends up to `amountOut`'s equivalent input, and refunds `msg.value - amountIn` back to `msg.sender` of that call — i.e. back to `EvmHost` itself, because `EvmHost` is the account that invoked the router with `{value: msg.value}`. `EvmHost` never forwards that refund back to the original transaction sender (`_msgSender()`/payer). None of the three functions record, track, or return this excess native balance, and there is no `withdraw`/`sweep` function elsewhere in `EvmHost.sol` that lets the original payer (or anyone) reclaim it.

This mirrors the reported bug class exactly: a funder who supplies `msg.value` in combination with a fee amount that requires less native token than sent (e.g., quoting off-chain with `quote()`, which is explicitly documented as "Approximate (subject to slippage)") permanently loses the difference — it becomes stuck in `EvmHost`'s balance with no mechanism to recover it, and is not credited to the payer's `FeeMetadata` since only the ERC20 `feeToken` fee is recorded (`_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee})`), not any residual native value.

### Impact Explanation
Any user or integrating dApp calling `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` with native-token payment and sending even a small buffer above the exact swap requirement (which the docs themselves recommend doing off-chain to avoid reverts from slippage) will have that excess ETH permanently locked in the `EvmHost` contract with no recovery path. Given `quote()` is explicitly warned to be "Approximate" and subject to sandwich/slippage risk, users are effectively encouraged by the documentation to overpay `msg.value`, directly triggering this loss on every affected dispatch. This is a direct, permanent loss of user funds (Medium/High severity depending on typical overpayment margins across the volume of dispatch calls).

### Likelihood Explanation
High likelihood: every one of the three payable native-fee code paths in `EvmHost.sol` (`dispatch(DispatchPost)`, `dispatch(DispatchGet)`, `fundRequest`) is affected, and providing a native-token payment for message dispatch/funding is a first-class, documented, unprivileged flow (any app or user can call it in a single transaction). Slippage on Uniswap swaps and imprecise off-chain quoting make some degree of overpayment routine rather than an edge case.

### Recommendation
Capture the return value of `swapETHForExactTokens` (the `amounts` array) in all three locations and refund the difference `msg.value - amounts[0]` back to `_msgSender()` (or the designated payer), for example:
```solidity
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
if (msg.value > amounts[0]) {
    payable(_msgSender()).transfer(msg.value - amounts[0]);
}
```
Apply the same fix to `dispatch(DispatchGet)` and `fundRequest`.

### Proof of Concept
1. Attacker/user calls `quote()` off-chain to estimate native cost for a `DispatchPost` with `fee = F` fee-tokens; due to normal price movement/slippage, the on-chain required `amountIn` at execution time is less than the quoted/sent `msg.value`.
2. User calls `EvmHost.dispatch{value: msg.value}(post)` with `post.fee = F`.
3. Inside `dispatch`, `swapETHForExactTokens{value: msg.value}(F, path, address(this), block.timestamp)` executes, spending only `amountIn < msg.value` and refunding `msg.value - amountIn` to `EvmHost` (the caller of the router), not to the user.
4. `dispatch` returns normally; the request is committed and emitted with `fee: F` — the leftover native ETH is now part of `EvmHost`'s contract balance, with no field in `FeeMetadata`, `HostParams`, or any external function that lets the user or protocol withdraw or credit it back.
5. Repeating this for any dispatch/fundRequest call accumulates unrecoverable ETH inside `EvmHost`.

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
