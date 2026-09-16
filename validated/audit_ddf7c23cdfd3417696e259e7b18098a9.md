### Title
Excess native `msg.value` in `EvmHost.dispatch()`/`fundRequest()` not refunded to caller after Uniswap swap - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token payment via `msg.value` and swap it for the exact required `feeToken` amount using `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)`. This is the same bug class as the referenced Sherlock report on `MultiInvoker._commitPrice()`: a function forwards the caller's full `msg.value` to a downstream call that only consumes part of it, and the leftover native token is never returned to the original transaction sender.

### Finding Description
In each of these three functions, the entire `msg.value` is forwarded to Uniswap's `swapETHForExactTokens`, which only needs enough ETH to buy the exact `post.fee`/`get.fee`/`amount` of `feeToken()`: [1](#0-0) [2](#0-1) [3](#0-2) 

By the standard Uniswap V2 Router semantics, `swapETHForExactTokens` refunds any unused ETH to `msg.sender` of that call. Since `EvmHost` itself is the direct caller of the router (not the original end user or the calling app contract such as `IntentGatewayV2` or `WrappedHyperFungibleToken`), any refund from the router is returned to `EvmHost`, not to the entity that originally supplied the excess `msg.value`. `EvmHost.sol` has no `receive()`/native-token withdrawal path visible in the reviewed portions of the contract to return this stranded ETH to the original caller. Every entry point that lets an unprivileged caller attach native value to `dispatch`/`fundRequest` — used directly by end users, by `IntentGatewayV2` for order fee payment, and by `WrappedHyperFungibleToken`/`HyperbridgeLzEndpoint` when forwarding `msg.value` — is affected: [4](#0-3) [5](#0-4) [6](#0-5) 

Unlike `IntentGatewayV2`, which explicitly tracks `amounts[0]` returned from the swap and reduces its own accounted `msgValue` before any further use, `EvmHost.dispatch`/`fundRequest` discard the `amounts` return value entirely and never track or refund unspent value: [7](#0-6) 

### Impact Explanation
Any caller (directly or via an integrating app contract) who overestimates the native token needed to cover the fee-token swap (due to price movement/slippage buffer, or simply passing a generous `msg.value`) permanently loses the difference — it becomes ETH stuck in `EvmHost` with no code path shown to reclaim or forward it back to the payer. This is a direct, unrecoverable loss of user funds reachable from an ordinary unprivileged `dispatch`/`fundRequest` call, matching the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
High likelihood: every dispatch of a POST/GET request or fee top-up paid in native token goes through this code path. The documentation itself warns that native-token payment has slippage risk (`docs/content/developers/evm/messaging/post-requests.mdx` lines 244-249), which is precisely the scenario that leaves excess `msg.value` after the swap — the leftover is silently forfeited rather than being explicitly slippage-protected or refunded.

### Recommendation
Capture the actual ETH consumed by the swap (via the returned `amounts[0]` from `swapETHForExactTokens`, or by comparing `address(this).balance` before/after) and refund the unused portion of `msg.value` to `msg.sender`/the payer using a low-level call, in `EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()`.

### Proof of Concept
1. Call `EvmHost.dispatch{value: X}(post)` where `X` is intentionally larger than the ETH amount required to purchase `post.fee` units of `feeToken` via the configured Uniswap V2 router (e.g., pass a generous buffer to account for slippage, as the docs recommend).
2. `EvmHost.dispatch` forwards the full `msg.value` (`X`) to `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)`.
3. The router uses only the ETH needed to satisfy `post.fee` and refunds the remainder — but because `EvmHost` is the caller of the router, the refund lands in `EvmHost`'s own balance, not back to the caller of `dispatch`.
4. `EvmHost.dispatch` never inspects the swap's returned `amounts` or the difference in balance, and performs no refund transfer to `_msgSender()`/`post.payer`.
5. The caller's overpayment (`X - amounts[0]`) is permanently unrecoverable from `EvmHost`.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L375-389)
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-281)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L296-306)
```text
        if (msg.value > 0) {
            IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            // Fee tokens already transferred to this contract by OFT's _payLzToken.
            // The quoted lzTokenFee includes a buffer above the relayer fee so the
            // legacy deployed host's per-byte protocol fee can be paid out of it;
            // approve our full feeToken balance and let the host take what it needs.
            address feeToken = IDispatcher(_host).feeToken();
            IERC20(feeToken).forceApprove(_host, IERC20(feeToken).balanceOf(address(this)));
            IDispatcher(_host).dispatch(request);
        }
```
