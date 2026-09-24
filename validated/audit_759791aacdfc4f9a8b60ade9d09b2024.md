### Title
Permanent Denial-of-Service on `finalizeGraduation()` via `Math.mulDiv` Overflow in `_noFeeSwapInput` - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The Nethermind report describes a crash triggered by feeding a peer unbounded/adversarial input that the client's processing code does not validate before performing an expensive operation, permanently taking the node down. The on-chain analog is `Bonding._noFeeSwapInput`, called from the mandatory HyperSwap V2 LP-seeding path of `finalizeGraduation()`. An attacker who controls both the bonding-curve's sell-off state and the pre-seeded HyperSwap V2 `TOKEN/LT` pair reserves can force `Math.mulDiv`'s internal multiplication to exceed `uint256`, causing every future call to `finalizeGraduation()` for that token to revert, permanently bricking graduation.

### Finding Description
`finalizeGraduation()` unconditionally routes any pre-seeded (mint-regime) HyperSwap V2 pair through `_seedUniswapV2Direct → _seedRebalancing → _pairRebalance → _noFeeSwapInput`: [1](#0-0) 

`_noFeeSwapInput` computes:
```
product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD)
```
The natspec on this function explicitly flags the risk: the result of this `mulDiv` "must still fit in uint256" and that "constructed adversarial inputs that violate this would `revert`", asserting it is safe only because `tokensForLP ≤ LP_RESERVE` and reserves are `uint112`-capped: [2](#0-1) 

That safety assumption breaks down because `targetN`/`targetD` are not independent of curve trading state. `tokensForLP` and `ltFromPair` are derived by `_prepareGraduationLiquidity` from the parabola `tokensForLP(sold) = sold·(S−sold)/S`, which trends to **zero as the curve approaches full sellout** while `ltFromPair` (the real LT raised) simultaneously approaches its maximum (documented as up to `3 × virtualLtReserve`): [3](#0-2) 

So an unprivileged trader who buys out almost the entire curve via `Zap.buy`/`Bonding.buy` (reachable, unprivileged) can drive `tokensForLP` toward a dust value (e.g. a handful of wei) while `ltFromPair` stays large (order `10^33`). The same actor can also pre-mint the destination HyperSwap V2 pair (`IUniswapV2Pair.mint`, an unprivileged call anyone can make before `finalizeGraduation` runs — this is the exact "pre-seeding the HyperSwap V2 TOKEN/LT pair before graduation" primitive the code's own `_seedRebalancing` regime-3 path defends against) with large `reserveToken`/`reserveLT` close to `uint112` capacity: [4](#0-3) 

With `product = reserveIn * reserveOut` on the order of `10^60` and `targetN/targetD` (i.e. `ltFromPair/tokensForLP`) inflated to an extreme ratio by the near-sellout curve state, `Math.mulDiv(product, targetN, targetD)` exceeds `type(uint256).max` and reverts (OpenZeppelin's `Math.mulDiv` reverts, rather than truncates, when the result overflows).

Because `finalizeGraduation()` recomputes byte-identical inputs on every call (the `PendingGraduation` struct is frozen once `_enterGraduating` runs, and `Lifecycle.Graduating` blocks any further curve trading that could change the ratio), this revert is **deterministic and permanent** — there is no retry, no admin override, and no alternate code path to reach `Lifecycle.Graduated` for that token.

### Impact Explanation
Once bricked, the token can never graduate:
- The entire curve-raised LT (`ltFromPair`, already pulled into `Bonding` via `Router.graduate` in `_prepareGraduationLiquidity`) is permanently stuck in `Bonding`.
- The 250M reserved LP tokens (`LP_RESERVE`) are permanently stuck in `Bonding`.
- `LPLock.recordLock` can never fire, and the token can never trade on HyperSwap V2.

This is a permanent freezing of curve-raised trader/creator funds, matching the accepted impact class ("permanent freezing of trader, creator or LP funds").

### Likelihood Explanation
Both preconditions are reachable by a single unprivileged address using only public entry points: (1) buying out the curve near-sellout via `Zap.buy`/`Bonding.buy`, and (2) pre-minting the HyperSwap V2 pair via `IUniswapV2Pair.mint` before calling (or letting a keeper call) `finalizeGraduation`. No privileged role, upgrade, or off-chain component is required. The cost is bounded by the capital needed to buy most of the curve and to seed a large-but-`uint112`-bounded V2 pair — a cost an attacker may find acceptable to permanently deny a competitor's or victim's token launch, or as pure griefing since the attacker's own curve tokens/LT is also otherwise recoverable/tradeable.

### Recommendation
- Replace the raw `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` with a formulation that bounds intermediate magnitude regardless of the `targetN/targetD` ratio (e.g. compute the target ratio in a normalized/fixed-point form before combining with reserves, or clamp `targetN`/`targetD` inputs to a bounded ratio before the multiply).
- Add an explicit try/catch (or pre-check) around the rebalance quote so that an overflowing computation falls back to `_seedDirectMint` (the same fallback already used when `_pairRebalance` returns `false`), instead of allowing `finalizeGraduation` to revert unconditionally.
- Consider bounding the achievable `ltFromPair/tokensForLP` ratio at the source (e.g. floor `tokensForLP` away from zero, or cap `ltFromPair` used in the rebalance target) so the near-full-sellout regime cannot produce arbitrarily large ratios.

### Proof of Concept
1. Attacker (or colluding party) launches or targets a live curve token `T` paired with LT `L` via `Bonding`/`Zap`.
2. Attacker repeatedly calls `Zap.buy`/`Bonding.buy` to purchase nearly the entire 750M curve supply, driving `Pair.tokenBalance()` toward (but not exactly) `0`, so `_prepareGraduationLiquidity`'s `tokensForLP = ltFromPair * tokenReserve / assetReserve` rounds to a dust value while `ltFromPair` sits near its curve-max (`~3× virtualLtReserve`).
3. Before `finalizeGraduation` is called, attacker (having acquired large LT holdings and a share of the bought-out `T` supply) calls `IUniswapV2Factory.createPair(T, L)` then `IUniswapV2Pair.mint` with reserves pushed toward the `uint112` ceiling.
4. Any caller (keeper or attacker) invokes `Bonding.finalizeGraduation(T)`. Execution reaches `_seedRebalancing → _pairRebalance → _noFeeSwapInput`, where `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` with the inflated ratio overflows `uint256` and reverts.
5. `finalizeGraduation(T)` reverts identically on every subsequent call — the token is permanently stuck in `Lifecycle.Graduating`, with the raised LT and 250M reserved tokens frozen in `Bonding` indefinitely.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
    }
```

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
