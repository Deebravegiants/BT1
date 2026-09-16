### Title
Silent uint256→uint128 truncation in `UniV4UniswapV2Wrapper` desyncs `EvmHost` fee accounting from actual swapped fee-token amount - (File: evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol)

### Summary
`EvmHost.dispatch(DispatchPost)` lets any caller pay the relayer fee in native ETH, which is converted to fee tokens via a configurable Uniswap V2-style router (`_hostParams.uniswapV2`). One of the supported router implementations, `UniV4UniswapV2Wrapper`, narrows the caller-supplied `uint256 amountOut`/`amountIn` fee values down to `uint128` before forwarding them to the Uniswap V4 Universal Router. Solidity's explicit narrowing casts do not revert on overflow — they truncate silently — so a `post.fee` larger than `type(uint128).max` produces a swap for a drastically different (wrapped-around) token amount while `EvmHost` still records the full, untruncated `post.fee` in `_requestCommitments[commitment]`.

### Finding Description
`EvmHost.dispatch(DispatchPost)` accepts `post.fee` as an arbitrary `uint256` from any caller: [1](#0-0) 

When native ETH is supplied, it calls the configured router's `swapETHForExactTokens(post.fee, path, address(this), block.timestamp)` and then unconditionally stores `FeeMetadata({sender: post.payer, fee: post.fee})` keyed by the request commitment — using the original, full `post.fee` value, not whatever the router actually delivered.

If `_hostParams.uniswapV2` is set to `UniV4UniswapV2Wrapper`, the wrapper's `swapETHForExactTokens` and `swapExactTokensForETH` narrow the `uint256` amount to `uint128` before encoding it into the Uniswap V4 swap parameters: [2](#0-1) [3](#0-2) 

Because `uint128(amountOut)` truncates rather than reverts, a `post.fee` value above `type(uint128).max` (`≈3.4e38`) is silently reduced modulo `2^128` before being used as the actual swap `amountOut`. The wrapper then executes the swap for this truncated (much smaller, attacker-chosen) amount and refunds any unused ETH back to `msg.sender` — so the attacker only ever pays for the truncated amount of fee tokens, not the value recorded on-chain.

Meanwhile, back in `EvmHost.dispatch`, `_requestCommitments[commitment].fee` is set to the original, full (non-truncated) `post.fee`. This creates a permanent desync: the protocol's fee-accounting ledger records an inflated fee amount that was never actually backed by real fee-token liquidity swapped in. This is the same root-cause pattern as the reported GPToke issue: a `uint256` value the caller fully controls is unconditionally narrowed to a smaller type without any bounds check, and the truncated value diverges from the un-truncated value used elsewhere in accounting.

### Impact Explanation
`meta.fee` (the untruncated, inflated value) is later paid out of `EvmHost`'s pooled fee-token balance — e.g. on timeout it is refunded to `meta.sender` via `feeToken().safeTransfer(...)`: [4](#0-3) 

and on successful relay, the same fee-token balance is used to pay relayers. Since `EvmHost` holds one shared `feeToken()` balance across all dispatches, an attacker can dispatch a request with an inflated `post.fee` (paying only for the truncated, tiny swapped amount), and later claim (via timeout refund or relayer payout) the full un-truncated fee amount from the shared pool — funded by fee tokens legitimately deposited by other users' dispatches. This is a concrete theft-of-funds vector against the shared fee-token treasury of `EvmHost`, reachable by any unprivileged caller of `dispatch()`.

### Likelihood Explanation
Likelihood is constrained by:
- The vulnerability only manifests when `_hostParams.uniswapV2` is configured to point at `UniV4UniswapV2Wrapper` (one of several router-wrapper implementations available in the repo — `GnosisUniswapV2Wrapper` and `UniV3UniswapV2Wrapper` were not verified for the same truncation pattern in this pass).
- `dispatch(DispatchPost)` is a standard, unprivileged, externally reachable entry point (any app or EOA can call it with `msg.value`), and `post.fee` is fully attacker-controlled, so triggering the truncation only requires supplying a `fee` value above `2^128 - 1`.
- I was not able to fully trace, within the remaining budget, the exact downstream code path that pays out `meta.fee` on successful delivery (only the timeout-refund path was directly confirmed), so the precise size/timing of the exploitable withdrawal is not fully verified.

### Recommendation
In `EvmHost.dispatch`, either (a) revert if `post.fee > type(uint128).max` before invoking the router, or (b) capture the actual amount consumed/received from the swap and use that value (not the caller-supplied `post.fee`) when populating `FeeMetadata`. Additionally, `UniV4UniswapV2Wrapper.swapETHForExactTokens`/`swapExactTokensForETH` should use `SafeCast.toUint128()` (or equivalent explicit bounds check) instead of a bare `uint128(...)` cast, so an out-of-range amount reverts instead of silently wrapping.

### Proof of Concept
1. Configure/observe an `EvmHost` deployment whose `_hostParams.uniswapV2` is set to a `UniV4UniswapV2Wrapper` instance (this is an admin-controlled runtime parameter, not attacker-controlled, but is a supported production configuration for the router).
2. Attacker calls `EvmHost.dispatch{value: v}(DispatchPost{ dest, to, body, timeout, fee: F, payer })` where `F = 2**128 + X` for some small `X`, and `v` is only large enough to cover swapping for `X` fee tokens (not `F`).
3. Inside `dispatch`, `swapETHForExactTokens{value: v}(F, path, address(this), block.timestamp)` is called on the wrapper.
4. Inside the wrapper, `uint128(amountOut)` truncates `F` down to `X`; the swap executes for `X` fee tokens using `v` ETH; any leftover ETH is refunded to the attacker.
5. Back in `dispatch`, `_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: F})` — the ledger now shows the request is entitled to `F` fee tokens, though only `X` were actually acquired.
6. On timeout (or successful relay payout, not independently confirmed here), the contract will attempt to pay out `F` fee tokens from its pooled `feeToken()` balance — funded in part by other users' dispatch fees — realizing a shortfall/theft of `F - X` fee tokens from the shared pool.

### Citations

**File:** evm/src/core/EvmHost.sol (L895-906)
```text
        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/EvmHost.sol (L921-948)
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

        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L66-76)
```text
    function swapETHForExactTokens(uint256 amountOut, address[] calldata path, address recipient, uint256 deadline)
        external
        payable
        returns (uint256[] memory amounts)
    {
        PoolKey memory poolKey = _createPoolKey(path[1]);

        bytes[] memory params = new bytes[](3);
        params[0] = abi.encode(poolKey, true, uint128(amountOut), uint128(msg.value), bytes(""));
        params[1] = abi.encode(poolKey.currency0, uint256(0), false);
        params[2] = abi.encode(poolKey.currency1, recipient, amountOut);
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L103-121)
```text
    function swapExactTokensForETH(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts) {
        address token = path[0];
        PoolKey memory poolKey = _createPoolKey(token);

        // Stage the tokens on the router so SETTLE can pay them from its own balance.
        IERC20(token).safeTransferFrom(msg.sender, address(this), amountIn);
        IERC20(token).safeTransfer(_params.universalRouter, amountIn);

        bytes[] memory params = new bytes[](3);
        // token (currency1) -> ETH (currency0), so zeroForOne is false.
        params[0] = abi.encode(poolKey, false, uint128(amountIn), uint128(amountOutMin), bytes(""));
        params[1] = abi.encode(poolKey.currency1, uint256(0), false);
        params[2] = abi.encode(poolKey.currency0, to, uint256(0));
```
