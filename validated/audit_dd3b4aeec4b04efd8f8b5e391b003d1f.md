### Title
Excess native-token refunds from Uniswap swaps become permanently locked in `EvmHost` - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch()` and `EvmHost.fundRequest()` both accept `msg.value` and route any supplied ETH through `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)`. This call is made by `EvmHost` itself, not by the original end user, so any ETH refunded by the router for exceeding the exact amount needed to purchase `post.fee`/`amount` fee-tokens is sent back to `address(this)` (the `EvmHost` contract), not to the caller. `EvmHost` has no `receive()`/`withdraw()` function to sweep or return this stray native balance, so it accumulates and is permanently locked, mirroring the reported Diamond.sol issue where the contract can receive ETH it can never release.

### Finding Description
In `dispatch(DispatchPost memory post)`: [1](#0-0) 

and identically in `dispatch(DispatchGet memory get)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

In all three functions, `EvmHost` is the direct caller (`msg.sender`, from the router's point of view) of `IUniswapV2Router02.swapETHForExactTokens`. Per the standard UniswapV2 router implementation, `swapETHForExactTokens(amountOut, path, to, deadline)` requires only enough ETH to cover the exact output requested (`post.fee`/`amount`); if `msg.value` exceeds the amount actually needed, the router refunds the difference to `msg.sender` of that call — which is `EvmHost`, not the end user who originally sent the transaction. Because `EvmHost` never forwards or reclaims that refunded ETH, and there is no `receive()` fallback logic, admin withdrawal path, or sweep function for native ETH anywhere in `EvmHost.sol` (only the `feeToken` ERC-20 balance is managed via `hostManager` withdrawal requests), the refunded ETH becomes permanently stuck in the contract.

This differs from the documented, intended flow (where "excess" is supposed to only ever be the exact amount, per the docs stating amounts should be estimated precisely), but in practice any slippage-driven overestimation by the caller, or a user simply sending more `msg.value` than strictly required, results in irrecoverable ETH loss, unlike the `feeToken` path, where excess/leftover balances are governed and can be withdrawn by the `hostManager`.

### Impact Explanation
Any user or integrating application that calls `dispatch()`/`fundRequest()` with native token payment and slightly overestimates the required ETH (a very likely occurrence given AMM slippage, price movement between estimation and execution, or simple safety margins) will have the excess ETH permanently locked in the `EvmHost` contract with no recovery mechanism. This is a direct, permanent freezing of user funds reachable from a single normal transaction — exactly the "permanent freezing of funds" class called out as in-scope.

### Likelihood Explanation
High likelihood: this triggers on the ordinary, documented "Native Token Payment" path that the protocol explicitly recommends and provides SDK/doc examples for, and requires no malicious actor — any user overshooting the exact swap amount (which the docs themselves note is "Approximate (subject to slippage)") is affected on every dispatch call.

### Recommendation
After the `swapETHForExactTokens` call, capture the returned `amounts` array and refund any leftover `msg.value` (or refunded WETH/ETH now held by `EvmHost`) back to `_msgSender()`. Alternatively, add a `receive()`/admin-gated withdrawal function that allows sweeping stray native balance, and explicitly forward router refunds to the caller instead of leaving them on `address(this)`.

### Proof of Concept
1. Alice calls `EvmHost.dispatch{value: 1 ether}(post)` where `post.fee = 100 feeToken` but the true swap cost is `0.5 ether` at execution time.
2. `EvmHost` calls `swapETHForExactTokens{value: 1 ether}(100, path, address(this), deadline)`.
3. The router wraps `0.5 ether` into WETH, swaps for exactly `100` fee tokens sent to `EvmHost`, and refunds the remaining `0.5 ether` to `msg.sender` of the router call — i.e., to `EvmHost` itself.
4. `EvmHost` now holds `0.5 ether` extra native balance with no function to withdraw or refund it to Alice; it is permanently locked in the contract.

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
