## Analysis Result

### Title
Excess native ETH sent to `EvmHost.dispatch`/`fundRequest` for fee swaps is permanently donated to the host instead of refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept `msg.value` and swap the *entire* amount through `swapETHForExactTokens`, but only need `post.fee`/`get.fee`/`amount` worth of fee tokens. The `swapETHForExactTokens` call refunds any leftover native ETH to its own caller — which is `EvmHost` itself, not the original `_msgSender()` — and `EvmHost` never captures or forwards that refund back to the user.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

and identically in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

In each case, the full `msg.value` is forwarded with `swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`, but the return value (the `amounts` array with the actual ETH spent) is **discarded** — `EvmHost` never checks it and never refunds unspent value to `_msgSender()`.

This differs materially from every other caller pattern in the same codebase that performs the identical swap: `IntentGatewayV2.placeOrder` captures `amounts[0]` and explicitly refunds the difference to `msg.sender` via `_sendValue`, and `WrappedHyperFungibleTokenUpgradeable.send` does the same. `EvmHost` itself lacks this logic.

Crucially, the swap functions (both the canonical `UniswapV2Router02.swapETHForExactTokens` and this repo's custom wrapper `UniV3UniswapV2Wrapper.swapETHForExactTokens`) refund any unspent ETH to `msg.sender` of the swap call: [4](#0-3) 

Since `EvmHost` is the one calling the router/wrapper, `msg.sender` in that refund is `EvmHost`, not the original transaction sender. The refunded ETH lands in and stays in `EvmHost`'s balance permanently — there is no `receive()`/`withdraw()` path shown in `EvmHost.sol` that returns this to the depositor; it becomes an unrecoverable donation.

This is directly reachable by any unprivileged contract or EOA (via a `HyperApp`-derived app, `IntentGatewayV2`'s cross-chain fee path, `HyperbridgeLzEndpoint`, `WrappedHyperFungibleTokenUpgradeable`, etc.) that calls `IDispatcher(host).dispatch{value: msg.value}(...)` with a `msg.value` larger than the on-chain quoted fee — which is explicitly recommended practice in the docs (e.g., "Apply a generous 2x buffer to absorb the legacy deployed host's per-byte protocol fee"): [5](#0-4) 

Any slippage between an off-chain `quote()` estimate and the actual on-chain Uniswap price, or any deliberate overpayment buffer, results in permanent loss of the difference for every single dispatcher/app in the protocol, not just an edge case.

### Impact Explanation
Every dispatch of a POST or GET request paid in native token, and every `fundRequest` call paid in native token, that supplies `msg.value` even slightly above the exact fee token cost will silently and permanently forfeit the excess ETH to the `EvmHost` contract balance. Because `quote()` is explicitly documented as an off-chain, non-atomic estimate subject to sandwich/slippage risk, and because SDKs/adapters recommend buffering `msg.value` (2x buffer example above), this is not a rare user error but a systemic value leak affecting essentially all native-fee dispatches across the protocol (IntentGatewayV2 cross-chain fills, LZ endpoint adapter, HyperFungibleToken transfers, and any custom `HyperApp`). This constitutes a concrete, protocol-wide loss of user funds with no on-chain recovery mechanism, satisfying a Medium-severity impact.

### Likelihood Explanation
High. This triggers on the default/only code path for native-token fee payment in `dispatch()`/`fundRequest()` — there is no special condition required beyond `msg.value > post.fee`'s Uniswap-equivalent, which will almost always occur in practice due to price movement between quote and execution, or intentional overpayment buffers recommended in the docs.

### Recommendation
Capture the `amounts` array returned by `swapETHForExactTokens` in all three functions (`dispatch(DispatchPost)`, `dispatch(DispatchGet)`, `fundRequest`) and refund `msg.value - amounts[0]` back to `_msgSender()`, mirroring the pattern already implemented in `IntentGatewayV2.placeOrder` and `WrappedHyperFungibleTokenUpgradeable.send`.

### Proof of Concept
1. Any application contract calls `IDispatcher(host).dispatch{value: msg.value}(post)` where `post.fee` requires only `X` ETH-equivalent but the caller sends `Y > X` ETH (e.g., due to slippage buffer or price movement since an off-chain `quote()`).
2. `EvmHost.dispatch` forwards the full `msg.value = Y` to `swapETHForExactTokens{value: Y}(post.fee, path, address(this), block.timestamp)`.
3. The router/wrapper spends only `X` and refunds `Y - X` to its caller, `EvmHost` (per `UniV3UniswapV2Wrapper.sol` lines 143-149 or standard UniswapV2Router02 behavior).
4. `EvmHost.dispatch` never reads the returned `amounts` and never sends anything back to the original caller; the `Y - X` difference remains stuck in `EvmHost`'s ETH balance indefinitely.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L143-149)
```text
        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L337-345)
```text
        // Apply a generous 2x buffer to absorb the legacy deployed host's
        // per-byte protocol fee (the in-source host has no such markup). Excess
        // native is refunded by the uniswap router; excess feeToken approval is
        // simply unused.
        if (_params.payInLzToken) {
            return MessagingFee({nativeFee: 0, lzTokenFee: request.fee * 2});
        } else {
            return MessagingFee({nativeFee: quote(request) * 2, lzTokenFee: 0});
        }
```
