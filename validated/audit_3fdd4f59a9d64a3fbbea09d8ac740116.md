### Title
Excess ETH from fee-swap is silently stripped from the caller and permanently stuck in `EvmHost` when dispatching POST/GET requests or funding a request - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all convert `msg.value` into `feeToken()` via `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`, but discard the returned `amounts[0]` (actual ETH spent) and never forward the router's dust-ETH refund back to the caller.

### Finding Description
Uniswap V2's `swapETHForExactTokens` only spends what is required to obtain the exact output (`fee`) and refunds `msg.value - amounts[0]` to whoever called the router — in this case that is `EvmHost` itself, since `EvmHost` is the direct caller of the router, not the end user: [1](#0-0) 

The same unchecked pattern repeats in `dispatch(DispatchGet)` and `fundRequest`: [2](#0-1) [3](#0-2) 

None of these functions capture the router's return value or refund the leftover ETH to `_msgSender()`. This is the exact class of bug from the Juicebox report: a swap is executed with an over-supplied input amount, the swap only consumes what is needed, and the unspent remainder is left stranded in the contract instead of being returned to the payer.

This is directly comparable to how the same repository handles it correctly elsewhere — `IntentGatewayV2`/`ExtrinsicIntents` explicitly track `amounts[0]` from the swap and refund the difference: [4](#0-3) 

and the standalone Uniswap wrapper contracts (`UniV3UniswapV2Wrapper`, `UniV4UniswapV2Wrapper`) both explicitly compute and refund unspent ETH back to `msg.sender`: [5](#0-4) 

`EvmHost`'s three fee-swap call sites are the only ones in the codebase that omit this refund step.

### Impact Explanation
Any user or application calling `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` with `msg.value` greater than the ETH actually required to buy `post.fee`/`get.fee`/`amount` worth of fee token will have the surplus ETH permanently trapped in `EvmHost`. There is no governance/admin sweep visible for stray native ETH in `EvmHost` (only ERC20 fee-token accounting exists), so the loss is effectively permanent for the caller. Because `dispatch()` is the primary unprivileged entry point used by every app built on Hyperbridge (intent gateway, token bridges, `HyperFungibleToken`, custom apps) to pay for cross-chain message dispatch, this affects a wide surface of production message flows, not an edge case.

### Likelihood Explanation
Overpaying `msg.value` for a fee-token swap is a normal integration pattern (callers typically send a generous ETH buffer to guarantee the swap succeeds despite slippage, exactly as done in `IntentGatewayV2` and the SDK's fee-quoting flow, and as explicitly tested in `IntentGatewayV2Test.testPlaceOrder_FeeSwap_RefundsExcessNativeToken`). Any caller who follows that same pattern against `EvmHost.dispatch()`/`fundRequest()` directly (rather than exclusively through `IntentGatewayV2`) will lose the difference. This requires no privileged role, no timing/race condition, and triggers on ordinary usage.

### Recommendation
Capture the `amounts` array returned by `swapETHForExactTokens` in all three call sites (`dispatch(DispatchPost)`, `dispatch(DispatchGet)`, `fundRequest`) and refund `msg.value - amounts[0]` to `_msgSender()`, mirroring the pattern already used in `IntentGatewayV2`/`ExtrinsicIntents`.

### Proof of Concept
1. Call `EvmHost.dispatch{value: 1 ether}(DispatchPost{fee: 1e6, ...})` where converting `1e6` fee-token units only requires, say, `0.01 ether`.
2. Internally, `IUniswapV2Router02.swapETHForExactTokens{value: 1 ether}(1e6, path, address(this), block.timestamp)` spends `0.01 ether` and refunds `0.99 ether` to `address(this)` (i.e., `EvmHost`), per standard Uniswap V2 router semantics.
3. `dispatch()` never reads the returned `amounts[0]` nor forwards any refund to `msg.sender`; the `0.99 ether` remains in `EvmHost`'s balance with no code path to withdraw native ETH back to the original caller.
4. The caller has permanently lost `0.99 ether`. [1](#0-0)

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L140-149)
```text
        bytes[] memory results = IMulticallExtended(_params.swapRouter).multicall(deadline, data);
        uint256 spent = abi.decode(results[0], (uint256));

        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```
