### Title
Excess native token sent to `EvmHost.dispatch()` for fee-token swap is stranded in the host contract instead of being refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` accept an arbitrary `msg.value` and forward the entire amount to a Uniswap-V2-style router's `swapETHForExactTokens` to buy exactly `post.fee`/`get.fee` worth of fee token. The underlying router protocol (standard Uniswap V2 Router02, and the project's own wrapper implementations) refunds any *unspent* ETH to `msg.sender` of that swap call — but the swap is called by `EvmHost` itself, not by the original transaction sender. `EvmHost` never captures or forwards this dust refund back to `_msgSender()`, so any excess native token sent above the exact fee requirement becomes permanently stuck in the `EvmHost` contract's balance.

### Finding Description
`EvmHost.dispatch(DispatchPost)`: [1](#0-0) 

and `EvmHost.dispatch(DispatchGet)`: [2](#0-1) 

both do:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
```
The entire `msg.value` is forwarded, but only `post.fee`/`get.fee` worth of tokens is required. The canonical Uniswap V2 router's `swapETHForExactTokens` implementation computes the exact input needed and refunds the dust ETH via `TransferHelper.safeTransferETH(msg.sender, msg.value - amounts[0])` — where `msg.sender`, from the router's perspective, is `EvmHost`, since `EvmHost` is the direct caller of the router. `EvmHost.dispatch()` discards the return value of `swapETHForExactTokens` and has no logic to relay that refunded ETH back to `_msgSender()` (the account that actually paid the excess).

This is confirmed by the repository's own custom router-wrapper implementations, which explicitly refund the caller of the wrapper (i.e. `EvmHost`) rather than the original user:
- `UniV3UniswapV2Wrapper.swapETHForExactTokens` refunds unspent ETH to `msg.sender`: [3](#0-2) 
- `UniV4UniswapV2Wrapper.swapETHForExactTokens` likewise refunds `msg.sender`: [4](#0-3) 
- `GnosisUniswapV2Wrapper.swapETHForExactTokens` is even more aggressive: it accepts any `msg.value >= amountOut` and forwards the *entire* `msg.value` (not just the required fee) as wrapped tokens to `msg.sender` (`EvmHost`), not the amount actually needed: [5](#0-4) 

In every case, "`msg.sender`" as seen by the router/wrapper is `EvmHost`, because `EvmHost` is the contract making the call — not the original dispatcher (app or EOA) that invoked `dispatch()`. `EvmHost` has no code path that forwards this reclaimed value (native ETH or extra fee-token) back to `_msgSender()`. Unlike the `IntentGatewayV2`/`ExtrinsicIntents`/`IntrinsicIntents` contracts in the same codebase — which correctly track `msgValue` and explicitly refund any unspent native token to the caller after swaps and fills (see e.g. `IntentGatewayV2.sol` lines 375-397, `ExtrinsicIntents.sol` lines 203-217, `IntrinsicIntents.sol` lines 139-142) — `EvmHost.dispatch()` contains no such accounting or refund step.

This is the exact bug class from the report: a contract accepts `msg.value` in excess of the amount actually required to satisfy a fee, and the surplus is not returned to the payer.

### Impact Explanation
Any application or user dispatching a POST/GET request through `EvmHost.dispatch()` and paying in native token (the documented/expected UX per `docs/content/developers/evm/messaging/post-requests.mdx`, where callers pass `msg.value` and let the host "swap native -> feeToken") will permanently lose any ETH sent above the exact fee-swap requirement. In practice, callers frequently over-provision `msg.value` (since the exact Uniswap price at execution time is not known precisely ahead of the transaction, and slippage/price movement between quote and execution is expected), so overpayment is a normal and expected occurrence, not an edge case. The lost funds accumulate in the `EvmHost` contract with no mechanism visible in `EvmHost.sol` for the original payer to reclaim them. This is a direct, permanent loss of user funds on every native-token dispatch that isn't perfectly metered — reachable by any unprivileged dispatcher of a POST/GET request (apps built on `HyperApp`, `HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken`, `IntentGatewayV2`'s cross-chain dispatch path, etc., as well as direct EOA callers).

### Likelihood Explanation
High. This triggers on ordinary usage whenever a caller sends `msg.value` that doesn't exactly match the fee-token amount required by the current AMM price — which is the normal case for any client that adds a safety buffer to `msg.value` to avoid reverts from price movement (as the documentation for other contracts in this same repo explicitly recommends, e.g. "Send 5 ETH for a fee swap that should cost much less" pattern used and correctly refunded elsewhere in `IntentGatewayV2`). No malicious actor is needed; ordinary correct usage triggers fund loss.

### Recommendation
In both `dispatch(DispatchPost)` and `dispatch(DispatchGet)` in `EvmHost.sol`, capture the router's return value (`amounts[0]`, the actual native amount spent) and refund `msg.value - amounts[0]` back to `_msgSender()`, mirroring the pattern already implemented correctly in `IntentGatewayV2.sol`/`ExtrinsicIntents.sol`/`IntrinsicIntents.sol`. Additionally, audit the `GnosisUniswapV2Wrapper` to ensure it only mints/forwards the exact `amountOut` needed rather than the full `msg.value`.

### Proof of Concept
1. Configure `_hostParams.uniswapV2` to a standard Uniswap V2 Router (or one of the project's wrapper contracts).
2. An app (or EOA) calls `EvmHost.dispatch(DispatchPost)` (or `DispatchGet`) with `post.fee = X` fee-token units required, but sends `msg.value` sized to comfortably cover `X` plus slippage buffer (e.g., 2x the expected ETH cost), a normal client practice.
3. Inside `dispatch()`, `swapETHForExactTokens{value: msg.value}(post.fee, ...)` executes; the router buys exactly `X` fee tokens and refunds the unspent ETH to `msg.sender`, which resolves to `EvmHost`'s own address (since `EvmHost` is the caller), not the original transaction sender.
4. `dispatch()` returns normally; the request commitment is created successfully.
5. Check `address(EvmHost).balance` before/after: the refunded dust ETH remains in `EvmHost`, while the original caller's wallet balance decreased by the full `msg.value` sent (not just the ETH actually needed for the fee swap) — with no function on `EvmHost` visible to reclaim it back to the caller.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L143-149)
```text
        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L91-96)
```text
        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
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
