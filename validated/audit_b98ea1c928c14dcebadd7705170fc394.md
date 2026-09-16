### Title
Excess native token sent to `EvmHost.dispatch()`/`fundRequest()` for ETH→feeToken swaps is refunded to the Host contract instead of the caller, permanently trapping user funds - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept `msg.value` and forward it to `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)` to buy an exact amount of `feeToken`, but none of them capture or forward the leftover ETH refund that the Uniswap router sends back.

### Finding Description
In each of the three payable entry points, when `msg.value > 0` the code does: [1](#0-0) [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` is a standard Uniswap V2 Router02 function that only spends as much ETH as needed to acquire the exact output amount, and refunds the unused ETH via `TransferHelper.safeTransferETH(msg.sender, ...)`. Because `EvmHost` itself is the caller of the router (not the original user who called `dispatch`/`fundRequest`), any refund from the router lands back in the `EvmHost` contract's balance, not in the hands of the original transaction sender. Since a caller can virtually never predict the exact swap output down to the wei (due to slippage/price movement between the client-side quote and execution), any caller sending slightly more ETH than the swap consumes will have that surplus permanently stuck in `EvmHost`.

This is structurally the same class of bug as the reported issue: an over-restrictive/overpay-prone payment path with no logic returning the surplus to the payer. Unlike other payable flows in this same repo (e.g. `IntentGatewayV2._fillCrossChain`, `ExtrinsicIntents`, and `UniV4UniswapV2Wrapper.swapETHForExactTokens`) which explicitly compute `msgValue -= amounts[0]` and call `_sendValue`/refund the caller, the three `EvmHost` functions have no such refund step: [4](#0-3) [5](#0-4) 

No `receive()`/`withdraw()` mechanism was found in `EvmHost.sol` for recovering this ETH either, meaning any surplus is trapped indefinitely (search for a native-ETH sweep/withdraw function in `EvmHost.sol` returned no results in the reviewed sections).

### Impact Explanation
Any unprivileged caller of `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` who pays with native token will almost always overpay relative to the exact swap output (due to price movement between fee estimation and execution, or simply rounding up their sent value for safety), and the excess ETH becomes permanently locked in `EvmHost` with no way for the user to reclaim it. This is a direct, protocol-wide loss of funds for every native-token payer across the primary dispatch and fee-funding paths of the bridge — a much broader blast radius than the original Allo pool-creation report since it affects every cross-chain message dispatch paid for in native token.

### Likelihood Explanation
High likelihood: this triggers on the ordinary, unprivileged, expected usage path (a single `dispatch{value: ...}` call) documented in the SDK/docs as the standard way to pay in native token, with no special preconditions, and it is essentially guaranteed to leave dust/surplus on every call where the sender doesn't send the exact wei amount consumed by the swap (which is nearly impossible to predict client-side given AMM slippage).

### Recommendation
After each `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the returned `amounts[0]` (actual ETH spent) and refund `msg.value - amounts[0]` back to `_msgSender()`, mirroring the pattern already used in `ExtrinsicIntents._fillCrossChain` and `UniV4UniswapV2Wrapper.swapETHForExactTokens`.

### Proof of Concept
1. Caller estimates the native-token amount needed to acquire `post.fee` of `feeToken` off-chain and calls `EvmHost.dispatch{value: estimatedAmount}(post)` where `estimatedAmount` is intentionally (or unavoidably, due to slippage buffer) higher than the amount actually required at execution time.
2. `dispatch` forwards the full `msg.value` to `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`.
3. The router spends only `amounts[0] <= msg.value` and refunds `msg.value - amounts[0]` ETH — but since `EvmHost` is `msg.sender` to the router, this refund is credited to `EvmHost`'s own balance, not returned to the caller.
4. `dispatch` returns normally without ever forwarding this leftover ETH to the caller; the caller has irreversibly lost `msg.value - amounts[0]` with no on-chain path in `EvmHost.sol` to recover it.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L375-397)
```text

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
