### Title
Excess native ETH sent to `EvmHost.dispatch()`/`fundRequest()` is refunded to the host contract instead of the caller, permanently trapping user funds - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept `msg.value` and forward it unconditionally to a Uniswap V2-compatible router's `swapETHForExactTokens`, requesting an *exact* fee-token output. Any ETH sent beyond what the swap actually needs is refunded by the router — but the refund goes to `msg.sender` from the router's perspective, which is `EvmHost` itself (since `EvmHost` is the one calling the router), not the original end user who supplied the excess `msg.value`. This is the same root-cause bug class as the reported `SwapperImpl#_transferToBeneficiary` issue: an overpayment of native ETH that should be refunded to the payer instead is retained/misdirected by the contract.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

In `dispatch(DispatchGet)`: [2](#0-1) 

In `fundRequest`: [3](#0-2) 

In all three, when `msg.value > 0`, the code executes:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(fee/amount, path, address(this), block.timestamp);
```
`swapETHForExactTokens` is an *exact-output* swap: the router only consumes as much ETH as needed to produce `fee`/`amount` fee tokens, and any leftover ETH is refunded back to whoever called the router — i.e., `EvmHost` (`address(this)`), because `EvmHost` is the direct caller of the router. The router has no knowledge of the original transaction's `_msgSender()`. `EvmHost` never checks for or forwards this leftover ETH back to `_msgSender()`. There is no accounting variable that tracks "unspent value belongs to caller X" the way `SwapperImpl._payback` was supposed to, and no observed sweep/return mechanism in `EvmHost.sol` for stray ETH.

This is structurally identical to the reported defect: a function that is supposed to only take exactly `fee`/`amount` worth of value from the caller instead can absorb an arbitrary overpayment of native ETH, with no path back to the original payer.

### Impact Explanation
Any user or contract calling `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` with `msg.value` greater than the ETH-equivalent cost of the specified fee amount has the excess ETH permanently stuck in `EvmHost`. Since dispatch and fee-funding are core, frequently-used, fully permissionless entry points for any relayer, application, or end-user initiating cross-chain messages, this can cause repeated, unrecoverable loss of user funds at scale — matching the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
High likelihood: callers routinely cannot predict the exact ETH cost of a Uniswap swap for a fixed fee-token output (due to slippage/price movement between quote and execution), so overpayment by a safety margin is a normal, expected usage pattern (as seen explicitly tested and expected to be refunded in the analogous `IntentGatewayV2`/`ExtrinsicIntents` flows, which do correctly refund excess `msg.value` to `msg.sender`). `EvmHost`'s dispatch/fundRequest paths lack the equivalent refund-to-caller logic present in those other contracts.

### Recommendation
After the `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the actual amount of ETH spent (returned by `amounts[0]` from the router) and refund `msg.value - amounts[0]` back to `_msgSender()`, mirroring the pattern used in `ExtrinsicIntents._fillCrossChain`/`IntrinsicIntents._fillSameChain` (`_sendValue(msg.sender, msgValue)`).

### Proof of Concept
1. A user calls `EvmHost.dispatch(DispatchPost)` (or `dispatch(DispatchGet)` / `fundRequest`) with `msg.value` deliberately larger than needed (e.g., to buffer for slippage) to cover a fee of `post.fee` fee-tokens.
2. `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` executes; the router spends only the ETH needed to acquire exactly `post.fee` tokens and refunds the remainder to `msg.sender` of that call — which is `EvmHost`.
3. `EvmHost`'s ETH balance increases by the refunded amount; the function returns without ever transferring this ETH back to the original caller.
4. The original caller's excess ETH is now permanently held by `EvmHost` with no code path identified to return it to them.

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
