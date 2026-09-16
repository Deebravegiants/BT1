### Title
Excess native-token payment in `EvmHost.dispatch`/`fundRequest` is refunded to the Host contract instead of the user, permanently freezing user funds - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)` and `EvmHost.fundRequest` are `payable` functions that let any unprivileged caller pay dispatch fees in native token. When `msg.value > 0`, the Host forwards the full `msg.value` to the configured Uniswap V2-compatible router/wrapper via `swapETHForExactTokens`, requesting an exact amount of fee tokens (`post.fee`/`get.fee`/`amount`). Any unspent ETH from that swap is refunded by the router to its immediate caller — which is `EvmHost` itself, not the original end user. `EvmHost` has no function to withdraw stray native balance or forward it back to the payer, so any overpayment is permanently stuck in the contract.

### Finding Description
`dispatch(DispatchPost)` and `dispatch(DispatchGet)` accept `msg.value` and, when non-zero, call the router's `swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`: [1](#0-0) [2](#0-1) 

`fundRequest` does the same for adding relayer fees: [3](#0-2) 

Looking at one of the concrete router implementations used for this swap, `UniV3UniswapV2Wrapper.swapETHForExactTokens`, any leftover ETH after the exact-output swap is refunded to `msg.sender` of that call: [4](#0-3) 

Because `EvmHost` itself is the caller of `swapETHForExactTokens` (not the end user who invoked `dispatch`), `msg.sender` inside the wrapper resolves to `EvmHost`'s own address. This is the same behavior for the canonical Uniswap V2 `Router02.swapETHForExactTokens`, which also refunds dust ETH to its immediate caller. Consequently, any amount a user sends above what's needed to cover `post.fee`/`get.fee`/`amount` is swept back into `EvmHost`'s balance rather than back to the user, and `EvmHost` provides no `receive()`-triggered accounting, no per-user refund tracking, and no owner/governance-only sweep function to release this native balance. The interface documentation itself only exposes `dispatch`/`fundRequest`/`feeToken`/`nonce`/etc., with nothing for reclaiming native ETH: [5](#0-4) 

### Impact Explanation
Because dispatching a request via native token is documented as the standard flow (client code cannot exactly predict the router's live swap rate at execution time and is instructed to add slack via `msg.value`), users are highly likely to over-supply ETH to guarantee the swap succeeds. Every unit of overpayment is transferred out of user control into `EvmHost` and becomes permanently unrecoverable — no owner, admin, or `HostManager` function exists to withdraw this stray native balance for reimbursement. This is a concrete freezing-of-funds bug reachable by any ordinary user via a single `dispatch()` transaction, not merely a "gas optimization" cosmetic issue as the reported analog implies.

### Likelihood Explanation
High. `dispatch()` is the primary unprivileged entry point for cross-chain messaging and is documented for native-fee payment across multiple app integrations (`HyperApp`, `WrappedHyperFungibleTokenUpgradeable.send`), meaning every native-fee-paying transaction is exposed to this loss whenever the exact swap price differs from the amount sent — which is the normal case, since callers must send `msg.value >= quote` and quotes drift with each block due to AMM pricing.

### Recommendation
After performing the swap in `dispatch`/`fundRequest`, compute the ETH actually consumed and refund any leftover `msg.value` directly to `_msgSender()` (or `post.payer`/`get.payer` where applicable) instead of relying on the router to refund `EvmHost`. Additionally, add an owner/`HostManager`-gated sweep function to recover any native ETH balance accidentally stuck in `EvmHost` from past transactions or third-party donations.

### Proof of Concept
1. User calls `EvmHost.dispatch{value: 1 ether}(post)` where `post.fee` only requires 0.5 ETH worth of fee token at the current AMM price.
2. `EvmHost` forwards the full 1 ETH to `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)`.
3. The router/wrapper spends only what's needed (e.g., 0.5 ETH) and refunds the remaining ~0.5 ETH to its caller, `EvmHost` (see `UniV3UniswapV2Wrapper.sol` lines 143-149).
4. `EvmHost` now holds the 0.5 ETH refund with no bookkeeping tied to the user and no function to send it back or let an admin sweep it out for reimbursement — the funds are permanently frozen in the contract.

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

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L118-164)
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

    /**
     * @dev Increase the relayer fee for a previously dispatched request.
     * This is provided for use only on pending requests, such that when they timeout,
     * the user can recover the entire relayer fee.
     *
     * @notice Payment can be made with either the native token or the IHost.feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the IHost.feeToken.
     *
     * If called on an already delivered request, these funds will be seen as a donation to the hyperbridge protocol.
     * @param commitment - The request commitment
     * @param amount - The amount provided in `IHost.feeToken()`
     */
    function fundRequest(bytes32 commitment, uint256 amount) external payable;
```
