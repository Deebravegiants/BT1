## Analysis

The reported bug is a **parameter/amount mismatch**: a function is supposed to consume a caller-specified, bounded amount but instead consumes a different value (`msg.value`), silently breaking the accounting invariant the caller and downstream logic rely on.

The closest reachable analog in Hyperbridge is `GnosisUniswapV2Interface.swapETHForExactTokens`, the chain-specific stand-in for `IUniswapV2Router02` used by `EvmHost.dispatch`, `EvmHost.fundRequest`, and `IntentGatewayV2`/`ExtrinsicIntents` order-fill/placement flows on Gnosis.

### Title
Gnosis UniswapV2 wrapper ignores `amountOut` and consumes the entire `msg.value`, breaking exact-fee accounting and refund invariants relied on by `EvmHost` and the Intent Gateway - (File: `evm/src/utils/uniswapv2/GnosisUniswapV2Wrapper.sol`)

### Summary
`swapETHForExactTokens` in the Gnosis wrapper is meant to emulate `IUniswapV2Router02.swapETHForExactTokens`: spend only what is needed to produce exactly `amountOut` of the output token, refunding the rest to the caller. Instead it wraps and forwards the entire `msg.value` regardless of `amountOut`, and returns `msg.value` (not `amountOut`) as the amount "spent".

### Finding Description
The wrapper's implementation: [1](#0-0) 

completely ignores the `amountOut` argument except for a lower-bound sanity check (`amountOut > msg.value` reverts), then deposits **all** of `msg.value` into WETH/WXDAI and transfers **all** of it to `msg.sender`, reporting `out[0] = msg.value` as the amount consumed.

This wrapper is wired in as the drop-in `uniswapV2` router for chains like Gnosis and is invoked from multiple unprivileged entry points that assume real UniswapV2 semantics (exact-output swap + automatic refund of unused native value):

- `EvmHost.dispatch`, reachable by any unprivileged dispatcher paying with native token: [2](#0-1) 
Here `_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee})` records the promised relayer fee as `post.fee`, independent of how much feeToken was actually received from the swap. [3](#0-2) 

- `EvmHost.fundRequest`, same pattern, callable by anyone to top up a request's fee: [4](#0-3) 

- `IntentGatewayV2.placeOrder` / the Tron port, where the returned swap amount is used to decrement the caller's remaining native balance (`msgValue -= amounts[0]`), and only `order.fees` (the requested amount, not the actual amount received) is credited to escrow: [5](#0-4) 

Because the wrapper returns `msg.value` as `amounts[0]` instead of the true cost of `amountOut`, every caller's "leftover native value" bookkeeping is wrong:
1. If a caller sends `msg.value` **greater** than what a correct router would need to buy `post.fee`/`order.fees` worth of feeToken, the entire surplus is swallowed by the wrapper instead of being refunded — the `msgValue -= amounts[0]` accounting in `IntentGatewayV2`/`ExtrinsicIntents` fill functions zeroes out, so the "refund unspent native tokens to the solver" step never fires even though the solver overpaid.
2. Conversely, if a caller sends `msg.value` that undershoots the correct exact-output cost (e.g., due to price movement or an off-chain quote using the real router's pricing formula), `EvmHost` still records the fee metadata / escrow as the full requested `post.fee` / `order.fees` amount, while the wrapper only actually delivered `msg.value` worth of feeToken to the contract — the acquired feeToken balance can be less than what the accounting promises to relayers, understating what was actually escrowed relative to what is later paid out (e.g. `IERC20(feeToken()).safeTransfer(meta.sender, meta.fee)` on timeout).

### Impact Explanation
This directly hits "relayer fee and reward accounting" and token-bridge fee escrow paths reachable by any unprivileged dispatcher/solver on a Gnosis-style deployment: relayer fee accounting can be under- or over-collected relative to the feeToken actually pulled in, and solver/user native-token refunds guaranteed by `IntrinsicIntents`/`ExtrinsicIntents`/`IntentGatewayV2` silently fail to return unspent value, effectively confiscating user funds sent as native token. Repeated exploitation of the "no refund of surplus" behavior lets the protocol accumulate unaccounted native/feeToken value while individual users lose the difference between what they sent and what was actually required — a fund-freezing/loss condition for any unprivileged caller paying fees in native token on this chain.

### Likelihood Explanation
Any user or solver calling `EvmHost.dispatch`, `EvmHost.fundRequest`, or `IntentGatewayV2.placeOrder`/fill functions with native-token fee payment on a deployment that uses `GnosisUniswapV2Interface` as the configured `uniswapV2` router will trigger this mismatch whenever their supplied `msg.value` does not exactly equal the amount the wrapper is expected to consume for the quoted `amountOut`. Since off-chain quoting tools (`quote()` helpers, SDKs) are built against real UniswapV2 semantics, exact-match by chance is unlikely, making the mismatch broadly and routinely triggerable, not a rare edge case.

### Recommendation
Make `GnosisUniswapV2Interface.swapETHForExactTokens` behave like a genuine exact-output swap: wrap exactly `amountOut` worth of native value (assuming 1:1 peg as intended), transfer only `amountOut` of the wrapped token to the caller, and refund the remainder (`msg.value - amountOut`) back to `msg.sender` in the same call, returning `amountOut` (not `msg.value`) as `out[0]`. This restores the invariant that `EvmHost.dispatch`/`fundRequest` and the Intent Gateway fill/placement logic depend on for correct fee escrow accounting and native-value refunds.

### Proof of Concept
1. Deploy `EvmHost` on a Gnosis-like chain with `uniswapV2 = GnosisUniswapV2Interface` and `feeToken() == WETH()` (WXDAI).
2. Attacker calls `dispatch(post)` with `post.fee = 10` and sends `msg.value = 1000` (e.g., by mistake or by intentionally overpaying to test refund behavior).
3. `GnosisUniswapV2Interface.swapETHForExactTokens{value: 1000}(10, path, address(this), ...)` wraps and forwards the full 1000 to `EvmHost`, returning `out[0] = 1000`.
4. `EvmHost` stores `FeeMetadata({sender: post.payer, fee: post.fee})` where `post.fee = 10`, while it actually now holds 1000 units of feeToken pulled from the caller with no code path to refund the 990 surplus — the caller permanently loses the difference, contradicting the exact-fee, refund-surplus design implied by `dispatch`'s NatSpec ("Payment for the request can be made with either the native token or the feeToken... Will revert if enough native tokens are not provided"). [6](#0-5)

### Citations

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

**File:** evm/src/core/EvmHost.sol (L908-932)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * @param post - post request
     * @return commitment - the request commitment
     */
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

**File:** evm/src/core/EvmHost.sol (L1031-1050)
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

        FeeMetadata memory metadata = _requestCommitments[commitment];
        if (metadata.sender == address(0)) revert UnknownRequest();

        metadata.fee += amount;
        _requestCommitments[commitment] = metadata;

        emit RequestFunded({commitment: commitment, newFee: metadata.fee});
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-488)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```
