### Title
Loss of surplus ETH in EvmHost native-fee dispatch paths - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept `msg.value` as an optional native-token payment for the relayer fee. When native value is supplied, the host swaps it for the exact fee-token amount via `swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`, but never captures or refunds the leftover ETH to the caller who actually sent it.

### Finding Description
In each of these functions, whenever `msg.value > 0`, the Uniswap V2 router is called with the caller's entire `msg.value` as the maximum input: [1](#0-0) [2](#0-1) [3](#0-2) 

`UniswapV2Router02.swapETHForExactTokens` only spends `amounts[0]` (the amount actually required to obtain `fee`) and refunds `msg.value - amounts[0]` back to its immediate caller — here, `EvmHost` itself, not the end user who originated the `dispatch`/`fundRequest` transaction (`_msgSender()`). The `dispatch`/`fundRequest` functions discard the `amounts` return value entirely and perform no comparison against `msg.value`, nor any subsequent transfer of unspent ETH back to `_msgSender()`.

This is the same root cause as the referenced Sherlock finding in `ExchangeProxy.executeSwapDirect()`: a payable entry point checks only that `msg.value` is *sufficient* (or, here, doesn't check it at all against the actual cost) and never refunds the difference, so any surplus becomes stuck in the contract.

Notably, the codebase elsewhere (`IntentGatewayV2.placeOrder`, `ExtrinsicIntents._fillCrossChain`) correctly implements this exact refund pattern by tracking `msgValue -= amounts[0]` and calling `_sendValue(msg.sender, msgValue)` for any remainder — confirming the intended design is to refund excess native value, but that pattern was not applied to `EvmHost.dispatch()` / `EvmHost.fundRequest()`. [4](#0-3) 

### Impact Explanation
Any user or integrating contract (including third-party apps built on Hyperbridge, e.g. `WrappedHyperFungibleToken.send()` or `HyperbridgeLzEndpoint`) that calls `EvmHost.dispatch()`/`fundRequest()` with native ETH and slightly overestimates the required fee (due to price movement between quoting and execution, or simply rounding up) permanently loses the difference. The ETH accumulates in the `EvmHost` contract with no built-in mechanism shown in this function set to return it to depositors, resulting in a direct, permanent loss of user funds. Given `dispatch()` is the core, permissionless message-dispatch entry point used by every app built on Hyperbridge, this affects a wide surface of callers, not an edge case.

### Likelihood Explanation
Likelihood is high: any caller providing native value slightly above the exact swap requirement (which is essentially guaranteed unless they compute the exact router quote atomically in the same block) triggers the loss on every such call. This is a normal usage pattern documented for consumers who "pay with native token" for dispatch fees, e.g. `WrappedHyperFungibleToken` docs describe native-token fee payment with a wrapper computing `msgValue`, but the underlying `EvmHost.dispatch()` itself has no refund logic when called directly.

### Recommendation
Capture the `amounts` array returned by `swapETHForExactTokens` in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, and refund `msg.value - amounts[0]` back to `_msgSender()` (or `post.payer`/`get`'s originator as appropriate) after the swap, mirroring the pattern already used in `IntentGatewayV2.placeOrder`/`ExtrinsicIntents._fillCrossChain` (`_sendValue(msg.sender, msgValue)`).

### Proof of Concept
1. A user (or an app such as `WrappedHyperFungibleToken`) calls `EvmHost.dispatch{value: X}(post)` where `X` is intentionally or unintentionally larger than the ETH cost required to obtain `post.fee` fee tokens via the configured Uniswap V2 router.
2. Inside `dispatch`, `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` executes, spending only `amounts[0] < X` and refunding `X - amounts[0]` to `address(this)` (the `EvmHost` contract), per standard Uniswap V2 router behavior.
3. `dispatch` returns without ever inspecting `amounts` or transferring `X - amounts[0]` back to the original caller.
4. The surplus ETH remains locked in the `EvmHost` contract balance, unrecoverable by the depositor through any function shown in `dispatch`/`fundRequest`.

Note: I was unable to fully verify within the available context whether `EvmHost` exposes any owner/admin-only ETH withdrawal function elsewhere in the contract that could recover this stray balance (search for `withdraw`/`sweep` in `EvmHost.sol` returned no distinct matching function bodies in the indexed context). If such a function exists, the funds may be recoverable only through privileged action rather than automatically to the affected user — the core defect (missing per-call refund to `_msgSender()`) still stands regardless.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-933)
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
