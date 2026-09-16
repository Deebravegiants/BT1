## Title
Excess native-token fees paid via `dispatch()`/`fundRequest()` are swept into `EvmHost` instead of refunded to the sender - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native-token payment for protocol fees and convert it to the fee token via Uniswap's `swapETHForExactTokens`. Any `msg.value` sent in excess of the exact amount required to buy `post.fee` / `get.fee` / `amount` fee-tokens is not returned to the caller — it is refunded by the Uniswap router to `EvmHost` itself and permanently retained there, with a comment explicitly confirming this is by design.

### Finding Description
In `dispatch(DispatchPost)`, when `msg.value > 0` the contract swaps the entire `msg.value` for exactly `post.fee` fee-tokens: [1](#0-0) 

`IUniswapV2Router02.swapETHForExactTokens` only spends the ETH actually required to obtain `post.fee` tokens and refunds any surplus ETH back to `msg.sender` of that call — which is `EvmHost`, not the original caller who supplied `msg.value`. The identical pattern exists in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest()`: [3](#0-2) 

`EvmHost` implements a `receive()` function whose comment confirms this dust-collection is intentional: "receive function for UniswapV2Router02, collects all dust native tokens": [4](#0-3) 

None of `dispatch()`, `fundRequest()` forward the refunded surplus back to `_msgSender()`/`post.payer`. The excess simply accumulates as native-token balance on `EvmHost`, and the only way to recover it is through the privileged `IHostManager.withdraw()` path controlled by the `hostManager`/admin, not by the user who overpaid: [5](#0-4) 

This directly mirrors the reported AvailBridge `sendMessage()` bug class: a fee-paying function checks only that `msg.value` (or the swap input) is sufficient, but has no refund path for anything paid beyond the exact fee, so ordinary users routinely lose the difference between what they send and the actual fee consumed.

### Impact Explanation
Any unprivileged caller of `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` who pays in native token — which is the documented, encouraged payment path per the docs (`docs/content/developers/evm/messaging/post-requests.mdx`) — loses any ETH sent above the exact Uniswap-quoted amount. Because on-chain quotes (`getAmountsIn`) can shift between the time a client quotes a fee and the time the transaction executes (AMM price movement across blocks, or a caller intentionally adding slippage buffer), essentially all native-fee dispatches leak value into the Host contract, which only the privileged host manager can later reclaim. This is a direct, unrecoverable-by-the-user loss of funds, satisfying the "concrete loss/freezing of user funds" threshold.

### Likelihood Explanation
High likelihood: this occurs on every native-token-funded dispatch/fundRequest call where `msg.value` doesn't exactly match the instantaneous Uniswap quote, which is close to guaranteed given AMM price drift and typical client-side slippage buffers. No malicious actor is required — it is a normal user-facing code path (`dispatchWithFeeToken`/native `dispatch` used throughout `HyperApp`, `HyperFungibleToken`, `WrappedHyperFungibleTokenUpgradeable`, `HyperbridgeLzEndpoint`, `IntentGatewayV2`, etc.).

### Recommendation
Track the actual ETH consumed by `swapETHForExactTokens` (its return value is the array of amounts, where `amounts[0]` is ETH spent) and refund `msg.value - amounts[0]` directly to `_msgSender()` in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, rather than allowing the Uniswap refund to be absorbed into the Host's own balance.

### Proof of Concept
1. Caller calls `EvmHost.dispatch{value: X}(post)` where `X` is `post.fee`'s quoted native-token cost plus a slippage buffer (a normal user pattern, and also what happens whenever the AMM price improves between quote-time and execution-time).
2. `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` spends only `amounts[0] < X` ETH to acquire exactly `post.fee` fee-tokens, and refunds `X - amounts[0]` ETH to `address(this)` (`EvmHost`) via its `receive()`.
3. `dispatch()` returns without any accounting or forwarding of the refunded dust to the original caller.
4. The caller's excess ETH is now permanently part of `EvmHost`'s balance, recoverable only by the host manager via `IHostManager.withdraw()` — the caller has no way to reclaim it. [1](#0-0) [4](#0-3)

### Citations

**File:** evm/src/core/EvmHost.sol (L74-96)
```text
interface IHostManager {
    /**
     * @dev Updates IsmpHost params
     * @param params new IsmpHost params
     */
    function updateHostParams(HostParams memory params) external;

    /**
     * @dev withdraws bridge revenue to the given address
     * @param params, the parameters for withdrawal
     */
    function withdraw(WithdrawParams memory params) external;
}

// Withdrawal parameters
struct WithdrawParams {
    // The beneficiary address
    address beneficiary;
    // the amount to be disbursed
    uint256 amount;
    // Withdraw the native token?
    address token;
}
```

**File:** evm/src/core/EvmHost.sol (L383-386)
```text
    /*
     * @dev receive function for UniswapV2Router02, collects all dust native tokens.
     */
    receive() external payable {}
```

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
