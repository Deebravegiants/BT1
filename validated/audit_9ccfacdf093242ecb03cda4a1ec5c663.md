## Analysis

The reported bug class — swaps executed without a real expiration deadline, exposing them to MEV/sandwich attacks when a transaction is held or delayed before inclusion — has a direct, reachable analog in `EvmHost.sol`'s native-token fee-swap paths.

### Title
Hardcoded `block.timestamp` deadline provides no MEV/sandwich protection for native-token fee swaps in `EvmHost` dispatch paths - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all convert user-supplied native tokens into `feeToken` via `IUniswapV2Router02.swapETHForExactTokens`, passing `block.timestamp` as the swap `deadline`. The same pattern is duplicated in `IntentGatewayV2.placeOrder` (both the mainline and the `evm/tron` copy). Using `block.timestamp` as the deadline is functionally equivalent to having *no* deadline: the check `deadline >= block.timestamp` inside the Uniswap router is evaluated against the timestamp of the block the transaction actually lands in, not the timestamp at which the user signed/submitted it. A validator or searcher can hold the transaction in the mempool indefinitely and include it whenever conditions are most favorable to them, and the deadline check will always pass.

### Finding Description [1](#0-0) [2](#0-1) [3](#0-2) 

In each of these functions, `swapETHForExactTokens{value: ...}(fee/amount, path, address(this), block.timestamp)` is called directly from unprivileged, permissionless entry points — any account can call `dispatch()` (post or get) or `fundRequest()` with `msg.value > 0`. Passing `block.timestamp` as the deadline argument nullifies the entire purpose of the deadline parameter, because it is impossible for a transaction to violate `deadline >= block.timestamp` once it is actually mined — the deadline is always satisfied "by definition" no matter how long the transaction sat pending. This is the same defect the external report flags in `UniV3SwapInput()`: no meaningful expiration protection against delayed/held execution, exposing the swap to price manipulation via front-running/sandwiching or delayed inclusion in unfavorable market conditions.

The same anti-pattern is repeated in `IntentGatewayV2.placeOrder`: [4](#0-3) 
and in the Tron variant: [5](#0-4) 

Note that these callers use `swapETHForExactTokens` (exact-output), so `amountInMaximum` is implicitly bounded by `msg.value`, which does cap the attacker's ability to force the caller to spend more ETH than sent. However, an attacker (e.g. a block-builder/validator or a searcher paying for priority) can still delay inclusion and/or sandwich the swap so that it consumes ETH much closer to the full `msg.value`, minimizing or eliminating the refund the router would otherwise send back — and in `EvmHost.dispatch`/`fundRequest`, that refund return value is never captured or forwarded back to the original caller (unlike `IntentGatewayV2.placeOrder`, which explicitly refunds unspent `msgValue`), so any ETH consumed beyond the true market-fair amount is effectively lost by the caller.

### Impact Explanation
Any user dispatching a cross-chain POST/GET request or funding a request with native token payment is exposed to a swap that can be timed or sandwiched by whoever controls block inclusion, forcing the user's ETH-to-feeToken conversion to execute at a worse price than intended, with no expiration safeguard to bound how long the transaction can be held before execution. Combined with `EvmHost.dispatch`/`fundRequest` not returning unspent ETH to the caller, this directly reduces user funds. This affects a core, frequently-used code path (every native-token-funded message dispatch and request funding call across all deployed `EvmHost` instances), qualifying as Medium severity consistent with the original report's rating.

### Likelihood Explanation
High reachability: `dispatch()` and `fundRequest()` are permissionless, unauthenticated entry points callable by any address, and native-token payment is a documented, encouraged payment mode. `IntentGatewayV2.placeOrder` with a native-token fee payment triggers the identical pattern. No special privileges or preconditions are required beyond supplying `msg.value`.

### Recommendation
Replace the hardcoded `block.timestamp` deadline with a genuine, caller-supplied (or bounded, e.g. `block.timestamp + MAX_SWAP_WINDOW`) deadline parameter threaded through `dispatch()`, `fundRequest()`, and `placeOrder()`, so that a transaction which sits in the mempool or is deliberately delayed past a reasonable window reverts instead of executing at a stale/manipulated price. Additionally, capture and refund any leftover native token from `swapETHForExactTokens` back to the original caller in `EvmHost.dispatch`/`fundRequest`, consistent with the refund logic already present in `IntentGatewayV2.placeOrder`.

### Proof of Concept
1. A user calls `EvmHost.dispatch(DispatchPost)` (or `dispatch(DispatchGet)`/`fundRequest`) sending `msg.value` in native token to cover `post.fee` in `feeToken`, generously buffered because the exact swap rate is unknown at submission time.
2. A searcher/validator observes the pending transaction and either (a) holds it until market conditions are less favorable, or (b) sandwiches it with front/back-run trades on the underlying Uniswap V2 pool.
3. Because `deadline = block.timestamp` is evaluated at inclusion time, the swap always passes the deadline check regardless of how long it was delayed or manipulated around.
4. The swap consumes ETH closer to (or at) `msg.value` due to the manipulated price; any residual ETH refunded by the router goes to `address(this)` (the `EvmHost` contract) and is never returned to the original caller in `dispatch`/`fundRequest`, resulting in a net loss of value to the user versus fair execution.

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

**File:** evm/src/core/EvmHost.sol (L1031-1040)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L375-392)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-488)
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
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```
