### Title
Excess native ETH sent to `EvmHost.dispatch`/`fundRequest` is stuck in EvmHost and never refunded to the caller - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept native ETH via `msg.value` and swap it through Uniswap V2 for the exact `feeToken` amount needed. Uniswap's `swapETHForExactTokens` refunds any unspent ETH to its immediate caller — which is `EvmHost` itself, not the original transaction sender. None of these three functions forward that residual balance back to `_msgSender()`, so any overpayment of native ETH is permanently trapped inside `EvmHost`.

### Finding Description
In `EvmHost.dispatch(DispatchPost)`: [1](#0-0) 

the same pattern repeats in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

In all three, `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)` is called directly by `EvmHost`. Per the standard UniswapV2Router02 implementation, `swapETHForExactTokens` refunds `msg.value - amountIn` back to `msg.sender` — which in this call context is `EvmHost` (the router sees `EvmHost` as its caller), not the account that originally sent ETH into `EvmHost`. Any unspent ETH therefore lands back on `EvmHost`'s own balance. None of these functions capture the swap's `amounts[0]` return value or otherwise compute/forward a refund of unspent native ETH back to `_msgSender()`.

This is architecturally identical to the referenced report's root cause: a contract accepts the caller's full `msg.value`, forwards it to an inner operation that only consumes part of it, and the unconsumed remainder is retained by the intermediate contract rather than being swept back to the actual payer.

The bug is directly reachable by any unprivileged caller. Besides direct calls to `IDispatcher(host).dispatch{value: ...}` (as documented for native-token payment), it is also reachable through `IntentGatewayV2`/`ExtrinsicIntents` cross-chain flows, e.g. `_post`, which forwards a caller-supplied `nativeFee` straight to `host.dispatch` without any means of recovering leftover ETH after the internal swap: [4](#0-3) 

Because `IDispatcher.dispatch` only returns a `bytes32 commitment` (no spent-amount data), the calling app has no way to detect or reclaim any leftover ETH that the internal Uniswap swap refunded into `EvmHost`: [5](#0-4) 

### Impact Explanation
Since native-token fee estimation off-chain is explicitly documented as approximate/slippage-prone ("Use the `quote()` view function... **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain..."), users and integrating apps are expected to send a `msg.value` that may exceed the exact fee-token cost by design/buffer. Any such overpayment across `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` becomes permanently locked inside `EvmHost`, with no code path returning it to the payer. This is a direct, protocol-wide loss of user/solver funds across every native-fee dispatch path in the system, satisfying "permanent freezing of funds" for the affected users.

### Likelihood Explanation
This triggers on ordinary usage, not an attack: any account calling `IDispatcher(host).dispatch{value: msg.value}(post)` (or `dispatch(DispatchGet)`/`fundRequest`) with even a small buffer above the exact Uniswap-quoted cost — which is normal practice to avoid reverts from price movement between quoting and execution — loses the excess irrecoverably. Given native-token payment is a first-class, documented payment method, likelihood of occurrence is high.

### Recommendation
Capture the `amounts[0]` (ETH actually spent) returned by `swapETHForExactTokens` in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, and refund `msg.value - amounts[0]` back to `_msgSender()` (or `payer`) at the end of each function, mirroring the pattern already correctly implemented in `IntentGatewayV2.placeOrder`: [6](#0-5) 

### Proof of Concept
1. A user calls `EvmHost.dispatch{value: 1 ether}(post)` where `post.fee` (in feeToken) only requires 0.3 ETH worth of native input to swap for via Uniswap.
2. Inside `dispatch`, `swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)` spends ~0.3 ETH and the router refunds ~0.7 ETH — but since `EvmHost` is the caller of the router, this refund lands on `EvmHost`'s own balance.
3. `dispatch` completes without forwarding any of the ~0.7 ETH back to the user; the funds remain in `EvmHost` indefinitely, with no function in the shown code path returning them to the original payer.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L126-142)
```text
    /// @dev Posts `body` to the gateway on the order's source chain, paying `nativeFee` in native
    /// tokens when non-zero and in the fee token otherwise.
    function _post(Order calldata order, bytes memory body, uint256 relayerFee, uint256 nativeFee) internal {
        DispatchPost memory request = DispatchPost({
            dest: order.source,
            to: abi.encodePacked(_instance(order.source)),
            body: body,
            timeout: 0,
            fee: relayerFee,
            payer: msg.sender
        });
        if (nativeFee > 0) {
            IDispatcher(host()).dispatch{value: nativeFee}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L118-146)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the IHost.feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the IHost.feeToken.
     *
     * @param request - post request
     * @return commitment - the request commitment
     */
    function dispatch(DispatchPost memory request) external payable returns (bytes32 commitment);

    /**
     * @dev Dispatch a GET request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the IHost.feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the IHost.feeToken.
     *
     * @param request - get request
     * @return commitment - the request commitment
     */
    function dispatch(DispatchGet memory request) external payable returns (bytes32 commitment);
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
