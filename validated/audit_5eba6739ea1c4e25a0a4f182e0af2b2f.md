## Title
`IntentGatewayV2.placeOrder` executes its native-fee Uniswap swap with `deadline = block.timestamp`, providing no real deadline protection - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
When a user places an order and pays the solver fee (`order.fees`) in native ETH, `placeOrder` swaps ETH for the fee token via UniswapV2 using `swapETHForExactTokens`, but passes `block.timestamp` as the `deadline` argument instead of a caller-supplied deadline. [1](#0-0)  Because `block.timestamp` is evaluated at execution time (whichever block eventually includes the transaction), the router's `deadline >= block.timestamp` check is trivially satisfied no matter how long the transaction sits in the mempool — this is functionally equivalent to having no deadline at all, mirroring the reported `ArrakisV2Router.addLiquidity` bug class.

### Finding Description
`placeOrder` is a fully unprivileged, user-reachable entry point for the Intent Gateway escrow flow. [2](#0-1)  When `order.fees > 0` and the caller funded the call with native tokens (`msgValue > 0`), the contract performs an on-chain swap to acquire the exact fee-token amount needed:

```solidity
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
    order.fees, path, address(this), block.timestamp
);
``` [3](#0-2) 

The `Order` struct already carries a `deadline` field, but it is only checked later in `fillOrder` to gate order expiry (`order.deadline < blockNumber`) [4](#0-3)  — it is never threaded into this swap. Instead, the swap deadline is hardcoded to `block.timestamp`, which always equals "now" at execution time regardless of when the transaction was originally signed/submitted. This removes any bound on how long a validator/searcher can hold the transaction before including it, exactly the missing-deadline pattern flagged in the source report for `ArrakisV2Router.addLiquidity`.

The same pattern also appears in `SimplexPaymaster.swapAndDeposit`, but that function is `treasury`-gated and thus out of scope per the exclusion rules for privileged-caller-only paths. [5](#0-4)  The `placeOrder` instance, by contrast, is reachable by any unprivileged user placing an intent order with a native-fee payment.

### Impact Explanation
Because the swap is exact-output (`order.fees` fixed, `amountInMax` implicitly bounded by `msgValue`), a delayed/sandwiched inclusion cannot make the router revert outright, but it can be timed or sandwiched by a searcher/validator to force the trade to execute at the worst available ETH/fee-token price up to the full `msgValue` bound. Since any ETH not consumed by the swap is refunded to the user (`msgValue -= amounts[0]`, refunded at the end of `placeOrder`) [6](#0-5) , an adversary who withholds/replays the transaction to a favorable block can extract value from the user's refund via price manipulation, i.e., a stale-price / sandwich MEV extraction against user funds — a concrete value-loss (fund-draining) vector, matching the classification of "concrete theft ... of funds."

### Likelihood Explanation
Any user placing an order with a non-zero `order.fees` and paying in native ETH triggers this code path; no special permissions or preconditions are required beyond a normal `placeOrder` call, and MEV searchers/validators routinely watch mempools for exactly this kind of unprotected on-chain swap.

### Recommendation
Add a `deadline` parameter (or reuse a strict, caller-supplied timestamp) to the `placeOrder`/`Order` interface and thread it into `swapETHForExactTokens` instead of `block.timestamp`, so that the swap can be rejected if it is not mined within the user-intended window.

### Proof of Concept
1. User A calls `placeOrder` with `order.fees = X` (fee token amount) and sends `msgValue` in native ETH sufficient to cover `X` at the current market rate, expecting the swap to execute near-immediately.
2. A validator/searcher observes the pending transaction and withholds/reorders it (or the tx is stuck in the mempool during high gas volatility) until a block where the ETH/fee-token price has moved unfavorably (e.g., via a sandwich attack around the eventual inclusion block).
3. Because `deadline = block.timestamp` is computed at execution time, `swapETHForExactTokens`'s deadline check always passes, so the swap proceeds regardless of the delay.
4. The swap consumes a larger amount of the user's native ETH (up to `msgValue`) to obtain the same `order.fees` amount of fee tokens, reducing the ETH refunded to User A versus what they would have received had the swap executed promptly — realizing MEV extraction at the user's expense.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
```

**File:** evm/src/apps/IntentGatewayV2.sol (L375-397)
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

        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L443-445)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
        uint256 blockNumber = _blockNumber();
        if (order.deadline < blockNumber) revert Expired();
```

**File:** evm/src/utils/SimplexPaymaster.sol (L454-476)
```text
    function swapAndDeposit(address token, uint256 amountIn) external {
        if (msg.sender != treasury) revert UnauthorizedCall();
        address router = IDispatcher(host()).uniswapV2Router();
        if (router == address(0)) revert InvalidRouter(router);
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;

        address[] memory path = new address[](2);
        path[0] = token;
        path[1] = IUniswapV2Router02(router).WETH();

        IERC20(token).forceApprove(router, amountIn);
        uint256[] memory amounts = IUniswapV2Router02(router)
            .swapExactTokensForETH(amountIn, amountOutMin, path, address(this), block.timestamp);

```
