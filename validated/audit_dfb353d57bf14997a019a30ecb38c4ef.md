### Title
`Bonding._seedRebalancing`'s zero-swap fallback lets a large, ratio-matched HyperSwap pre-seed hijack graduation liquidity - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._seedRebalancing` assumes that whenever `_pairRebalance` fails to find a non-zero rebalancing swap, the pre-existing pool reserves must be "negligible" and therefore safe to overpower with a raw `pair.mint()` via `_seedDirectMint`. That assumption is not actually enforced: `_pairRebalance` returns `false` whenever the *computed swap amount* rounds to zero, which can happen even when the pre-seeded reserves are large, as long as an attacker seeds the HyperSwap V2 TOKEN/LT pair at (or extremely close to) the curve-close ratio. In that case `_seedDirectMint` calls `IUniswapV2Pair.mint()` against a pool whose `totalSupply()` is non-zero, so Uniswap V2's own `min(amount0*supply/reserve0, amount1*supply/reserve1)` formula governs — not the "cached ratio" the natspec claims. Because the attacker also owns 100% of the pre-existing LP supply (self-minted, unlocked), any one-sided donation from the mismatched deposit inflates the redeemable value of the attacker's own LP tokens.

### Finding Description
`_seedRebalancing` only screens out pre-seeds that are tiny relative to `tokensForLP`/`ltFromPair` via the `DIRECT_MINT_PRESEED_BPS` (1 bps) band check: [1](#0-0) 

Anything above that band goes through the "rebalance" path, computing a swap via `_noFeeSwapInput` and executing it directly against the pair: [2](#0-1) 

`_noFeeSwapInput` can legitimately return `0` (or yield an `expectedOut` of `0`) purely because the *pre-seeded ratio is already close to the target ratio* — this is a function of ratio proximity and integer truncation, not of absolute reserve size: [3](#0-2) 

When that happens, `_seedRebalancing` falls back to `_seedDirectMint` — the exact same function used for the "empty pool" happy path — but now against a pool with non-zero `totalSupply()`: [4](#0-3) 

The natspec explicitly (and incorrectly) asserts this fallback is safe because "the reserves are then negligible against this graduation's inventory": [5](#0-4) 

But nothing in the code enforces that claim for the `_pairRebalance`-returns-`false` path — only the earlier `DIRECT_MINT_PRESEED_BPS` branch checks reserve size, and that check is bypassed once reserves exceed the 1 bps band. An attacker can pre-seed the pair with reserves comparable in magnitude to (or larger than) `tokensForLP`/`ltFromPair`, set at (almost) the exact ratio the curve will close at (which is publicly computable from `Bonding.previewLtUntilGraduation` and `IPair.getReserves()` before triggering graduation), so that the required corrective swap rounds to zero. `_seedDirectMint` then transfers the full `tokensForLP`/`ltFromPair` into the pool and calls `pair.mint(lpLock)`, which — against a non-zero-supply pool — mints LP based on `min(amount0*supply/reserve0, amount1*supply/reserve1)`, donating the excess side into the pool's reserves. Since the attacker is the pool's sole pre-existing LP holder (self-minted via a direct, permissionless `pair.mint(attacker)` call on the pre-created HyperSwap pair), the attacker can then `burn` their LP and redeem a disproportionate share of the donated assets — effectively stealing curve-raised LT and/or the 250M graduation tokens that should have backed the protocol-locked LP.

### Impact Explanation
This lets an attacker capture assets intended for the permanently locked graduation LP (`LPLock.recordLock`), i.e., theft of curve-raised LT and/or launch tokens that belong to the protocol/community LP. It also results in the LP being seeded at a ratio that donates value to the attacker rather than opening at the curve-close price, an explicitly in-scope impact.

### Likelihood Explanation
The attack requires only unprivileged, permissionless actions reachable by any address: pre-creating/seeding the HyperSwap V2 TOKEN/LT pair via `IUniswapV2Factory.createPair` + a direct `pair.mint(attacker)` call, and triggering graduation via a curve buy or `Bonding.triggerGraduation`. The attacker can read all state needed (curve reserves, `previewLtUntilGraduation`) ahead of time to craft a ratio-matched pre-seed of the size needed to force `_pairRebalance`'s zero-swap fallback. This requires precise sizing/rounding engineering but no privileged access, and the code path is explicitly a "cold path" the contract itself documents as reachable ("~1% of graduations hit this branch").

### Recommendation
Do not treat `_pairRebalance` returning `false` as proof that reserves are negligible. Before falling back to `_seedDirectMint` on a non-empty pool, explicitly re-check that `reserveToken`/`reserveLT` are within the same `DIRECT_MINT_PRESEED_BPS` band used at the top of `_seedRebalancing` (or some other reserve-size-based bound), and if not, use a router-mediated balanced deposit (`addLiquidity` with real slippage protection) instead of a raw `pair.mint()` that inherits V2's ratio-donation formula.

### Proof of Concept
1. Attacker permissionlessly creates the HyperSwap V2 TOKEN/LT pair for a target token via `IUniswapV2Factory.createPair(token, lt)` (or it already exists) before graduation.
2. Attacker reads the token's curve state (`Bonding.previewLtUntilGraduation`, `IPair.getReserves()`) to compute the ratio the curve will close at, i.e., the eventual `tokensForLP / ltFromPair`.
3. Attacker acquires TOKEN and LT (via curve buy / direct LT mint) and transfers both into the HyperSwap pair at a size comparable to (or larger than) the anticipated `tokensForLP`/`ltFromPair`, matched as closely as possible to the computed target ratio, then calls `pair.mint(attacker)` to receive 100% of the pool's LP supply.
4. Attacker triggers graduation (via a curve buy crossing the threshold, or `Bonding.triggerGraduation`).
5. `finalizeGraduation` → `_seedUniswapV2Direct` → `_seedRebalancing` computes the rebalancing swap; because the pre-seed ratio is already near-target, `_pairRebalance` returns `false` (swap or output rounds to zero).
6. `_seedDirectMint` is invoked against the non-empty pool, calling `pair.mint(lpLock)` which applies Uniswap V2's `min()` formula, donating the mismatched side of the deposit into pool reserves controlled by the attacker's pre-existing LP share.
7. Attacker calls `pair.burn` on their LP tokens to redeem the disproportionate share of the donated TOKEN/LT, extracting value that should have backed the locked graduation LP.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1168-1176)
```text
    ///           When the seed is small enough that the fee-charging swap
    ///           quote rounds to zero, no swap can move the ratio — but the
    ///           reserves are then negligible against this graduation's
    ///           inventory, so we fall back to the regime-1 direct mint
    ///           (`_seedDirectMint`) and open at the cached ratio anyway.
    ///           The captured LP share is bounded by
    ///           `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`,
    ///           which vanishes for any seed that small.
    ///
```

**File:** packages/contracts/src/Bonding.sol (L1245-1259)
```text
    function _seedDirectMint(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair
    ) internal returns (uint256 liquidity) {
        IERC20(tokenAddress).safeTransfer(pair, tokensForLP);
        IERC20(lt).safeTransfer(pair, ltFromPair);
        liquidity = IUniswapV2Pair(pair).mint(_s().lpLock);
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1291-1302)
```text
        // Below the band on BOTH sides, overpower the pre-seed with a direct
        // mint at the cached ratio: the rebalance swap is too coarse to reach
        // the ratio against such small reserves, and the pre-existing LP's
        // claim on the deposit stays bounded by `DIRECT_MINT_PRESEED_BPS`. A
        // side that is large relative to its LP target still takes the
        // rebalance path so it isn't donated under the empty-mint `min()`.
        if (
            reserveToken * BPS_DENOM <= tokensForLP * DIRECT_MINT_PRESEED_BPS
                && reserveLT * BPS_DENOM <= ltFromPair * DIRECT_MINT_PRESEED_BPS
        ) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }
```

**File:** packages/contracts/src/Bonding.sol (L1414-1429)
```text
    function _pairRebalance(
        RebalanceParams memory p
    ) internal returns (bool) {
        uint256 s = _noFeeSwapInput(p.reserveIn, p.reserveOut, p.targetN, p.targetD, p.maxSwap);
        if (s == 0) return false;

        // Quote from the pair so the output tracks its live fee; a value
        // derived from a stale fee rate would trip the pair's K-check.
        uint256 expectedOut = IUniswapV2Pair(p.pair).getAmountOut(s, p.tokenIn);
        if (expectedOut == 0) return false;

        IERC20(p.tokenIn).safeTransfer(p.pair, s);
        (uint256 amount0Out, uint256 amount1Out) = p.tokenInIs0 ? (uint256(0), expectedOut) : (expectedOut, uint256(0));
        IUniswapV2Pair(p.pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
        return true;
    }
```

**File:** packages/contracts/src/Bonding.sol (L1507-1522)
```text
    function _noFeeSwapInput(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 targetN,
        uint256 targetD,
        uint256 maxSwap
    ) internal pure returns (uint256) {
        if (reserveIn == 0 || reserveOut == 0 || targetN == 0 || targetD == 0 || maxSwap == 0) {
            return 0;
        }
        uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
        uint256 newIn = Math.sqrt(product);
        if (newIn <= reserveIn) return 0;
        uint256 s = newIn - reserveIn;
        return s > maxSwap ? maxSwap : s;
    }
```
