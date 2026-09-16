### Title
Users lose excess native token as unrecoverable "dust" when overpaying `EvmHost.dispatch`/`fundRequest` - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` accept arbitrary `msg.value` and forward it wholesale to `swapETHForExactTokens`, but never validate that `msg.value` equals the amount actually required for the swap, nor refund any leftover native token to the caller. Any overpayment is silently absorbed by the host contract as permanent "dust," analogous to `FootiumAcademy.mintPlayers` only checking `msg.value < totalFee` and never returning the difference.

### Finding Description
In `EvmHost.dispatch(DispatchPost)`, when `msg.value > 0` the full `msg.value` is sent to Uniswap's `swapETHForExactTokens`, requesting exactly `post.fee` output tokens: [1](#0-0) 

The identical pattern exists for GET requests: [2](#0-1) 

And for `fundRequest`: [3](#0-2) 

`swapETHForExactTokens` only consumes the ETH needed to produce the requested exact output amount and refunds any unused ETH to the caller of the router — which is `EvmHost` itself, not the original `msg.sender`. This refunded ETH lands back in the host via its own `receive()` function, whose comment confirms this is intentional/expected behavior rather than a bug being guarded against: [4](#0-3) 

Unlike the newer intents contracts in this same repository (`ExtrinsicIntents._fillCrossChain`, `IntentGatewayV2.placeOrder`), which explicitly track `msgValue` and call `_sendValue(msg.sender, msgValue)` to refund any excess native token to the caller, `EvmHost.dispatch`/`fundRequest` contain no such refund path. There is no check equivalent to `msg.value != requiredAmount` and no accounting of unused value back to the payer — it is unconditionally retained by the host contract as "dust."

### Impact Explanation
Because dispatching a POST/GET request or funding a request is an entirely permissionless action reachable by any unprivileged caller (any application or end user dispatching a cross-chain message through `EvmHost.dispatch`), any overestimate of the required native-token amount (which is expected in practice, since callers must estimate fees off-chain and add slippage/safety margin — the docs explicitly recommend using `quote()` off-chain and buffering for sandwich-attack protection) results in permanent loss of the excess ETH sent by the caller. That ETH is retained by the host and only recoverable by protocol governance via `IHostManager.withdraw`, restricted to `_hostParams.hostManager`, not by the original payer: [5](#0-4) 

This is a permanent freezing/loss of user funds with no self-service recovery path.

### Likelihood Explanation
Overpayment is a near-certain occurrence: on-chain the exact `amountIn` for a desired `feeToken` output can only be estimated in advance (subject to slippage/price movement between quote and execution), and the docs explicitly warn against computing exact quotes on-chain due to sandwich-attack risk, implying users routinely send extra native token as buffer. Every such buffered payment through `dispatch`/`fundRequest` results in silent loss of the excess.

### Recommendation
Track the ETH actually consumed by `swapETHForExactTokens` (its return value/`amounts[0]`) and refund `msg.value - amountsIn` back to `_msgSender()` (or the designated `payer`) in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, mirroring the refund pattern already implemented in `IntentGatewayV2`/`ExtrinsicIntents`.

### Proof of Concept
1. Caller estimates `post.fee` in feeToken terms and, following documented guidance to buffer for slippage, sends `msg.value` noticeably larger than the exact amount required by `swapETHForExactTokens` to yield `post.fee`.
2. `EvmHost.dispatch(DispatchPost)` forwards the entire `msg.value` to `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`.
3. Uniswap consumes only the exact ETH needed and refunds the remainder to `address(this)` (`EvmHost`), which accepts it via `receive()`.
4. The request commitment/dispatch completes successfully; the excess ETH remains in `EvmHost`'s balance with no state associating it with the caller.
5. The caller has no function to reclaim this excess; only governance (`withdraw`, restricted to `hostManager`) can move it out, and typically to a treasury, not back to the original payer.

### Citations

**File:** evm/src/core/EvmHost.sol (L383-386)
```text
    /*
     * @dev receive function for UniswapV2Router02, collects all dust native tokens.
     */
    receive() external payable {}
```

**File:** evm/src/core/EvmHost.sol (L651-660)
```text
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
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
