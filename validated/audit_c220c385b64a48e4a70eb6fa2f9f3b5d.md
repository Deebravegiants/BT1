### Title
Excess native-token fee payment is permanently stranded in `EvmHost` instead of being refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` accept native-token (ETH) fee payment and swap the entire `msg.value` for the exact required amount of `feeToken` via `IUniswapV2Router02.swapETHForExactTokens`. Any unspent ETH from that swap is refunded by the Uniswap router to `msg.sender` of the swap call — but because `EvmHost` itself is the caller of the router (not the original transaction sender), the refund lands back in `EvmHost`'s own balance rather than being returned to the app/user who supplied the excess ETH. [1](#0-0) 

### Finding Description
Any `IApp`/user-facing contract that calls `IDispatcher(host).dispatch{value: msg.value}(post)` (the documented pattern for native-token fee payment) forwards `msg.value` directly into `EvmHost.dispatch`: [1](#0-0) 

Inside `dispatch`, when `msg.value > 0`, the full amount is passed to `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. The standard UniswapV2Router02 implementation swaps only `amounts[0]` (the exact input needed for `post.fee`) and refunds the difference `msg.value - amounts[0]` via `TransferHelper.safeTransferETH(msg.sender, ...)`. Since `EvmHost` is the direct caller of the router, `msg.sender` in that refund is `EvmHost`'s own address — the dust is sent right back into `EvmHost`'s balance, not to the app or end user who overpaid.

This is architecturally distinct from every other native-swap wrapper in the codebase, which explicitly re-forward unspent value to the true caller:
- `UniV3UniswapV2Wrapper.swapETHForExactTokens` explicitly computes `refund = msg.value - spent` and sends it back to `msg.sender`. [2](#0-1) 
- `UniV4UniswapV2Wrapper.swapETHForExactTokens` snapshots balance and explicitly refunds `refundETH` to `msg.sender`. [3](#0-2) 
- `IntentGatewayV2.placeOrder` explicitly tracks `msgValue -= amounts[0]` after the fee swap and is tested to refund the user's overpayment. [4](#0-3) [5](#0-4) 

`EvmHost.dispatch(DispatchPost)`/`dispatch(DispatchGet)` contains no equivalent tracking or refund logic — there is no post-swap step that measures leftover value and forwards it to `_msgSender()` or `post.payer`. [6](#0-5) 

Because `HyperFungibleToken`, `WrappedHyperFungibleToken`, and other `HyperApp`-based apps document and rely on the pattern "send `msg.value` and let the Host swap it" (users are told to estimate fees off-chain and may naturally overpay for safety margin), any user who supplies more native token than the exact swap requires — a normal occurrence given price/slippage estimation — permanently loses that excess to `EvmHost`'s contract balance. [7](#0-6) 

### Impact Explanation
This is the reverse mirror of the reported analog: rather than "excess ETH being stealable by the next caller," the excess ETH becomes value that is deposited into `EvmHost`'s own contract balance with no code path that credits it back to the payer, constituting a permanent, protocol-wide loss of user funds on every native-fee dispatch that overpays even slightly (which is expected in practice since `quote()` is explicitly documented as an imprecise, sandwich-attack-prone off-chain estimate). This qualifies as impact under "permanent freezing of funds" since ordinary unprivileged callers of `dispatch()` (via `HyperApp.dispatch`/`dispatchWithFeeToken` wrappers, `HyperFungibleToken.send`, `WrappedHyperFungibleToken.send`, and any custom `IApp`) have no way to recover the stranded ETH.

### Likelihood Explanation
High likelihood: this triggers on the routine, documented usage pattern of paying dispatch fees in native token, whenever the actual on-chain swap cost is even slightly less than what the caller supplied (normal slippage/estimation variance, or intentional safety margin), which is the common case since `quote()` is explicitly not meant for exact, atomic on-chain use.

### Recommendation
In `EvmHost.dispatch(DispatchPost)` and `dispatch(DispatchGet)`, after calling `swapETHForExactTokens`, capture the returned `amounts[0]` (amount actually spent) and refund `msg.value - amounts[0]` to `_msgSender()` (or `post.payer`/`get.payer`), mirroring the refund logic already present in `IntentGatewayV2.placeOrder`, `UniV3UniswapV2Wrapper`, and `UniV4UniswapV2Wrapper`.

### Proof of Concept
1. App `A` (e.g. a `HyperApp`-derived contract) calls `IDispatcher(host).dispatch{value: msg.value}(post)` where `msg.value` includes a safety margin above the exact quoted fee (standard documented usage).
2. Inside `EvmHost.dispatch`, `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` is invoked; the router spends only `amounts[0] < msg.value` and refunds the difference to `msg.sender`, which is `EvmHost` itself. [1](#0-0) 
3. `EvmHost.dispatch` returns without ever inspecting or forwarding this refunded dust; it simply remains part of `EvmHost`'s ETH balance.
4. The original payer has no function to reclaim this amount — `dispatch` has no output parameter reflecting spent value, and no subsequent withdraw path exists for regular users.

### Citations

**File:** evm/src/core/EvmHost.sol (L908-959)
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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L143-149)
```text
        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L83-96)
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-189)
```text
### Native Token Payment

For native token payments, dispatch directly and let the Host handle the Uniswap swap:

```solidity lineNumbers title="MyApp.sol"
contract MyApp is HyperApp {
    function sendMessageWithNative(
        bytes memory message,
        bytes memory dest,
        uint64 timeout,
        address to,
        uint256 relayerFee
    ) public payable returns (bytes32) {
        DispatchPost memory post = DispatchPost({
            body: message,
            dest: dest,
            timeout: timeout,
            to: abi.encode(to),
            fee: relayerFee,
            payer: msg.sender
        });
        
        // User must send enough native tokens to cover fees
        // The Host will swap native -> feeToken via Uniswap
        return IDispatcher(host()).dispatch{value: msg.value}(post);
    }
}
```
```
