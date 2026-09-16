### Title
Excess native token payment is fully swapped and permanently trapped in EvmHost with no refund path - (File: evm/src/utils/uniswapv2/GnosisUniswapV2Wrapper.sol / evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch()` (and `fundRequest()`) let a caller pay the dispatch fee in native token by forwarding `msg.value` to a Uniswap-V2-style router's `swapETHForExactTokens`, expecting the router to consume only the exact `post.fee` amount and refund any excess ETH to the caller. On Gnosis Chain, the router is replaced with `GnosisUniswapV2Wrapper`, whose `swapETHForExactTokens` implementation ignores the requested `amountOut` beyond a minimum check and converts the *entire* `msg.value` into `feeToken`, sending it all to `EvmHost`. Because `EvmHost` only records `post.fee` in the request's `FeeMetadata`, any overpayment is silently absorbed by the contract with no accounting, no refund, and no way for the user to reclaim it — the exact same fund-locking bug class as the reported Allo.sol issue.

### Finding Description
`EvmHost.dispatch(DispatchPost)` pays the relayer fee like this: [1](#0-0) 

The developer's intent (documented in the function's NatSpec) is that "payment for the request can be made with either the native token or the feeToken... it will perform a swap under the hood... will revert if enough native tokens are not provided," implying only the exact fee amount should be consumed and any surplus should not be lost.

On chains configured to use `GnosisUniswapV2Wrapper` as the `uniswapV2` router (set in `HostParams.uniswapV2`), the swap function is: [2](#0-1) 

This function only checks `amountOut > msg.value` (i.e. that the user sent *at least* the fee), but then deposits the **entire** `msg.value` into WETH and transfers the **entire** `msg.value` worth of `feeToken` to `msg.sender` — which, from the wrapper's perspective, is `EvmHost` itself (the caller of the swap). The `amountOut`/`post.fee` parameter is never used to bound how much is actually consumed; unlike a genuine Uniswap V2 router, there is no ETH refund path at all.

Back in `EvmHost.dispatch()`, only `post.fee` is recorded against the request: [3](#0-2) 

So if a user calls `dispatch{value: X}(post)` with `X > post.fee` (e.g. because they estimated fees imprecisely, or padded for safety as the docs even suggest doing off-chain), the wrapper converts all `X` into `feeToken` and gives it to `EvmHost`, but the commitment only tracks `post.fee`. The difference `X - post.fee` (in feeToken terms) becomes an untracked balance sitting in `EvmHost` — it is never refunded to the payer, never paid to the relayer (who only receives `meta.fee`), and there is no admin/withdraw function shown in `EvmHost.sol` that sweeps this specific surplus back to the original payer. The same applies to `fundRequest()`, which calls the same wrapper.

This is functionally identical to the Allo.sol root cause: the contract accepts more native value than it actually needs for a fee, deducts only the intended amount, and the remainder becomes permanently stuck with no return mechanism.

### Impact Explanation
Any user of `dispatch()`/`fundRequest()` on the Gnosis-configured `EvmHost` who sends more native token than the exact fee required (a very likely occurrence, since fee estimation is explicitly recommended to be done off-chain and padded, per the SDK docs) will have their full `msg.value` irreversibly converted and retained by the protocol, not just the intended fee. This is a direct, permanent loss of user funds with no recovery path, satisfying "concrete theft or permanent freezing of funds."

### Likelihood Explanation
High likelihood: this triggers on every native-token dispatch/fundRequest call where `msg.value` exceeds the exact `post.fee`/`amount`, which is the normal/expected pattern for slippage-padded client-side fee estimates (as documented in the SDK usage guides). No privileged role or attacker action is needed — a single ordinary user transaction on the affected chain(s) causes the loss.

### Recommendation
Fix `GnosisUniswapV2Wrapper.swapETHForExactTokens` to only consume `amountOut` worth of ETH, mint/wrap and transfer exactly `amountOut` of `feeToken`, and refund `msg.value - amountOut` back to the true originating caller. More robustly, `EvmHost.dispatch`/`fundRequest` should track the balance before/after the swap call and refund any leftover native ETH (or resulting excess feeToken) to `_msgSender()`/`post.payer`, mirroring recommendation #2 in the referenced report, rather than relying on router-specific refund semantics that this wrapper does not implement.

### Proof of Concept
1. Configure `EvmHost` (on a Gnosis-style deployment) with `uniswapV2 = GnosisUniswapV2Wrapper`.
2. Call `EvmHost.dispatch{value: 5 ether}(post)` where `post.fee = 1 ether`.
3. Inside `dispatch`, `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: 5 ether}(1 ether, path, address(this), ...)` is invoked [4](#0-3) .
4. `GnosisUniswapV2Wrapper.swapETHForExactTokens` only checks `1 ether > 5 ether` (false, passes), then wraps and transfers the full 5 ether worth of feeToken to `EvmHost` [5](#0-4) .
5. `_requestCommitments[commitment]` only stores `fee: 1 ether` [6](#0-5) .
6. The extra 4 ether worth of feeToken remains in `EvmHost` with no reference anywhere in state, unrecoverable by the user.

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

**File:** evm/src/core/EvmHost.sol (L946-948)
```text
        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```

**File:** evm/src/utils/uniswapv2/GnosisUniswapV2Wrapper.sol (L39-54)
```text
    function swapETHForExactTokens(uint256 amountOut, address[] calldata, address, uint256)
        external
        payable
        returns (uint256[] memory)
    {
        if (amountOut > msg.value) revert MsgValueLessThanExactAmount();

        (bool sent,) = WETH().call{value: msg.value}("");
        if (!sent) revert DepositFailed();

        IERC20(WETH()).safeTransfer(msg.sender, msg.value);

        uint256[] memory out = new uint256[](1);
        out[0] = msg.value;
        return out;
    }
```
