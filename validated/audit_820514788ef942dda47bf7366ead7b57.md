Confirmed: in `swapETHForExactTokens`, the refund `msg.sender.call{value: refund}("")` at line 147 refunds to the *caller* of that function, which is `EvmHost` itself (since `EvmHost.dispatch` invokes the router with `{value: msg.value}` on behalf of the user). Any excess native token sent by a user calling `EvmHost.dispatch()`/`fundRequest()` beyond the exact fee amount gets refunded into `EvmHost`'s own balance instead of back to the original user, with no sweep/withdraw function evident in `EvmHost.sol` to recover it for the user.

### Title
Overpayment of native token fee in `EvmHost.dispatch`/`fundRequest` is refunded to `EvmHost` itself instead of the user, permanently locking user funds - (File: evm/src/core/EvmHost.sol, evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` forward the entire `msg.value` sent by the caller into `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)` without first checking that `msg.value` equals the exact native amount required for `fee`. [1](#0-0) [2](#0-1) 

### Finding Description
The router used on some chains is `UniV3UniswapV2Wrapper`, whose `swapETHForExactTokens` computes `spent` (actual ETH consumed for the exact-output swap) and, if `spent < msg.value`, refunds the difference — but to `msg.sender`, not to any parameter identifying the original payer: [3](#0-2) 

Because `EvmHost` itself is the direct caller of the router (it forwards `msg.value` from the original user), `msg.sender` inside `swapETHForExactTokens` resolves to the `EvmHost` contract address, not the end user who called `dispatch`/`fundRequest`. Any surplus ETH sent above what's strictly needed to acquire `post.fee` (or `amount` for `fundRequest`) in fee-token terms is refunded into `EvmHost`'s own balance rather than back to the caller. There is no user-facing sweep/refund mechanism in `EvmHost.sol` for this stranded native balance, so user overpayment becomes permanently unrecoverable to them — exactly mirroring the "msg.value > msgValue causes loss of ETH to the contract" class from the referenced report, except the root cause here is a nested-call `msg.sender` refund-target mismatch rather than a missing equality check.

This is directly reachable by any unprivileged caller: any app or user dispatching a POST/GET request with `msg.value` (e.g. via `HyperFungibleToken.send`, `WrappedHyperFungibleToken.send`, `IntentGatewayV2.placeOrder`, or any `IApp` calling `IDispatcher(_host).dispatch{value: msg.value}(...)`) that overestimates the exact native amount needed for the swap will have the excess siphoned into `EvmHost` with no path to reclaim it. [4](#0-3) [5](#0-4) 

### Impact Explanation
Users routinely cannot predict the exact native ETH amount a swap will consume (Uniswap V3 pool price moves between quote and execution), so any generous `msg.value` (a common practice to avoid reverts from slippage) results in silent, permanent loss of the excess to the protocol contract itself, with no owner/admin withdrawal path visible in `EvmHost.sol` for arbitrary stuck native balance. This is a direct, unbounded loss of user funds reachable from a single transaction by any unprivileged caller of `dispatch`/`fundRequest`, satisfying the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
High likelihood: overpaying `msg.value` for a fee to guard against slippage/price movement is the expected, common usage pattern (docs even reference paying "an optional relayer fee ... in native token" without specifying exact amounts client-side must match on-chain price at execution time). Every call through this path where `msg.value` slightly exceeds the swap's exact-output cost triggers the loss.

### Recommendation
Have `swapETHForExactTokens`/`swapETHForExactTokensSupportingFeeOnTransferTokens`-style wrapper functions accept an explicit `refundTo` parameter (defaulting to `tx.origin`-independent, explicitly passed by `EvmHost`) rather than using `msg.sender`, and have `EvmHost.dispatch`/`fundRequest` pass through the original `_msgSender()` as the refund recipient so any swap surplus returns to the actual payer instead of accumulating in `EvmHost`.

### Proof of Concept
1. User calls `HyperFungibleToken.send{value: 1 ether}(params)` where the actual fee token cost for `params.relayerFee` only requires 0.5 ETH worth of the pool at execution time.
2. `HyperFungibleToken.send` forwards `msg.value` to `IDispatcher(_host).dispatch{value: msgValue}(request)`. [6](#0-5) 
3. `EvmHost.dispatch` forwards the full 1 ETH to `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)`. [7](#0-6) 
4. Inside the wrapper, `spent` (e.g. 0.5 ETH) `< msg.value` (1 ETH), so `refund = 0.5 ETH` is sent to `msg.sender`, which is `EvmHost`, not the user. [3](#0-2) 
5. The user's 0.5 ETH surplus is now held by `EvmHost` with no function exposed to return it to the user.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L143-149)
```text
        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-273)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-480)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
```
