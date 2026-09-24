## Title
`_seedRebalancing`'s round-to-zero fallback lets a large, near-target-ratio pre-seed force a full-inventory `mint()` donation to the attacker's LP - ([File: packages/contracts/src/Bonding.sol])

## Summary
The external report describes attacker-supplied data being fed, unchecked, into a privileged execution path (`COPY FROM PROGRAM`) that the trusted component then executes at face value. The analogous class on alt.fun is Bonding's hostile-pre-seed defense for HyperSwap V2 LP seeding: `finalizeGraduation` → `_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` → fallback `_seedDirectMint`, where a value the attacker controls (the pre-existing pair reserves/ratio) is trusted to decide whether the protocol's entire graduation inventory gets deposited via the raw, unguarded `IUniswapV2Pair.mint()` path.

## Finding Description
`finalizeGraduation` is permissionless and calls `_seedUniswapV2Direct`, which routes a non-empty, attacker-pre-minted pool into `_seedRebalancing` [1](#0-0) .

`_seedRebalancing` only takes the "overpower with direct mint" fast path up front when **both** sides of the pre-seed are below `DIRECT_MINT_PRESEED_BPS` (1 bp) of the LP-bound target — i.e. only when the pre-seed is provably dust [2](#0-1) . Otherwise it computes a corrective swap via `_pairRebalance`, and **only falls back to `_seedDirectMint` again if that swap's quote rounds to zero**, on the documented assumption that "the reserves are then negligible against this graduation's inventory" [3](#0-2) .

That assumption is false. `_pairRebalance` computes the no-fee-optimal swap size `s` from `_noFeeSwapInput`, which returns a value proportional to *how far off* the current ratio is from the target, not to the *absolute size* of the reserves [4](#0-3) . An attacker can pre-mint the HyperSwap V2 pair with **large** reserves that sit *almost exactly* — but not exactly — at the curve-close ratio. This yields a tiny, non-zero `s`, and the pair's fee-charging `getAmountOut(s, tokenIn)` truncates to `0`, so `_pairRebalance` returns `false` [5](#0-4) . That is precisely the trigger for the fallback: `_seedDirectMint` is called against a pool that is **not dust** (it bypassed the `DIRECT_MINT_PRESEED_BPS` check because it is large) and whose `totalSupply() > 0` (the attacker's own LP shares) [6](#0-5) .

`_seedDirectMint` unconditionally transfers the *entire* graduation payload (`tokensForLP` up to `LP_RESERVE`, and all of `ltFromPair`, the curve's full raised LT) into the pair and calls the raw `IUniswapV2Pair.mint(lpLock)` [7](#0-6) . Standard UniswapV2 `mint()` on a non-empty pool computes `liquidity = min(amount0*totalSupply/reserve0, amount1*totalSupply/reserve1)`; whichever side is proportionally larger than the other relative to the pool's *actual* (slightly off-target) ratio is silently donated to the pre-existing LP holder — the attacker — while `lpLock` only receives LP proportional to the smaller side. The code's own natspec acknowledges this exact "min() donates the over-funded side to the pre-seeder" mechanic for the dust regime, but nothing re-validates that the reserves are actually dust-sized before invoking it from the round-to-zero branch.

## Impact Explanation
Because the trigger condition (`getAmountOut` truncating to zero) is a function of *ratio precision*, not *reserve magnitude*, an attacker can force this fallback while the pre-seeded reserves are arbitrarily large (bounded only by `uint112` and the attacker's own capital to mint LT/token equivalents — but note the attacker only needs the token side scaled at will and LT sized to be close to ratio, since donated funds return once the LP is later removed). The protocol then donates a slice of the full graduation-bound `tokensForLP`/`ltFromPair` — potentially close to the entire `LP_RESERVE` (250M tokens) or the entire curve-raised LT — into LP shares that are majority-owned by the attacker, who can immediately withdraw via `IUniswapV2Pair.burn`. This is concrete theft of creator/trader LP funds and an LP seeded away from the true curve-close price, matching the accepted impact classes.

## Likelihood Explanation
`finalizeGraduation` is fully permissionless and reachable by any unprivileged address once a token is `Lifecycle.Graduating` [8](#0-7) . An attacker only needs to front-run the keeper: create the HyperSwap V2 pair (or reuse `_ensureUniswapV2Pair`'s creation) and `pair.mint()` a self-funded position sized to sit just off the eventual curve-close ratio before calling (or letting the keeper call) `finalizeGraduation`. Predicting the curve-close ratio is straightforward since it is derived from pure on-chain pair state (`_prepareGraduationLiquidity`'s `tokensForLP`/`ltFromPair` are fixed the moment phase 1 fires, well before phase 2/finalize executes) [9](#0-8) . The narrow-window precision needed to hit "ratio close enough that the corrective swap quote rounds to zero" is a tunable, computable target, not luck.

## Recommendation
In `_seedRebalancing`, do not treat "`_pairRebalance` returned false" as proof that reserves are negligible. Before falling back to `_seedDirectMint`, re-check that `reserveToken`/`reserveLT` are still within the `DIRECT_MINT_PRESEED_BPS` band relative to `tokensForLP`/`ltFromPair` (the same guard already used for the upfront dust check). If the pre-seed is large but the swap quote rounds to zero, either widen the swap precision (e.g. round the swap size up rather than relying on the pair's truncating `getAmountOut`), or route to `_routerDepositAndDispose` (which uses the router's `quote()`-based optimal-split addLiquidity and never exposes a `min()` donation) instead of the raw `mint()`.

## Proof of Concept
1. Token trades on the curve until `canGraduate` is true; phase 1 (`_enterGraduating`) fixes `tokensForLP` and `ltFromPair` in `pendingGraduation`.
2. Attacker (or a script watching for `TokenGraduating`) calls `Bonding._ensureUniswapV2Pair`-equivalent (`v2Factory.createPair(token, lt)` directly, or lets the pair creation happen) and self-funds a large `token`/`lt` deposit into the pair, then calls `pair.mint(attacker)`, choosing the deposited amounts so that `reserveToken/reserveLT` differs from `tokensForLP/ltFromPair` by an amount small enough that `_noFeeSwapInput`'s resulting `s` produces `pair.getAmountOut(s, tokenIn) == 0` (achievable by scaling both reserves up while holding the ratio delta to a few wei-equivalent units).
3. Anyone calls `finalizeGraduation(token)`. `_seedRebalancing` computes the mismatch, `_pairRebalance` returns `false` (quote rounds to zero), and falls back to `_seedDirectMint`, which transfers the full `tokensForLP`/`ltFromPair` to the pair and calls `pair.mint(lpLock)` against the attacker's non-empty, non-dust reserves.
4. Standard V2 `mint()` math donates the proportionally larger side of the deposit to the attacker's pre-existing LP shares (since `totalSupply() > 0`); `lpLock` receives disproportionately little.
5. Attacker calls `pair.burn()` on their LP shares to withdraw the donated `token`/`lt`, realizing profit while the graduation's LP position remains under-collateralized relative to what should have been seeded.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1005)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();
```

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

**File:** packages/contracts/src/Bonding.sol (L1201-1234)
```text
    function _seedUniswapV2Direct(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        // Regime 2 — pull any donation pre-seed into this contract so it
        // doesn't pollute the post-swap ratio. Routed to `address(this)`
        // (NOT `lpLock`) so donated TOKEN can be burned and donated LT
        // can be swept to the owner via `_sweepLTToOwner` — `LPLock` has
        // no rescue path, so anything sent there is permanently stuck.
        // No-op on a freshly-created pair (balance == reserves == 0).
        IUniswapV2Pair(pair).skim(address(this));

        // Regime 1 — no LP minted yet (`totalSupply == 0`): a pristine empty
        // pair, or a dust pre-seed from `transfer(pair, dust) + sync()` that
        // leaves reserves non-zero while supply is still zero. Keying on
        // supply rather than reserves routes the dust shape here instead of
        // the rebalance path: with zero supply V2 mints from our amounts
        // alone, so the pool opens at the cached ratio and any dust becomes
        // reserves with no LP claim.
        if (IUniswapV2Pair(pair).totalSupply() == 0) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Regime 3 — mint pre-seed: rebalance, then deposit balanced subset.
        // `lpLock_` re-read from storage inside `_routerDepositAndDispose`.
        // Reserves and token-ordering re-read inside `_seedRebalancing` to
        // keep this function's stack pressure under solc's 16-slot ceiling
        // without `viaIR`.
        return _seedRebalancing(tokenAddress, lt, pair, tokensForLP, ltFromPair, protectedLT);
    }
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

**File:** packages/contracts/src/Bonding.sol (L1310-1332)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1488-1522)
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
