### Title
Excess native ETH sent to `EvmHost.dispatch()` / `fundRequest()` is not refunded to the caller and becomes permanently stranded in the contract - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept `msg.value` and forward the *entire* value to a Uniswap-style router's `swapETHForExactTokens()` to buy a fixed `amount`/`fee` of `feeToken()`. None of these functions compute the amount actually spent by the swap and refund the difference to `_msgSender()`. This is the exact bug class described in the reference report (payable functions that collect ETH for a fee but never refund the excess).

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

the whole `msg.value` is sent to the router with `swapETHForExactTokens{value: msg.value}(post.fee, ...)`. The identical pattern is used in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest()`: [3](#0-2) 

The router implementations used across chains behave inconsistently but never return the leftover value to the original transaction sender:
- The generic Uniswap V2/V3/V4 wrapper (`UniV4UniswapV2Wrapper.swapETHForExactTokens`) refunds unspent ETH — but only to `msg.sender` of the swap call, which is `EvmHost` itself, not the end user: [4](#0-3) 
- The Gnosis wrapper doesn't refund at all — it wraps the *entire* `msg.value` into `WETH()`/feeToken and transfers all of it (not just `amountOut`) to `EvmHost`: [5](#0-4) 

In every case, any ETH beyond what's needed for the swap ends up sitting in `EvmHost`'s own balance/feeToken balance, and `EvmHost` has no logic afterward to forward that surplus back to the caller. `EvmHost.sol` has no `receive()`/refund logic for this in any of the three payable entry points shown above, confirmed by grepping for refund/receive patterns.

This is unlike the project's own `IntentGatewayV2` and `ExtrinsicIntents` contracts, which explicitly track `msgValue` after the swap and call `_sendValue(msg.sender, msgValue)` to return the unspent amount, e.g.: [6](#0-5) 

and are specifically tested for this behavior: [7](#0-6) 

`EvmHost.dispatch()`/`fundRequest()` lack this equivalent refund step and equivalent test coverage (no matches for overpayment-refund tests against `EvmHost`).

### Impact Explanation
Any unprivileged user or application calling `EvmHost.dispatch()` (POST/GET) or `EvmHost.fundRequest()` with native token payment and sending more ETH than the swap actually consumes (a very common occurrence, since callers/front-ends estimate fees using `quote()` off-chain against a fluctuating AMM price, or intentionally add slippage buffer) will permanently lose the excess ETH. The surplus becomes stuck in `EvmHost`'s balance (as native ETH from the UniV3/UniV4 wrapper flow) or as extra feeToken balance (Gnosis flow), with no mechanism exposed to the paying user to reclaim it. This is a direct, protocol-wide loss of user funds affecting every native-token dispatch across all EVM deployments of Hyperbridge, not an edge case — it will occur on essentially every native-fee-paying dispatch that doesn't send the exact optimal amount.

### Likelihood Explanation
High likelihood: `dispatch()` is the primary, most-used entry point for sending cross-chain messages and is payable by design specifically to support native-token fee payment via Uniswap swap. Front-end fee estimation via `quote()` is explicitly documented as being used for a rough/off-chain estimate (with the docs warning that it's vulnerable to sandwich attacks and can be imprecise), so real-world callers will regularly send more ETH than strictly required to avoid reverts from price movement between quoting and execution. Every such call bleeds the surplus into the contract permanently.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the actual amount spent from `swapETHForExactTokens` (it returns `amounts[0]` = ETH spent) and refund `msg.value - amountSpent` back to `_msgSender()` via a safe ETH transfer, mirroring the pattern already used in `IntentGatewayV2`/`ExtrinsicIntents` (`_sendValue(msg.sender, msgValue)`). Ensure this refund logic is added uniformly across all three payable functions and add regression tests analogous to `testPlaceOrder_FeeSwap_RefundsExcessNativeToken` for `EvmHost`.

### Proof of Concept
1. Caller estimates required native ETH via `IHyperApp.quote()`/frontend estimate, then calls `IDispatcher(host).dispatch{value: X}(post)` where `X` intentionally includes slippage buffer (standard practice per the project's own docs at `docs/content/developers/evm/messaging/post-requests.mdx`).
2. Inside `dispatch()`, `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` is called; the underlying router only needs `Y < X` ETH to acquire `post.fee` of feeToken.
3. The router (e.g., `UniV4UniswapV2Wrapper`) refunds `X - Y` back to its caller, `EvmHost`, per [8](#0-7) .
4. `dispatch()` never forwards this `X - Y` back to the original caller — execution proceeds straight to building the `PostRequest`/emitting the event as shown at [9](#0-8) .
5. Result: caller permanently loses `X - Y` ETH, now sitting in `EvmHost`'s balance with no path back to the user.

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

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L83-100)
```text
        // Snapshot standing balance (excluding inbound msg.value) so the refund is the swap-call delta only,
        // immune to any ETH that lands on the wrapper from outside the router (e.g., selfdestruct, coinbase).
        uint256 balanceBefore = address(this).balance - msg.value;

        IUniversalRouter(_params.universalRouter).execute{value: msg.value}(
            abi.encodePacked(bytes1(uint8(Commands.V4_SWAP))), inputs, deadline
        );

        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
        }

        amounts = new uint256[](2);
        amounts[0] = msg.value - refundETH;
        amounts[1] = amountOut;
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L203-217)
```text
        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
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
