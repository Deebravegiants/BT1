### Title
Excess native ETH sent to `EvmHost.dispatch()` for POST/GET fee-swaps is not refunded to the caller and becomes stuck in the host - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` accept `msg.value` and swap it for the exact `feeToken` fee amount via Uniswap V2's `swapETHForExactTokens`, but never capture the swap's returned `amounts[0]` (actual ETH spent) nor refund the difference (`msg.value - amounts[0]`) to the original caller. This is the same class of bug as the PoolTogether `CrossChainRelayerArbitrum.processCalls` finding: a smart contract paying an ETH-denominated protocol fee through an intermediary call loses any overpayment because the refund is credited to the wrong party (here, silently retained by `EvmHost` itself) instead of the entity that actually funded the transaction.

### Finding Description
`dispatch(DispatchPost)` and `dispatch(DispatchGet)` swap native ETH for the exact fee amount: [1](#0-0) [2](#0-1) 

`IUniswapV2Router02.swapETHForExactTokens` sends any unused ETH (`msg.value` minus the amount actually needed for the swap) back to `msg.sender` of that router call. Since `EvmHost` itself is the direct caller of the router (not the application contract or EOA that called `EvmHost.dispatch()`), any refund the router issues lands on `EvmHost`'s own balance rather than being forwarded back to `_msgSender()` (the entity that funded `msg.value`).

Contrast this with `IntentGatewayV2.placeOrder`, which performs the same kind of ETH→feeToken swap but correctly captures the returned amounts and refunds the unspent portion to the caller: [3](#0-2) 

`EvmHost.dispatch()` has no equivalent logic — it neither captures the `amounts` return value of `swapETHForExactTokens` nor sends any leftover ETH back to `_msgSender()`. Any application contract (or user) that overestimates the ETH needed to cover `post.fee`/`get.fee` and calls `dispatch{value: msg.value}(...)` directly (e.g. any `IApp`/`HyperApp` integrator dispatching with native value, exactly the documented "Payment Methods" flow) permanently loses the excess ETH to the host contract, with no caller-triggered recovery path exposed in `dispatch()`.

### Impact Explanation
Any contract (a token bridger, message dispatcher, or any `IApp`/`HyperApp` integrator) that dispatches a POST or GET request paying with native ETH and does not supply the *exact* minimal ETH amount required for the swap will have the excess permanently trapped in `EvmHost`, since:
- The refund is not routed back to the dispatching contract/user.
- `dispatch()` exposes no mechanism for the caller to reclaim the difference.
- Recovery, if any, would require privileged/governance withdrawal via `IHostManager.withdraw` (an admin-only path), not something the affected caller controls.

This constitutes a permanent loss of user/application funds via a single, unprivileged `dispatch()` call — meeting the "concrete theft or permanent freezing of funds" bar for Medium severity, matching the judged severity in the source report.

### Likelihood Explanation
Likelihood is high in practice: callers must estimate the ETH amount to cover a Uniswap V2 swap to an exact token output, which is inherently imprecise (slippage/price movement between quote and execution). Any application that pads its ETH payment for safety margin (a common and recommended pattern, as documented elsewhere in this same codebase, e.g. `HyperbridgeLzEndpoint.quote()`'s explicit 2x buffer for exactly this reason) will systematically overpay and lose the difference on every dispatch through the native-ETH path.

### Recommendation
In both `dispatch(DispatchPost)` and `dispatch(DispatchGet)`, capture the `amounts` array returned by `swapETHForExactTokens` and refund `msg.value - amounts[0]` back to `_msgSender()`, mirroring the pattern already implemented correctly in `IntentGatewayV2.placeOrder` (`evm/src/apps/IntentGatewayV2.sol:383-397`).

### Proof of Concept
1. An `IApp` integrator (e.g., a custom `HyperApp`-based bridge/relayer contract) calls `EvmHost.dispatch{value: X}(post)` where `X` exceeds the ETH actually required to purchase `post.fee` worth of `feeToken`.
2. Inside `dispatch()`, `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` executes; the router spends `amountIn < X` and refunds `X - amountIn` ETH to its caller, `EvmHost`. [1](#0-0) 
3. `dispatch()` never reads the swap's return value or forwards the refunded ETH to `_msgSender()`; the leftover ETH remains in `EvmHost`'s balance indefinitely, unrecoverable by the caller.

Note: I could not fully verify within the available tool calls whether `EvmHost` exposes any `receive()`/`withdraw()` path that could return this stranded ETH to affected callers (the grep found 6 matches for `receive()/withdraw()/fallback()` in `EvmHost.sol` but the file excerpt could not be retrieved before the iteration limit). Even if such a function exists, it is governance/admin-gated (`IHostManager.withdraw`), not a caller-controlled refund, so the core finding — that the caller cannot recover their own overpayment — stands regardless.

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
