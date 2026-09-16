Confirmed across `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, all three use `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`, where the refund recipient is `address(this)` (the `EvmHost` contract itself), not the original caller. This is the direct analog to the PhiFactory bug.

### Title
Native-token overpayment in `EvmHost.dispatch`/`fundRequest` is silently trapped in the host instead of being refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all accept native ETH (`msg.value`) as payment and swap it for the exact `feeToken` amount required via Uniswap's `swapETHForExactTokens`. Any leftover ETH from that swap is refunded by the Uniswap router to `address(this)` (the `EvmHost` contract), not to the original transaction sender, so users who send more ETH than strictly required permanently lose the difference into the host's balance.

### Finding Description
In `dispatch(DispatchPost)` [1](#0-0) , `dispatch(DispatchGet)` [2](#0-1) , and `fundRequest` [3](#0-2) , the pattern is identical:

```solidity
if (msg.value > 0) {
    ...
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
```

`swapETHForExactTokens(amountOut, path, to, deadline)` takes an exact output amount (`post.fee`/`get.fee`/`amount`) and an upper bound `msg.value` input; per Uniswap V2 semantics, any unused ETH is refunded to the caller of the router call — here that caller is `EvmHost` itself (since `EvmHost` is the contract invoking the router), not `_msgSender()`/the original user who sent the transaction. There is no code path in `EvmHost` that forwards this leftover ETH back to the user; it simply accrues in the host's native balance. The comment in the `dispatch` docstring, "Will revert if enough native tokens are not provided," documents the underflow case but says nothing about the overflow/refund case, confirming this was not accounted for.

The parallel to the `PhiFactory:claim` finding is direct: the caller's `msg.value` is not validated against the actual amount consumed, and the excess is neither refunded to the caller nor reverted — it is absorbed by the receiving contract's own balance.

### Impact Explanation
Any user who dispatches a POST/GET request or funds a pending request with native ETH and provides any safety margin above the exact swap quote (which is standard practice, since `quote()` is explicitly documented as being for off-chain estimation only and vulnerable to sandwiching/slippage, per `docs/content/developers/evm/messaging/get-requests.mdx`), will have that margin permanently trapped in `EvmHost`. This is a direct, protocol-wide loss of user funds on every native-token dispatch across all EVM deployments of `EvmHost`. The only path to recover this ETH is the privileged `withdraw()` function [4](#0-3) , restricted to `_hostParams.hostManager`, meaning the trapped user funds are effectively converted into protocol-controlled/host-manager-withdrawable revenue rather than returned to their rightful owner.

### Likelihood Explanation
This triggers on essentially every native-ETH dispatch, since a user must supply `msg.value` before the transaction executes and cannot know the exact on-chain Uniswap price at execution time; users are structurally forced to overpay by some margin to avoid reverts from slippage/frontrunning, guaranteeing dust-to-meaningful ETH accumulates in the host on virtually every call. No malicious actor or special preconditions are required — this is a systemic, always-reachable loss for any unprivileged caller of `dispatch`/`fundRequest`.

### Recommendation
After the `swapETHForExactTokens` call, compute the actual ETH consumed (e.g., via the returned `amounts[0]` from the router call, or by comparing `address(this).balance` before/after accounting for other flows) and refund the unused remainder to `_msgSender()`. Alternatively, use `swapExactETHForTokens` with a minimum-out check plus explicit refund logic, or track/emit the leftover per-call and expose a `sweep`/`claimRefund` mechanism keyed to the depositor rather than letting it become indistinguishable host revenue.

### Proof of Concept
1. Deploy `EvmHost` with a configured `uniswapV2` router and `feeToken`.
2. Call `host.dispatch{value: X}(DispatchPost{ fee: F, ... })` where `X` is slightly greater than the exact ETH needed to buy `F` fee tokens (as is required in practice since `quote()` is only an off-chain, sandwichable estimate).
3. Observe that `swapETHForExactTokens` only consumes `< X` ETH; the difference `X - consumed` is refunded by the router to `address(this)` (the `EvmHost` contract).
4. Check `address(host).balance` after the call — it will have increased by `X - consumed`, and no portion of it is attributed to or refundable by the original caller. Repeat and observe this balance grows on every over-provisioned native dispatch, while only the privileged `hostManager` can extract it via `withdraw()`.

### Citations

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
