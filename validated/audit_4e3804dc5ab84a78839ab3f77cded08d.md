### Title
Excess native ETH sent to `EvmHost.dispatch`/`fundRequest` is swapped in full and stranded in the contract instead of being refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` accept `msg.value` and forward the **entire** value to `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`, requesting only `fee`/`amount` worth of output tokens. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
A standard Uniswap V2 router's `swapETHForExactTokens` refunds any unspent ETH to `msg.sender` of that call. In these `EvmHost` functions, the caller of the router is `EvmHost` itself, not the original transaction sender. Any dust/overpayment refunded by the router therefore lands in `EvmHost`'s own balance rather than being returned to the account that supplied `msg.value`. `EvmHost` has no logic after the swap call to compute or forward any leftover ETH back to `_msgSender()`. Additionally, some `uniswapV2` wrapper implementations wired into `_hostParams.uniswapV2` (e.g. `GnosisUniswapV2Wrapper.swapETHForExactTokens`) deposit and forward the **full** `msg.value` as WETH to the caller (`EvmHost`), not just the `amountOut` requested — meaning any excess native tokens sent by the user are fully converted to fee-token and retained by `EvmHost` as unaccounted surplus, never credited to the user's dispatched request nor refunded. [4](#0-3) 

This is functionally identical to the reported bug class: a payable entrypoint that accepts `msg.value >= requiredAmount` without validating equality or refunding the difference, permanently stranding the caller's excess funds in the contract. Every other native-value entrypoint audited in this codebase (`IntentGatewayV2.placeOrder`, `fillOrder`, `ExtrinsicIntents._fillCrossChain`) explicitly tracks `msgValue` and calls `_sendValue(msg.sender, msgValue)` to refund any unspent amount, confirming this is the established pattern that `EvmHost.dispatch`/`fundRequest` fails to follow. [5](#0-4) [6](#0-5) 

### Impact Explanation
`EvmHost` is the core, unprivileged, externally-callable dispatch entrypoint reachable by any user or contract dispatching a POST/GET request or funding a pending request with native tokens (documented as the standard "Native Token Payment" pattern across all messaging guides). Any caller who over-estimates the required native fee (a very likely occurrence, since off-chain `quote()` estimates are explicitly documented as approximate due to Uniswap slippage) will have their excess ETH permanently trapped in `EvmHost`, with no function to reclaim it. This is a direct, permanent freezing-of-funds bug affecting every native-fee payer of the protocol's most-used entrypoint.

### Likelihood Explanation
High likelihood: the docs explicitly warn that native-token fee estimation is "Approximate (subject to slippage)" and recommend using `quote()` off-chain, which by nature will rarely match on-chain execution exactly. Every user who dispatches a POST/GET request or increases a relayer fee with native tokens (a documented, first-class payment method) is exposed, since `swapETHForExactTokens` will almost always leave some dust when the quoted amount and actual required amount diverge even slightly. [7](#0-6) 

### Recommendation
After each `swapETHForExactTokens{value: msg.value}(...)` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the actual ETH spent (via the returned `amounts[0]` or balance delta) and refund the difference (`msg.value - spent`) back to `_msgSender()`, mirroring the `_sendValue(msg.sender, msgValue)` pattern already used in `IntentGatewayV2` and `ExtrinsicIntents`. Additionally, audit non-standard `uniswapV2` wrapper implementations (e.g. `GnosisUniswapV2Wrapper`) to ensure they only consume/convert exactly the requested output amount rather than the entire `msg.value`, or otherwise return unused native value so `EvmHost` can refund it.

### Proof of Concept
1. User calls `EvmHost.dispatch{value: X}(DispatchPost{fee: F, ...})` where `X > amountRequiredToBuy(F)` (e.g. due to stale quote or intentional overpayment).
2. `EvmHost.dispatch` forwards `{value: X}` to `swapETHForExactTokens(F, path, address(this), block.timestamp)`. [1](#0-0) 
3. The router swaps only enough ETH to buy `F` fee tokens and refunds the remainder `X - spent` to `msg.sender`, which is `EvmHost`, not the user.
4. `EvmHost` proceeds to record the commitment and emit the event without ever inspecting or forwarding the leftover ETH. [8](#0-7) 
5. The leftover ETH permanently accumulates in `EvmHost`'s balance with no withdrawal path for the original depositor, confirmed by the absence of any refund/withdraw logic in the surrounding contract.

### Citations

**File:** evm/src/core/EvmHost.sol (L908-932)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * @param post - post request
     * @return commitment - the request commitment
     */
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

**File:** evm/src/core/EvmHost.sol (L934-959)
```text
        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
        emit PostRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: _msgSender(),
            to: abi.encodePacked(request.to),
            nonce: request.nonce,
            timeoutTimestamp: request.timeoutTimestamp,
            body: request.body,
            fee: post.fee
        });
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

**File:** evm/src/utils/uniswapv2/GnosisUniswapV2Wrapper.sol (L39-54)
```text
    function swapETHForExactTokens(uint256 amountOut, address[] calldata, address, uint256)
        external
        payable
        returns (uint256[] memory)
    {
        if (amountOut > msg.value) revert MsgValueLessThanExactAmount();

        (bool sent,) = WETH().call{value: msg.value}("");
        if (!sent) revert DepositFailed();

        IERC20(WETH()).safeTransfer(msg.sender, msg.value);

        uint256[] memory out = new uint256[](1);
        out[0] = msg.value;
        return out;
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L214-217)
```text
        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
