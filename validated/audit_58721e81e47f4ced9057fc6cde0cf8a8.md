### Title
Excess native ETH sent to `EvmHost.dispatch()` is permanently stuck instead of refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)` (and the analogous `dispatch(DispatchGet)` / `fundRequest`) is a `payable` entry point that any unprivileged application/user can call to pay dispatch fees in native token. It forwards the *entire* `msg.value` to `UniswapV2Router02.swapETHForExactTokens`, but never captures the returned `amounts[0]` (actual ETH spent) nor refunds the unspent remainder to the original caller.

### Finding Description
`EvmHost.dispatch()` is defined as: [1](#0-0) 

```solidity
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
    ...
```

The standard `UniswapV2Router02.swapETHForExactTokens` implementation refunds any unspent ETH via `TransferHelper.safeTransferETH(msg.sender, msg.value - amounts[0])`. Critically, from the router's point of view `msg.sender` is whoever called the router — here that's the `EvmHost` contract itself, not the original transaction sender (the app/user who called `EvmHost.dispatch()`). So any overpayment beyond the exact fee amount is refunded back into `EvmHost`'s own balance, not to the caller.

This is confirmed by the codebase's own pattern elsewhere: every other integration point that wraps `swapETHForExactTokens` explicitly captures the unspent amount and forwards it back to the real caller — e.g. `IntentGatewayV2.placeOrder()` computes `msgValue -= amounts[0]` and calls `_sendValue(msg.sender, msgValue)`: [2](#0-1) 

And the custom Uniswap wrapper contracts (`UniV3UniswapV2Wrapper`, `UniV4UniswapV2Wrapper`) explicitly unwrap/refund the leftover ETH to `msg.sender`: [3](#0-2) 

`EvmHost.dispatch()` has none of this refund logic — it discards the router's return value entirely. Since the docs explicitly warn users/integrators **not** to call `quote()` on-chain and to rely on an off-chain estimate (which by design includes slippage/buffer margin), every native-fee dispatch call is expected to routinely overpay: [4](#0-3) 

There is no `receive()`/native-ETH sweep function visible for ordinary users to reclaim this stuck balance from `EvmHost`; the only privileged interface (`IHostManager`) exists to withdraw protocol revenue/update params, not to refund individual overpayers, and is governance-gated. This is the same bug class as the report's `CollateralEscrowV1.depositAsset()` locked-ETH issue: a `payable` function accepts native value without an accounting path to return the unused portion to its rightful owner.

### Impact Explanation
Every call to `EvmHost.dispatch(DispatchPost)`/`dispatch(DispatchGet)` with `msg.value` greater than the exact swap cost permanently locks the excess ETH inside `EvmHost`. Because dispatch fees are quoted off-chain via a Uniswap `getAmountsIn` (subject to slippage per the docs' own warning), exact-match payments are the exception rather than the norm — this is a systemic, continuously-triggered loss of user funds across all EVM deployments of the host, reachable by any application or EOA dispatching a cross-chain POST/GET request with native-token fee payment.

### Likelihood Explanation
High likelihood: this path is hit on every native-fee dispatch (the default/primary fee payment method documented for end users), requires no privileged role, and is triggered by ordinary usage (any overestimate of the required native amount, which is expected given slippage buffers).

### Recommendation
Capture the return value of `swapETHForExactTokens` (`amounts[0]`) in `EvmHost.dispatch()`/`fundRequest`, compute the unspent `msg.value - amounts[0]`, and refund it to `_msgSender()` (mirroring the pattern already used in `IntentGatewayV2.placeOrder()`), rather than allowing the router's refund to be silently absorbed by the host contract.

### Proof of Concept
1. A user/app calls `IDispatcher(host).dispatch{value: X}(post)` where `X` is deliberately (or due to normal slippage-buffered off-chain quoting) larger than the exact ETH required to swap for `post.fee` fee-tokens.
2. `EvmHost.dispatch()` forwards the full `X` to `router.swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)`.
3. The router spends only `amountIn < X`, refunding `X - amountIn` back to `msg.sender` of the router call, which is `EvmHost`, not the original caller.
4. `EvmHost.dispatch()` ignores the return value and issues no refund; `X - amountIn` remains stuck in `EvmHost`'s native balance with no user-facing mechanism to reclaim it.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L141-149)
```text
        uint256 spent = abi.decode(results[0], (uint256));

        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
