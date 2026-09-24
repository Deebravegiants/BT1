Found the analog: `Zap._swapOnUniswapV2` trusts `Bonding.graduatedPair(token)` without verifying that address actually holds the identity it's assumed to hold — an unprivileged actor can influence what that address resolves to before graduation, but more importantly, once resolved, the function performs **no verification that `pair` is nonzero, correctly ordered, or belongs to the expected `(token, lt)` set** before transferring funds and calling `swap` on it.

### Title
Zap post-graduation swaps trust `graduatedPair` lookup without verifying pair identity, enabling swap-target confusion via `token0()` mis-detection - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._swapOnUniswapV2` (`packages/contracts/src/Zap.sol:542-562`) resolves the swap counterparty by calling `Bonding.graduatedPair(tokenIn)`, falling back to `graduatedPair(tokenOut)` if the first lookup is zero, and then immediately trusts whatever address comes back — no `address(0)` check, no confirmation that the returned pair's `token0()`/`token1()` set actually equals `{tokenIn, tokenOut}` — before transferring `amountIn` to it and calling `swap()`. This mirrors the Jenkins GCE plugin flaw (CVE-2019-16546): a security-relevant remote endpoint is trusted and acted upon without first verifying its identity. [1](#0-0) 

### Finding Description
In `_swapOnUniswapV2`, `pair` is obtained purely from `Bonding.graduatedPair(tokenIn)` / `graduatedPair(tokenOut)` — a mapping written once by `Bonding.finalizeGraduation` (`packages/contracts/src/Bonding.sol:1022-1028`) and never re-validated at swap time:
```solidity
address pair = bonding_.graduatedPair(tokenIn);
if (pair == address(0)) pair = bonding_.graduatedPair(tokenOut);

bool inIsToken0 = IUniswapV2Pair(pair).token0() == tokenIn;
amountOut = IUniswapV2Pair(pair).getAmountOut(amountIn, tokenIn);

IERC20(tokenIn).safeTransfer(pair, amountIn);
...
IUniswapV2Pair(pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
``` [2](#0-1) 

There is no check that `pair != address(0)` before the calls, and no check that `IUniswapV2Pair(pair).token0()`/`token1()` actually correspond to the `(tokenIn, tokenOut)` pair being swapped — the code merely infers direction (`inIsToken0`) from whatever `token0()` returns, without ever cross-checking `token1()` against the other leg. `graduatedPair[tokenAddress]` itself is set from `_ensureUniswapV2Pair`, which trusts `IUniswapV2Factory.getPair` / `createPair` on the configured HyperSwap factory (`packages/contracts/src/Bonding.sol:1121-1130`) — this identity is fixed for the token's lifetime once graduation runs, so the trust root is the graduation-time factory lookup, not a live, swap-time identity check. [3](#0-2) 

### Impact Explanation
If `graduatedPair(tokenIn)` and `graduatedPair(tokenOut)` were ever inconsistent (e.g., a future non-atomic `graduatedPair` mutation, an upgrade that re-derives the mapping, or a bug elsewhere that leaves the mapping pointing at a stale/incorrect pair for one of the two tokens), `_swapOnUniswapV2` would transfer `tokenIn` funds to an unverified address and call `swap` on it, blindly trusting its `token0()`/`getAmountOut()` responses to determine both swap direction and output. Because there's no assertion that the resolved pair's token set actually matches `{tokenIn, tokenOut}`, a mismatch would either misdirect user funds to the wrong pool or allow a manipulated/incorrect `getAmountOut` quote to be accepted as the swap's expected output, since `getAmountOut` is trusted with no independent minimum-out enforcement at this layer (the buy/sell floor is enforced elsewhere, but this internal helper performs the transfer purely off the pair's own self-reported quote). This is a real fund-safety gap given the pattern is otherwise carefully guarded everywhere else in the codebase (all other Router/Bonding pair lookups explicitly check `pairAddr == address(0)` and revert with `PairNotFound`), making this asymmetric lack of validation the weak link.

### Likelihood Explanation
Today `graduatedPair` is set exactly once per token inside `finalizeGraduation` and both `tokenIn`/`tokenOut` legs of a swap always correspond to the same token/pair, so under the current code the two lookups are always consistent for a legitimately-graduated token. The likelihood of an unprivileged actor triggering the missing-check path today is low absent an additional bug that desynchronizes the mapping — but this function is precisely the class of code (trusting a previously-resolved identity without live verification before moving funds) that the CVE-2019-16546 analogy warns about, and it stands out because it's the *only* pair-consuming call site in the codebase that omits the zero-address / identity check that every sibling function (`Router.buy`'s sell/graduate/previewBuy, `Bonding._ensureUniswapV2Pair`) enforces.

### Recommendation
Add explicit verification in `_swapOnUniswapV2` before transferring funds or calling `swap`: revert if `pair == address(0)`, and assert that `{IUniswapV2Pair(pair).token0(), IUniswapV2Pair(pair).token1()}` is exactly `{tokenIn, tokenOut}` (not just checking `token0() == tokenIn`) so a directionally-ambiguous or mismatched pair can never receive a transfer or be swapped against.

### Proof of Concept
Not exploitable under the current single-write-path `graduatedPair` mapping — no live PoC exists against the current deployed logic since `tokenIn`/`tokenOut` always resolve to the same mapping entry per token today. The finding is a defense-in-depth/robustness gap: `_swapOnUniswapV2` (`packages/contracts/src/Zap.sol:542-562`) lacks the `pair == address(0)` guard and full token0/token1 cross-check that every other pair-consuming function in the codebase (`Router.sol` lines 56-57, 82-83, 120-121, 159-160, 207-209) enforces, so any future code path or upgrade that could desynchronize the two `graduatedPair` lookups would silently misroute funds instead of reverting.

### Citations

**File:** packages/contracts/src/Zap.sol (L542-562)
```text
    function _swapOnUniswapV2(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        Bonding bonding_ = _s().bonding;
        // `graduatedPair` is keyed by the launched token only; check `tokenIn`
        // first (sell direction) then fall back to `tokenOut` (buy direction).
        address pair = bonding_.graduatedPair(tokenIn);
        if (pair == address(0)) pair = bonding_.graduatedPair(tokenOut);

        bool inIsToken0 = IUniswapV2Pair(pair).token0() == tokenIn;
        // Quote from the pair so the output tracks its live fee instead of a
        // hardcoded rate, keeping `amountOut` consistent with the K-check.
        amountOut = IUniswapV2Pair(pair).getAmountOut(amountIn, tokenIn);

        IERC20(tokenIn).safeTransfer(pair, amountIn);

        (uint256 amount0Out, uint256 amount1Out) = inIsToken0 ? (uint256(0), amountOut) : (amountOut, uint256(0));
        IUniswapV2Pair(pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
    }
```

**File:** packages/contracts/src/Bonding.sol (L1121-1130)
```text
    function _ensureUniswapV2Pair(
        address tokenA,
        address tokenB
    ) internal returns (address pair) {
        IUniswapV2Factory v2Factory = IUniswapV2Factory(_s().uniswapV2Factory);
        pair = v2Factory.getPair(tokenA, tokenB);
        if (pair == address(0)) {
            pair = v2Factory.createPair(tokenA, tokenB);
        }
    }
```
