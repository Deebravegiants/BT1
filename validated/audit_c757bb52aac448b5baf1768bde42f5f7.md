### Title
Native-to-fee-token swaps in `EvmHost.dispatch()` rely on manipulable spot AMM price with no slippage/TWAP protection - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` convert user-supplied native currency into the protocol `feeToken` by calling `IUniswapV2Router02.swapETHForExactTokens` directly against the live Uniswap V2 pool reserves, using `block.timestamp` as the swap deadline (a no-op deadline) and no independent price reference (no TWAP, no oracle, no min/max bound beyond the caller's own `msg.value`). This mirrors the reported class of vulnerability: relying on an instantaneously-manipulable AMM spot price as a pricing oracle inside a single transaction, without any time-weighted or externally-verified reference price.

### Finding Description
In `dispatch(DispatchPost memory post)`: [1](#0-0) 
and identically in `dispatch(DispatchGet memory get)`: [2](#0-1) 

the amount of native currency required to obtain the exact `feeToken` output (`post.fee`/`get.fee`) is computed live by the Uniswap V2 Router from the pool's current reserves at execution time (`getReserves`-based constant-product formula), with `deadline = block.timestamp` — i.e., the deadline check is always satisfied and provides zero protection. There is no minimum/maximum acceptable exchange-rate check, no TWAP consultation, and no comparison against any external reference price before the swap executes and before the resulting `feeToken` is credited into `_requestCommitments[commitment] = FeeMetadata({sender: ..., fee: post.fee})`.

Because a single unprivileged caller can flash-loan-manipulate the reserves of the WETH/`feeToken` Uniswap V2 pool configured in `_hostParams.uniswapV2` (any user can call `dispatch` with `msg.value`), an attacker can, within one atomic transaction:
1. Skew the WETH/feeToken pool reserves so that WETH is temporarily overvalued relative to `feeToken`.
2. Call `dispatch{value: msg.value}(post)` with a large `post.fee`; `swapETHForExactTokens` computes a distorted (low) native-token cost for that large `feeToken` output based on the manipulated reserves, and the swap fills from the pool's real liquidity.
3. Unwind the manipulation (repay flash loan) in the same transaction, having drained real `feeToken` value from the pool's liquidity providers into `EvmHost`'s balance for far less native currency than fair market value.
4. The oversized `post.fee` is now recorded as `FeeMetadata.fee` for the dispatched commitment. If the request subsequently times out (or the relayer never delivers it), `dispatchTimeOut`/`onGetTimeout` fully refunds `meta.fee` in clean, liquid `feeToken` back to `meta.sender`: [3](#0-2) [4](#0-3) 

effectively laundering the AMM-manipulation profit into a legitimate `feeToken` payout from `EvmHost`.

### Impact Explanation
This lets an unprivileged caller (anyone invoking `dispatch`) extract real value from the configured Uniswap V2 pool's liquidity providers by manipulating the same-block spot price the Host uses to price its native-to-feeToken conversion, then recover the manipulated `feeToken` amount as a clean refund via the request-timeout path. This is a concrete theft-of-funds vector reachable from a single dispatched request/message, matching the High severity bar (unbacked/mispriced value extraction via oracle/AMM manipulation) requested in the validation criteria.

### Likelihood Explanation
Any user can call the public, unprivileged `dispatch()` functions with `msg.value`. Manipulating a single AMM pool's reserves within one transaction (via flash loans) is a well-established, low-cost technique, and the code provides no slippage bound (besides the attacker's own chosen `msg.value`) and no TWAP/oracle cross-check, and `deadline = block.timestamp` provides no timing protection at all. The only precondition is that a Uniswap V2 pool with sufficient/attackable liquidity exists for WETH/feeToken on the deployed chain, which is inherent to the design (`_hostParams.uniswapV2` is a required configured dependency for native-fee payments).

### Recommendation
- Do not rely on live Uniswap V2 spot pricing for native→feeToken conversion inside `dispatch`. Use a TWAP-based price or an external oracle (e.g., Chainlink) to bound the acceptable native cost, and/or require callers to pass an explicit `amountInMax`/slippage tolerance rather than implicitly using the whole `msg.value`.
- Replace the meaningless `deadline = block.timestamp` with a caller-supplied deadline to prevent transaction-ordering abuse.
- Consider disallowing same-transaction dispatch immediately after large reserve changes, or route native fee payments through a venue less susceptible to single-block manipulation.

### Proof of Concept
1. Attacker takes a flash loan and swaps a large amount of WETH into the configured WETH/feeToken Uniswap V2 pool, sharply reducing the feeToken reserve relative to WETH (or vice versa depending on desired direction).
2. In the same transaction, attacker calls `EvmHost.dispatch{value: X}(DispatchPost{... fee: largeFeeAmount ...})`. Because `IUniswapV2Router02.swapETHForExactTokens` prices `largeFeeAmount` off the now-skewed reserves, `X` (a small value) suffices to fulfill `amountOut = largeFeeAmount`. [1](#0-0) 
3. Attacker reverses the initial swap to restore the pool and repay the flash loan, keeping the arbitrage profit realized from the pool's liquidity.
4. `FeeMetadata{sender: attacker, fee: largeFeeAmount}` is now stored under the request commitment.
5. Attacker lets the request time out (or it fails to be relayed); calling the timeout handler refunds `largeFeeAmount` in `feeToken` directly to the attacker: [3](#0-2)

### Citations

**File:** evm/src/core/EvmHost.sol (L871-876)
```text

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
```

**File:** evm/src/core/EvmHost.sol (L900-905)
```text

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
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
