### Title
`EvmHost.dispatch()`/`fundRequest()` overpay in native token is not refunded to caller — unaccounted ETH lost to the contract - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.fundRequest()` are `payable` and, when `msg.value > 0`, forward the *entire* `msg.value` into a Uniswap V2-style `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` call, but never capture or refund any unspent native token back to the original caller. This mirrors the reported `flash()` class of bug: a payable entrypoint accepts more ETH than the function logic actually consumes/accounts for.

### Finding Description
In `dispatch()`: [1](#0-0) 
the full `msg.value` is passed to the swap router, but only `post.fee` worth of `feeToken()` is requested (`amountOut`), and only `post.fee` is recorded in `_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee})`. The function does not inspect the return value of `swapETHForExactTokens` (an `amounts` array reporting how much ETH was actually spent) nor does it refund the difference to `_msgSender()`.

The identical pattern repeats in `fundRequest()`: [2](#0-1) 

Whether this results in stuck ETH or stuck fee-token depends on which Uniswap wrapper is configured as `_hostParams.uniswapV2`:
- `UniV3UniswapV2Wrapper.swapETHForExactTokens` and `UniV4UniswapV2Wrapper.swapETHForExactTokens` refund unspent ETH to `msg.sender` of the swap call — which is `EvmHost`, not the original transaction sender — via a low-level `call`, e.g. `UniV3UniswapV2Wrapper.sol` lines 143-148 and `UniV4UniswapV2Wrapper.sol` lines 91-96. That refunded ETH lands in `EvmHost`'s balance with no bookkeeping tying it back to the depositor.
- `GnosisUniswapV2Wrapper.swapETHForExactTokens` converts the **entire** `msg.value` to WETH/WXDAI and transfers it all to `EvmHost` regardless of the requested `amountOut`: [3](#0-2) 
so any excess beyond `post.fee`/`amount` becomes unaccounted `feeToken()` balance sitting in `EvmHost`.

By contrast, the codebase's own `IntentGatewayV2.placeOrder()` demonstrates the correct pattern — it captures the `amounts` returned from the same style of swap and refunds the unspent native balance back to `msg.sender`: [4](#0-3) 
`EvmHost.dispatch()`/`fundRequest()` lack this accounting entirely.

### Impact Explanation
Any user (an "unprivileged message dispatcher") calling `dispatch()` or `fundRequest()` with `msg.value` greater than what is strictly required to acquire `post.fee`/`amount` of `feeToken()` permanently loses the excess — it is neither refunded to them nor credited to their request's fee metadata. Because fee quoting off-chain can be imprecise (slippage, price movement between quote and execution), users are practically likely to send slightly more ETH than the exact required amount, and that surplus is silently absorbed by the contract with no path to reclaim it. This is a direct, protocol-wide loss-of-funds bug for any caller who dispatches a POST/GET request or funds a pending request using native token payment, not merely an edge case.

### Likelihood Explanation
Likelihood is high: `dispatch()` is the primary, unprivileged entrypoint used by all IsmpModule callers/apps (including `HyperFungibleToken.send`, `WrappedHyperFungibleToken.send`, etc.) paying in native token, so the payable-overpayment condition is triggered on essentially every native-fee dispatch where the caller's supplied `msg.value` doesn't exactly match the swap's `amountIn`. Given real-world gas/price quoting slippage, exact-match transactions are the exception rather than the rule.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2.placeOrder()`: capture the `amounts` (or `amountIn` spent) returned by `swapETHForExactTokens`, and if `msg.value > amounts[0]`, refund `msg.value - amounts[0]` back to `_msgSender()` via a low-level call in both `dispatch()` and `fundRequest()`. Alternatively, require exact-value dispatch and revert on any leftover balance detected after the swap, rather than silently retaining it.

### Proof of Concept
1. Caller invokes `EvmHost.dispatch{value: 1 ether}(post)` where `post.fee` only requires `0.5 ether` worth of native token to acquire the needed `feeToken()` amount (per current pool price).
2. Inside `dispatch()`, `swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)` executes; depending on the configured wrapper:
   - `UniV3/V4UniswapV2Wrapper`: spends ~0.5 ether, refunds ~0.5 ether back to `EvmHost` (the caller of the swap), which `dispatch()` never forwards to the user.
   - `GnosisUniswapV2Wrapper`: converts the full 1 ether to WETH/WXDAI and sends all of it to `EvmHost`, while only `post.fee` (0.5 ether equivalent) is tracked in `FeeMetadata`.
3. `_requestCommitments[commitment].fee` records only `post.fee`; the extra ~0.5 ether (as native ETH or as feeToken) remains stranded in `EvmHost` with no function to claim or refund it to the original caller.
4. Repeating this for every dispatch call accumulates unaccounted, effectively lost user funds inside `EvmHost`. [1](#0-0) [2](#0-1)

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
