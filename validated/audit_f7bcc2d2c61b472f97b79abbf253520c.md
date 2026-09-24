### Title
`finalizeGraduation` can be permanently bricked by an arithmetic overflow in the hostile-pre-seed rebalance math - ([File: packages/contracts/src/Bonding.sol])

### Summary
An attacker who pre-seeds the HyperSwap V2 `TOKEN/LT` pair with an extreme, asymmetric mint before phase-2 graduation runs can force `Math.mulDiv` inside `Bonding._noFeeSwapInput` to overflow uint256, which reverts every call to `finalizeGraduation` for that token. Since `Lifecycle.Graduating` has no other exit path, this permanently freezes the token's curve-raised LT and the 250M tokens parked on `Bonding` for that graduation.

### Finding Description
`finalizeGraduation` is permissionless and, when the V2 pair already has non-zero `totalSupply()` (a "mint pre-seed", Regime 3), routes through `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`: [1](#0-0) 

`_noFeeSwapInput` computes the no-fee swap size needed to rebalance the pool toward the curve-close ratio: [2](#0-1) 

The natspec itself acknowledges the risk but dismisses it as bounded: [3](#0-2) 

`Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` first multiplies the pair's live `uint112` reserves (`reserveIn`, `reserveOut`, each up to `~2^112`), giving a product up to `~2^224`. It is then scaled by `targetN` (either `ltFromPair` or `tokensForLP`, bounded at launch to `~2^111` via `ExchangeRateTooLow`'s `virtualLtReserve ≤ uint112.max/4` check) and divided by `targetD`. `targetD` is the *other* pinned graduation quantity (`tokensForLP` or `ltFromPair`), which is **not** bounded away from small values — the parabola `tokensForLP(sold) = sold·(S−sold)/S` can be arbitrarily small near either end of the curve, and `ltFromPair` can be small for a token that graduates almost entirely off LT appreciation with little raised LT. When `targetD` is small while `reserveIn`/`reserveOut` are attacker-inflated toward their `uint112` ceiling via a large mint pre-seed of the V2 pair, the intermediate `mulDiv` result exceeds `2^256` and OpenZeppelin's `Math.mulDiv` reverts (`MathOverflowedMulDiv`) rather than truncating.

Because the attacker's pre-seed sits both above the `DIRECT_MINT_PRESEED_BPS` dust band (so the direct-mint fallback is skipped) and drives the overflow, every call to `finalizeGraduation(tokenAddress)` — by anyone, at any time — hits this revert inside `_pairRebalance`. There is no retry-with-different-parameters path: `finalizeGraduation` always recomputes the same cached `PendingGraduation` values and the same pool reserves, so the revert is deterministic and permanent.

### Impact Explanation
`Lifecycle.Graduating` is a one-way state with a single exit function, `finalizeGraduation`. If that function can never succeed:
- The token's entire curve-raised LT (`ltFromPair`, already pulled out of the curve `Pair` via `Router.graduate` inside `_prepareGraduationLiquidity`, sitting in `Bonding`) is permanently frozen.
- The 250M `LP_RESERVE`-bound tokens cached as `tokensForLP` and held/approved on `Bonding` are permanently frozen (never minted into any LP, never burned).
- `LPLock.recordLock` never fires, so the token can never reach `Lifecycle.Graduated`; trading and LP-lock never resume.

This is a direct, permanent freezing of trader/creator funds and matches the CVE's "attacker-crafted input triggers an unhandled failure in the target's core processing loop, permanently disabling normal service" bug class, mapped onto alt.fun's two-phase graduation and V2-pool-seeding logic.

### Likelihood Explanation
The attack requires only:
1. Buying/holding the launched token in sufficient quantity on the curve prior to graduation (bounded by total supply, ~1e27 wei, well within economic reach for a determined attacker targeting one launch), and
2. Holding/minting a correspondingly large amount of the paired LT to seed the V2 pair with an extreme ratio, then calling `pair.mint` directly (a permissionless HyperSwap V2 primitive) before any `finalizeGraduation` call lands.

Both actions are reachable by any unprivileged address using only public functions (`Zap.buy`/curve `buy`, direct `IUniswapV2Pair.mint`). The main cost is acquiring enough LT capital to push `reserveIn`/`reserveOut` toward the danger zone, and the trigger condition (`targetD` small) further depends on where on the parabola/graduation path the specific token closes — so it is not universally exploitable on every launch, but is a concrete, reachable griefing/exploit path against targeted, moderately-sized launches (e.g., tokens closing near either extreme of `tokensForLP(sold)`).

### Recommendation
- Bound the rebalance computation so it cannot revert on adversarial inputs: clamp/scale `reserveIn`, `reserveOut`, `targetN`, `targetD` into a safe range before calling `Math.mulDiv`, or compute the ratio comparison using scaled/normalized values (e.g. divide down common factors, or use a fixed-point representation with a fixed bit-width) instead of raw products.
- Wrap the `_pairRebalance`/`_noFeeSwapInput` call in a `try/catch` (or precompute overflow safety) inside `_seedRebalancing`, falling back to `_seedDirectMint` (the same fallback already used for the "swap rounds to zero" case) whenever the rebalance quote would overflow, so a hostile pre-seed degrades to a direct mint instead of bricking `finalizeGraduation`.
- Add an invariant test that pre-seeds the V2 pair with extreme, asymmetric reserves (near `uint112` max on the LT leg, minimal `tokensForLP`/`ltFromPair` target ratio) and asserts `finalizeGraduation` still succeeds.

### Proof of Concept
1. Launch a token via `Zap.createToken`; let it trade on the curve so that it closes with a very small `tokensForLP` relative to `ltFromPair` (achievable by graduating via the USD-threshold trigger with light real LT raised and heavy price appreciation, or via `triggerGraduation` right after threshold-crossing where the parabola `tokensForLP(sold)=sold·(S−sold)/S` yields a small value).
2. `Bonding._executeBuy` fires `_enterGraduating`, caching `PendingGraduation{tokensForLP: small, ltFromPair: large}` (via `_prepareGraduationLiquidity`, `packages/contracts/src/Bonding.sol:1073-1096`).
3. Before anyone calls `finalizeGraduation`, the attacker (an unrelated wallet) calls `IUniswapV2Factory.createPair(token, lt)` (or lets `_ensureUniswapV2Pair` create it) and then directly `IUniswapV2Pair.mint(attacker)` after transferring large, asymmetric amounts of `token` and `lt` into the pair — pushing `reserveToken`/`reserveLT` toward their `uint112` ceiling in a ratio far from the curve-close ratio, while keeping both sides above the `DIRECT_MINT_PRESEED_BPS` (1 bps) floor so Regime 3 (`_seedRebalancing`) is taken instead of falling back to `_seedDirectMint`.
4. Any caller of `finalizeGraduation(token)` now hits `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`, where `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` (`packages/contracts/src/Bonding.sol:1517`) exceeds `type(uint256).max` and reverts with `MathOverflowedMulDiv`.
5. `finalizeGraduation` reverts unconditionally on every subsequent call — the token is permanently stuck in `Lifecycle.Graduating`, and its cached `ltFromPair`/`tokensForLP` remain frozen on `Bonding` forever.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1279-1354)
```text
    function _seedRebalancing(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));

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

        // Budget reads `balanceOf(this)` rather than `tokensForLP` /
        // `ltFromPair` so any skim donation contributes to the rebalance
        // and not only to `_routerDepositAndDispose`'s deposit.
        // Direction: pool TOKEN-rich vs target ⇒ swap LT in (TOKEN out).
        // Pool LT-rich ⇒ swap TOKEN in (LT out). Bounded by uint112 reserves
        // and curve-close-shape targets, both products fit in uint256.
        // When `_pairRebalance` returns false the seed is too small for any
        // swap to move the ratio (its fee-charging quote rounds to zero), so
        // the reserves are negligible against this graduation's inventory:
        // overpower them with a direct mint at the cached ratio rather than
        // letting the router deposit at the attacker's ratio. A swap that
        // does fire leaves the pool ≈ at target for the router deposit.
        if (reserveToken * ltFromPair > reserveLT * tokensForLP) {
            // Pool TOKEN-rich. tokenIn = lt, tokenOut = tokenAddress.
            // tokenInIs0 = (lt is token0) = !tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: lt,
                        tokenInIs0: !tokenIs0,
                        reserveIn: reserveLT,
                        reserveOut: reserveToken,
                        targetN: ltFromPair,
                        targetD: tokensForLP,
                        maxSwap: _swapBudget(_ltSwapInventory(lt, protectedLT))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        } else if (reserveToken * ltFromPair < reserveLT * tokensForLP) {
            // Pool LT-rich. tokenIn = tokenAddress, tokenInIs0 = tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: tokenAddress,
                        tokenInIs0: tokenIs0,
                        reserveIn: reserveToken,
                        reserveOut: reserveLT,
                        targetN: tokensForLP,
                        targetD: ltFromPair,
                        maxSwap: _swapBudget(IERC20(tokenAddress).balanceOf(address(this)))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        }
        // else: pool already at curve-close ratio (rare — e.g. attacker
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1488-1506)
```text
    /// @dev Smallest swap input that drives the pool's reserve ratio
    ///      `(reserveIn + s) / (reserveOut - out)` to `targetN/targetD`
    ///      under the no-fee constant-product model:
    ///        `(reserveIn + s)² = reserveIn * reserveOut * targetN/targetD`
    ///      ⇒ `s = sqrt(reserveIn * reserveOut * targetN/targetD) - reserveIn`,
    ///      capped at `maxSwap`. The actual swap is fee-charging (the pair's
    ///      live fee), so the post-swap ratio drifts from the target by the
    ///      fee; the balanced-subset deposit absorbs the residual without
    ///      donating.
    ///
    ///      `Math.mulDiv` keeps the intermediate product
    ///      `reserveIn * reserveOut * targetN` inside its 512-bit working
    ///      space, but the final result `... / targetD` must still fit in
    ///      uint256. Call sites must keep that invariant — in practice
    ///      both the V2 uint112 reserve cap and the bound that
    ///      `tokensForLP` ≤ `LP_RESERVE` and `ltFromPair` ≤ raised LT
    ///      are well inside the safe envelope. Constructed adversarial
    ///      inputs that violate this would `revert` rather than silently
    ///      truncate, which is the correct failure mode.
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
