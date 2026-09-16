### Title
Excess native token sent to `EvmHost.dispatch()` / `fundRequest()` is permanently lost instead of refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` accept `msg.value` and swap it via Uniswap V2's `swapETHForExactTokens` for an *exact* amount of fee tokens (`post.fee`, `get.fee`, or `amount`). Any ETH the router does not need to fill that exact output is refunded — but the refund goes to `msg.sender` of the swap call, which is `EvmHost` itself, not the original transaction sender who supplied the `msg.value`. Unlike `IntentGatewayV2`/`IntentGatewayV2SameChainTest`, which explicitly track and refund unspent `msgValue` back to the caller after every native-token operation, `EvmHost` has no such refund step.

### Finding Description
In `EvmHost.dispatch(DispatchPost memory post)`: [1](#0-0) 

the full `msg.value` is forwarded to `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. The router computes the minimum ETH input required to produce exactly `post.fee` fee tokens and refunds the unspent portion — but by Uniswap V2 Router semantics, that refund is sent to whichever address called the router function, i.e., `EvmHost`, not to `_msgSender()` (the dispatching app/user). The function then proceeds to build the request and emit the event with no subsequent step that returns unspent native token to the caller: [2](#0-1) 

The same pattern repeats in the GET-request dispatcher and in `fundRequest`: [3](#0-2) 

By contrast, the `IntentGatewayV2` app, which performs an analogous native-token fee swap before dispatching, explicitly measures leftover `msgValue` and calls `_sendValue(msg.sender, msgValue)` to return any unspent ETH to the caller (verified by `testPlaceOrder_FeeSwap_RefundsExcessNativeToken`), demonstrating that the correct pattern (return unspent payment) is known and used elsewhere in the same codebase but is missing in `EvmHost` itself: [4](#0-3) 

Any application built with `HyperApp`/`IDispatcher` that calls `dispatch{value: msg.value}(...)` with more native token than strictly required for the fee swap (a very common case, since front-ends must estimate ETH input off-chain against a fluctuating AMM price, and the docs explicitly warn against using `quote()` on-chain due to sandwich-attack risk) will have the excess silently retained by `EvmHost` rather than returned.

### Impact Explanation
This is directly analogous to the LienToken `_payment` bug: a caller submits more native token than is actually owed for the relayer fee, and the protocol contract keeps the entire amount sent instead of taking only what is needed. Because `EvmHost` has no visible sweep/withdraw path for accumulated native ETH exposed here, the overpaid amount is permanently stranded, resulting in an unconditional loss of funds for any unprivileged caller (a message dispatcher, relayer-fee payer, or any `IApp`/user calling `dispatch`/`fundRequest` with native token) who overestimates the required ETH input, which — given AMM slippage and price movement between quote and execution — is the normal, expected case rather than an edge case.

### Likelihood Explanation
High likelihood: every consumer of `dispatch{value: msg.value}(...)` or `fundRequest{value: ...}(...)` that pays fees in native token is affected on every call unless they compute the exact Uniswap input amount ahead of time (which the docs themselves warn against doing on-chain, and is inherently imprecise off-chain due to slippage/front-running). This is a routine cross-chain message dispatch path reachable by any unprivileged sender submitting a single transaction — no special conditions or malicious actors are needed to trigger the loss.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2`: after the `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, compute the actual unspent ETH remaining in the contract (or measure balance before/after) and refund it to `_msgSender()` via a low-level call, instead of leaving it in `EvmHost`.

### Proof of Concept
1. A user (or `HyperApp` contract) calls `EvmHost.dispatch{value: X}(post)` where `post.fee = F` (denominated in fee token), and estimates `X` off-chain to safely cover the AMM price for `F` fee tokens.
2. `IUniswapV2Router02.swapETHForExactTokens{value: X}(F, path, address(this), deadline)` executes, needing only `Y < X` ETH to produce exactly `F` fee tokens; the router refunds `X - Y` ETH — to `EvmHost`, since `EvmHost` is the caller of the router.
3. `EvmHost.dispatch` completes, emitting `PostRequestEvent`, without ever transferring the `X - Y` ETH back to the original caller.
4. The caller's `X - Y` ETH is now stuck in `EvmHost` with no path back to them, constituting a direct, permanent loss of funds for every native-fee dispatch that isn't an exact-match payment.

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

**File:** evm/src/core/EvmHost.sol (L933-959)
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

**File:** evm/src/core/EvmHost.sol (L974-1051)
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

        uint64 timeoutTimestamp = get.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(get.timeout);
        GetRequest memory request = GetRequest({
            source: host(),
            dest: get.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            timeoutTimestamp: timeoutTimestamp,
            keys: get.keys,
            height: get.height,
            context: get.context
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
        emit GetRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: request.from,
            keys: request.keys,
            nonce: request.nonce,
            height: request.height,
            context: request.context,
            timeoutTimestamp: request.timeoutTimestamp,
            fee: get.fee
        });
    }

    /**
     * @dev Increase the relayer fee for a previously dispatched request.
     * This is provided for use only on pending requests, such that when they timeout,
     * the user can recover the entire relayer fee.
     *
     * @notice Payment can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * If called on an already delivered request, these funds will be seen as a donation to the hyperbridge protocol.
     * @param commitment - The request commitment
     * @param amount - The amount provided in `feeToken()`
     */
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

        FeeMetadata memory metadata = _requestCommitments[commitment];
        if (metadata.sender == address(0)) revert UnknownRequest();

        metadata.fee += amount;
        _requestCommitments[commitment] = metadata;

        emit RequestFunded({commitment: commitment, newFee: metadata.fee});
    }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3713-3752)
```text
    /// @notice placeOrder with fee swap refunds unused ETH after swapETHForExactTokens.
    function testPlaceOrder_FeeSwap_RefundsExcessNativeToken() public {
        uint256 inputAmount = 1000 * 1e6;
        uint256 feeAmount = 1 * 1e18; // 1 DAI worth of fees

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 1000,
            nonce: 0,
            fees: feeAmount,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        uint256 userEthBefore = user.balance;

        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        // Send 5 ETH for a fee swap that should cost much less
        intentGateway.placeOrder{value: 5 ether}(order, bytes32(0));
        vm.stopPrank();

        // User should get back most of the 5 ETH — the swap only needed a tiny fraction
        uint256 ethSpent = userEthBefore - user.balance;
        assertTrue(ethSpent < 1 ether, "User should have been refunded most of the 5 ETH");
        assertTrue(ethSpent > 0, "User should have spent some ETH on the fee swap");
    }
```
