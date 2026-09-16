## Title
Ineffective transaction-expiration check in `EvmHost` native-fee swaps (`block.timestamp` used as deadline) — (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all convert native token payments into `feeToken` via `IUniswapV2Router02.swapETHForExactTokens`, but pass `block.timestamp` as the swap's `deadline` argument instead of a caller-supplied, meaningful future deadline. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
Any unprivileged caller can invoke `dispatch()`/`fundRequest()` with `msg.value > 0` to have `EvmHost` swap native tokens for the exact `feeToken` amount needed to cover a POST/GET dispatch fee, using the chain's local Uniswap V2 router. The Uniswap deadline protection is designed to bound how long a signed transaction can remain valid in the mempool before it must revert rather than execute against a stale/manipulated price. Passing `block.timestamp` — evaluated at the moment the transaction is actually mined — makes the `deadline` check a permanent no-op: `require(deadline >= block.timestamp)` is always true regardless of how long the transaction sat pending. This is precisely the missing-transaction-expiration-check class described in the reference report (swap executed unconditionally at whatever price exists at mining time, with no bound on staleness).

Because this is an exact-output swap (`amountOut = post.fee`/`get.fee`/`amount`, capped by `msg.value` as the implicit max input), the practical consequence of the missing deadline is that a transaction that is delayed in the mempool (e.g., due to a gas-price spike or intentional delay/front-running) will still execute at whatever ETH/`feeToken` price exists at that later block, rather than reverting to protect the user from a worse rate. Compounding this, `EvmHost` never reclaims/forwards any unspent native token from the swap back to `_msgSender()` — the router refunds unspent ETH to `msg.sender` of the swap call, which is `EvmHost` itself, not the original transaction sender. Contrast this with the project's own `UniV3UniswapV2Wrapper.swapETHForExactTokens`, which correctly accepts a caller-supplied `deadline` and explicitly refunds unspent value to the original caller. [4](#0-3) 

### Impact Explanation
Every unprivileged user who dispatches an ISMP request or funds one with native token payment is exposed. A pending transaction that lingers (deliberately or due to network congestion) will not revert on stale pricing — it will execute at the current, possibly much worse, exchange rate, and any leftover native token from the swap is retained by `EvmHost` rather than returned to the payer. This is a direct value-loss vector for ordinary dispatch/fundRequest callers, reachable from a single unprivileged transaction, matching "Medium" severity per the bug class (loss of user funds via an unprotected swap during message dispatch, not merely a resource/DoS issue).

### Likelihood Explanation
High reachability: `dispatch()` and `fundRequest()` are the primary unprivileged entry points for the Hyperbridge dispatch/relayer-fee flow and accept native token payment by design in normal operation. The `deadline = block.timestamp` anti-pattern is deterministic (not a race condition) — it is always ineffective, so the exposure exists on every native-token dispatch, and is amplified during periods of gas volatility or targeted MEV activity against pending transactions.

### Recommendation
Add a caller-supplied `deadline` parameter to `DispatchPost`/`DispatchGet`/`fundRequest()` (or a fixed reasonable buffer such as `block.timestamp + maxSlippageWindow` computed at call time is still insufficient — it must be an argument fixed at transaction-signing time) and pass it through to `swapETHForExactTokens`. Additionally, after the swap, refund any unspent native token balance to `_msgSender()`/`post.payer` rather than allowing it to be retained by `EvmHost`.

### Proof of Concept
1. User A calls `EvmHost.dispatch{value: X}(post)` with `post.fee = F`, expecting the swap to consume roughly `X` ETH for `F` feeToken at the current pool price.
2. Due to a gas price spike, the transaction remains pending for an extended period.
3. During this window, the ETH/feeToken price on the local Uniswap V2 pool moves unfavorably for the pending swap parameters (or is manipulated via flash loan just before inclusion).
4. The transaction is eventually mined; `swapETHForExactTokens(F, path, address(this), block.timestamp)` is called with `deadline == block.timestamp` (always valid), so the swap proceeds and consumes up to the full `msg.value` at the now-worse price instead of reverting.
5. Any ETH not consumed by the swap is refunded by the router to `EvmHost` (the caller of the router), not to User A, permanently reducing what User A receives back versus what a properly deadline-protected and refund-forwarding flow would provide.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L114-156)
```text
    function swapETHForExactTokens(uint256 amountOut, address[] calldata path, address recipient, uint256 deadline)
        external
        payable
        returns (uint256[] memory)
    {
        address weth = _params.WETH;
        if (path[0] != weth) revert InvalidWethAddress();

        (bool sent,) = weth.call{value: msg.value}("");
        if (!sent) revert DepositFailed();

        IV3SwapRouter.ExactOutputSingleParams memory params = IV3SwapRouter.ExactOutputSingleParams({
            tokenIn: weth,
            tokenOut: path[1],
            fee: _params.maxFee,
            recipient: recipient,
            amountOut: amountOut,
            amountInMaximum: msg.value,
            sqrtPriceLimitX96: 0
        });

        bytes memory swapCall = abi.encodeWithSelector(IV3SwapRouter.exactOutputSingle.selector, params);

        bytes[] memory data = new bytes[](1);
        data[0] = swapCall;

        bytes[] memory results = IMulticallExtended(_params.swapRouter).multicall(deadline, data);
        uint256 spent = abi.decode(results[0], (uint256));

        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }

        uint256[] memory amounts = new uint256[](2);
        amounts[0] = spent;
        amounts[1] = amountOut;

        return amounts;
    }
```
