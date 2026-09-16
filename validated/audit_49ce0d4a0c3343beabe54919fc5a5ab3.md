### Title
`EvmHost.dispatch`/`fundRequest` strand unused native-token change in the Host contract instead of refunding the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all accept `msg.value` and forward the *entire* value to `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)` without ever computing or returning the unused change to the original caller.

### Finding Description
When a user (or an app contract acting on a user's behalf) dispatches a POST/GET request or funds a request with native token payment, they don't know in advance the exact ETH cost of the `fee` amount of `feeToken` — they must send an upper-bound `msg.value`. `EvmHost` forwards the full `msg.value` to the Uniswap V2 router: [1](#0-0) 

The `swapETHForExactTokens` function on a canonical `UniswapV2Router02` only spends exactly `amounts[0]` ETH to obtain `post.fee` output tokens, and refunds `msg.value - amounts[0]` via `TransferHelper.safeTransferETH(msg.sender, ...)`. Critically, `msg.sender` from the router's perspective is `EvmHost` itself (the direct caller of the router), not `_msgSender()` (the original transaction sender). Any unused ETH change is therefore returned into `EvmHost`'s own balance rather than back to the user who supplied it.

The identical pattern repeats in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

None of these three functions compute a refund delta or forward any leftover native value back to `_msgSender()`/`msg.sender`. This is the exact bug class from the report: a payable entrypoint that swaps only part of the supplied ETH and never sweeps the remainder back to the payer.

By contrast, other native-swap helpers in this same codebase (`UniV3UniswapV2Wrapper.swapETHForExactTokens` and `UniV4UniswapV2Wrapper.swapETHForExactTokens`, and the app-level `IntentGatewayV2`/`IntrinsicIntents`/`ExtrinsicIntents` contracts) explicitly compute `refundETH = balanceAfter - balanceBefore` (or track `msgValue -= amounts[0]`) and call `_sendValue`/`.call{value: refund}` to return unspent ETH to `msg.sender`: [4](#0-3) [5](#0-4) 

This shows the intended/expected pattern for this codebase — refund unused native value — is missing specifically from `EvmHost`'s own `dispatch`/`fundRequest` functions, which is the core, most-reachable entrypoint for every app dispatching cross-chain messages with native payment (as documented in the Hyperbridge docs, which explicitly instruct app developers to call `IDispatcher(host()).dispatch{value: msg.value}(post)` directly): [6](#0-5) 

I could not find any `receive()`/rescue function in `EvmHost.sol` that later sweeps this stranded ETH back out to affected users; based on available context, unused ETH accumulates permanently in the Host contract's balance with no accounting of who it is owed to.

### Impact Explanation
Any user or downstream app (including `HyperFungibleToken.send`, `HyperbridgeLzEndpoint.send`, or any third-party `HyperApp`-based contract) that dispatches a POST/GET request or funds a request using native token payment and supplies a `msg.value` even slightly above the exact ETH cost of the router swap will have that difference permanently trapped in `EvmHost`, rather than refunded. Because callers cannot predict the exact on-chain swap rate at execution time, some margin is essentially always sent, so unaccounted ETH accumulates in the Host contract on every native-token dispatch. This constitutes a direct, permanent loss of user funds (frozen/stranded, and effectively harvestable/donated to the protocol with no user recourse), satisfying the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
Likelihood is high: this occurs on every single call to `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest` where `msg.value` is not the exact wei amount consumed by the Uniswap swap — which is the normal case since callers must estimate an upper bound and cannot know the precise swap execution price in advance. No malicious actor or special conditions are required; it's triggered by ordinary usage exactly as documented.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the actual amount spent (e.g., from the `amounts` array returned by `swapETHForExactTokens`, or by snapshotting `address(this).balance` before/after the swap) and transfer any leftover `msg.value` back to `_msgSender()` (or `msg.sender`) before returning, mirroring the refund logic already used in `UniV3UniswapV2Wrapper`/`UniV4UniswapV2Wrapper` and the `IntentGatewayV2`/`Intrinsic/ExtrinsicIntents` contracts elsewhere in this codebase.

### Proof of Concept
1. A user calls `EvmHost.dispatch(DispatchPost)` with `post.fee = 100` (feeToken units) and sends `msg.value = 1 ether`, expecting the swap to need far less than 1 ether of ETH to acquire 100 feeToken units.
2. `EvmHost.dispatch` calls `IUniswapV2Router02.swapETHForExactTokens{value: 1 ether}(100, path, address(this), block.timestamp)`.
3. The router spends, say, `0.01 ether` to obtain the 100 feeToken units and refunds the remaining `0.99 ether` to `msg.sender`, which is `EvmHost`'s own address (since `EvmHost` is the direct caller of the router), not the original user.
4. `EvmHost.dispatch` completes without ever inspecting or forwarding that `0.99 ether` back to the user; the ETH remains stuck in `EvmHost`'s balance.
5. Repeating this for every native-paid dispatch/fundRequest call across all users continuously accumulates stranded ETH in `EvmHost`, unrecoverable by the affected users through any documented or found mechanism.

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-188)
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
