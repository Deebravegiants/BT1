## Analysis

The reachable analog to this report is **`EvmHost`'s native-ETH-to-feeToken conversion path**, which hardcodes `block.timestamp` as the UniswapV2 swap deadline exactly like the audited `BalancerV2Swap.sol` finding, and is reachable by any unprivileged caller in a single transaction.

### Title
Hardcoded `block.timestamp` deadline in `EvmHost`'s native-fee UniswapV2 swaps enables sandwich extraction of dispatcher-supplied ETH - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all convert native ETH sent with the call into the protocol fee token via `IUniswapV2Router02.swapETHForExactTokens`, passing `block.timestamp` as the swap's `deadline` argument. Because this "deadline" is computed at execution time rather than supplied by the caller, it imposes no real time bound — a block producer/searcher can withhold or reorder the transaction until the AMM pool has been manipulated into its most unfavorable price for the exact-output swap, exactly the classic swap-deadline sandwich pattern described in the source report.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

The identical pattern recurs in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

Any unprivileged account can call `dispatch(...)` or `fundRequest(...)` with `msg.value > 0` in a single transaction — no permission, allowlist, or prior state is required. Each of these paths computes `amounts[0] = getAmountsIn(post.fee, path)` inside `swapETHForExactTokens` at whatever price the pool holds when the transaction is finally mined, and requires only `amounts[0] <= msg.value`. Passing `block.timestamp` as the deadline (rather than a caller-supplied, off-chain-chosen expiry) means the swap accepts execution at *any* block the miner/searcher chooses to include it in, no matter how long the transaction sits in the mempool/bundle queue. A searcher can therefore front-run the call by buying the feeToken (raising its ETH price), forcing the fixed-output swap to consume far more ETH from `msg.value` than a fair-price execution would, and back-run to restore the price — capturing the price-impact spread as MEV profit extracted directly from the ETH the caller sent to `EvmHost`.

The identical hardcoded-`block.timestamp` swap pattern is also reachable through `IntentGatewayV2.placeOrder`'s fee-swap step: [4](#0-3) 

By contrast, the codebase demonstrates the fix is already known and applied elsewhere: `UniV3UniswapV2Wrapper.swapETHForExactTokens` accepts a caller-supplied `deadline` parameter and forwards it to the underlying router's `multicall(deadline, data)`, explicitly documented as providing "deadline protection": [5](#0-4) 

This confirms the vulnerability class is understood in this codebase for the V3 wrapper, but `EvmHost`'s direct UniswapV2 calls (and `IntentGatewayV2`'s) were left with the unprotected `block.timestamp` pattern.

### Impact Explanation
Any unprivileged user dispatching an ISMP request or funding one with native ETH is exposed to MEV sandwich extraction on the mandatory ETH→feeToken swap. Because the deadline can never actually expire relative to the block it lands in, the transaction can be held/reordered by a searcher/validator indefinitely until the pool state is at its worst for the caller, and the value siphoned off (the inflated ETH cost of acquiring the fixed `post.fee`/`get.fee`/`amount` output) is real economic loss extracted from user-supplied funds on every affected `dispatch`/`fundRequest`/`placeOrder` call that pays in native ETH. This satisfies "concrete theft ... of funds" via a route that any unprivileged dispatcher can trigger.

### Likelihood Explanation
High likelihood: `dispatch`, `fundRequest`, and `placeOrder` are the core, permissionless, frequently-called entry points of the Hyperbridge messaging and intents systems whenever a caller pays fees in native ETH rather than the fee token directly — this is an advertised, first-class payment option (see the function NatSpec: "If native tokens are supplied, it will perform a swap under the hood using the local uniswap router"). Any MEV searcher monitoring the mempool for such calls with non-trivial `msg.value` can profitably sandwich them with standard AMM manipulation, requiring no special access.

### Recommendation
Add a caller-supplied `deadline` (and ideally a caller-supplied `amountInMax` distinct from raw `msg.value`, or a `minOut`-style slippage bound) to `DispatchPost`, `DispatchGet`, and `fundRequest`'s parameters, and thread it through to `swapETHForExactTokens` instead of hardcoding `block.timestamp`. Apply the same fix to `IntentGatewayV2`'s fee-swap call. This mirrors the deadline-parameter approach already implemented in `UniV3UniswapV2Wrapper`.

### Proof of Concept
1. A user calls `EvmHost.dispatch(DispatchPost)` with `msg.value = X` ETH intending to cover `post.fee` feeTokens via the local UniswapV2 pool at the current fair price.
2. The transaction is observed in the mempool/bundle by a searcher/validator; because the swap's deadline is computed as `block.timestamp` at execution (not a caller-chosen expiry), the searcher can safely delay inclusion or bundle a front-run trade.
3. The searcher front-runs by buying the feeToken with ETH in the same pool, raising the ETH price of `post.fee` tokens.
4. `EvmHost`'s call to `swapETHForExactTokens(post.fee, path, address(this), block.timestamp)` executes at the manipulated price; since `block.timestamp` always satisfies the deadline check, the call does not revert on staleness — it computes `amounts[0]` (ETH consumed) at the inflated price, up to the `msg.value` ceiling.
5. The searcher back-runs, selling the feeToken back and capturing the price-impact spread as profit — value that was extracted from the ETH the original user supplied to `EvmHost`. [1](#0-0)

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

**File:** evm/src/apps/IntentGatewayV2.sol (L375-386)
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
```

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L106-140)
```text
    /**
     * @notice Swaps ETH for exact amount of tokens through V3 with deadline protection.
     * @param amountOut The exact amount of tokens to receive
     * @param path Array of token addresses representing the swap path
     * @param recipient Address that will receive the output tokens
     * @param deadline Unix timestamp deadline by which the transaction must confirm
     * @return amounts Array of amounts [ethSpent, tokensReceived]
     */
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
```
