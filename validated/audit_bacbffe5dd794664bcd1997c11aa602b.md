### Title
EvmHost dispatch/fundRequest functions do not refund excess native token overpayment - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept `msg.value` and swap it through `IUniswapV2Router02.swapETHForExactTokens` to obtain an exact amount of fee token, but never refund the leftover native token to the original caller, matching the class of bug described in the external report (excess payment not returned to the payer).

### Finding Description
All three payable entrypoints in `EvmHost.sol` follow the same pattern: if `msg.value > 0`, the full `msg.value` is forwarded to the configured UniswapV2 router via `swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`. [1](#0-0) [2](#0-1) [3](#0-2) 

The standard UniswapV2Router02 implementation of `swapETHForExactTokens` refunds any leftover ETH beyond the amount actually needed for the exact-output swap back to `msg.sender` of that call — which, in these code paths, is `EvmHost` itself (the router is called *by* the Host, not by the original transaction sender). Nowhere in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` is there any subsequent logic that forwards this router refund back to `_msgSender()`/the original payer. Compare this to the equivalent flow in `IntentGatewayV2`/`ExtrinsicIntents`, where excess `msg.value` is explicitly tracked and refunded to the user after the same kind of Uniswap swap: [4](#0-3) [5](#0-4) 

`EvmHost` has no analogous refund step, so any dispatcher, relayer, or app that overestimates the required native fee and sends more ETH than the swap actually consumes has that surplus silently absorbed into the Host contract's own balance instead of being returned.

### Impact Explanation
Because the excess ETH lands as a plain balance increase on the `EvmHost` contract (not tracked in any accounting struct like `FeeMetadata`), it is not recoverable by the original caller through any user-facing function. This is a direct, permanent loss of funds for any account that calls `dispatch()` or `fundRequest()` with `msg.value` exceeding the exact swap input — a realistic scenario since callers must estimate the ETH amount needed for a Uniswap "exact output" swap ahead of time (price/slippage is unknown at call time) and will typically send a buffer to avoid the transaction reverting with `INSUFFICIENT_INPUT_AMOUNT`.

### Likelihood Explanation
High. `dispatch()` and `fundRequest()` are core, unprivileged, permissionless entrypoints reachable by any dispatcher, app, or relayer paying with native token as documented ("Native token (ETH, BNB, POL, DOT etc.) Sent with transaction via msg.value... Automatically swapped to fee token via Uniswap"). Overpayment is the normal/expected mode of use since the exact swap-in amount can't be predicted precisely off-chain, and the docs themselves instruct users to send native value without describing any refund mechanism for the Host-level swap paths. [6](#0-5) 

### Recommendation
After each `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, compute the leftover native balance (or capture the returned `amounts[0]` actually spent) and forward `msg.value - amounts[0]` back to `_msgSender()` (or an explicit `payer`/`refundTo` parameter), following the same pattern already used in `IntentGatewayV2`/`ExtrinsicIntents.sol` and in the `UniV3UniswapV2Wrapper`/`UniV4UniswapV2Wrapper` contracts, which correctly refund unspent ETH after the swap. [7](#0-6) 

### Proof of Concept
1. A user (or app contract on behalf of a user) calls `EvmHost.dispatch(DispatchPost)` with `post.fee = X` and `msg.value = Y` where `Y > amount_actually_needed_to_swap_for_X_fee_tokens` (a realistic buffer against price movement/slippage). [1](#0-0) 
2. `IUniswapV2Router02.swapETHForExactTokens{value: Y}(X, path, address(this), block.timestamp)` executes: it deposits only the exact ETH needed into WETH, performs the swap, and refunds `Y - amountSpent` ETH to `msg.sender`, i.e., to the `EvmHost` contract itself (since `EvmHost` is the caller of the router).
3. Execution returns to `dispatch()`, which proceeds directly to building the `PostRequest`/emitting the event — no code path sends the refunded `Y - amountSpent` back to the original caller. [8](#0-7) 
4. The surplus ETH remains in `EvmHost`'s balance permanently; the caller has no function to reclaim it, resulting in a direct loss equal to the overpaid amount. The identical pattern repeats in `dispatch(DispatchGet)` and `fundRequest()`. [2](#0-1) [3](#0-2)

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L115-127)
```text
## Payment Methods

The Hyperbridge protocol ultimately collects its fees in the `feeToken` (usually a stablecoin). But it can also accept native token payments, which are automatically swapped for the `feeToken` using the local AMMs like Uniswap.


| Token | Payment Method |
|-------|----------------|
| Native token (ETH, BNB, POL, DOT etc.) | Sent with transaction via `msg.value` |
| Fee token (set by IsmpHost) | Requires ERC20 approval before dispatch |

<Callout type="info">
For testing purposes on testnet, you can use the testnet fee token, [Hyper USD](https://sepolia.etherscan.io/address/0xBe97E73126d66188d72FBf99029126d0340a7f18). The contract address is the same across several EVM chains. Check out the [guide](/developers/guides/testnet-fee-token) on how to get the token. 
</Callout>
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
