### Title
Hostile HyperSwap V2 pre-seed can force `finalizeGraduation` to seed the graduated LP at a price far from curve-close, transferring value to the attacker's own pre-existing LP position - (File: packages/contracts/src/Bonding.sol)

### Summary
`Bonding.finalizeGraduation` seeds the post-graduation HyperSwap V2 `TOKEN/LT` pair via `_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` → `_routerDepositAndDispose`. When an attacker has pre-minted LP in that pair with a sufficiently extreme `TOKEN:LT` ratio, the corrective swap in `_pairRebalance` is capped by `_swapBudget` (99% of Bonding's own LT holdings for that graduation), and the code's own natspec admits the deposit then lands "at the post-swap ratio" rather than the curve-close ratio when the cap binds [1](#0-0) . The router deposit (`addLiquidity` with `min0=1, min1=1`) then commits capital at that still-skewed ratio [2](#0-1) , mispricing the newly locked LP and benefiting the attacker's own pre-existing LP shares in the same pair.

### Finding Description
`_seedUniswapV2Direct` distinguishes three regimes for seeding the graduated LP; Regime 3 ("mint pre-seed") applies when an attacker has already called `pair.mint()` against a self-funded, imbalanced `(TOKEN, LT)` deposit [3](#0-2) .

In that regime, `_seedRebalancing` computes a corrective swap via `_pairRebalance`/`_noFeeSwapInput`, bounded by `maxSwap = _swapBudget(inventory)`, i.e. 99% of whichever side of Bonding's own graduation inventory (LT raised on the curve, or the fixed `tokensForLP`) is available [4](#0-3) . Bonding's LT inventory for a given graduation is bounded (at most ~3× `virtualLtReserve`, itself capped by `VIRTUAL_LIQUIDITY_USD` and the graduation threshold), so the swap budget is finite and known in advance.

An attacker can deliberately make the required correction (`_noFeeSwapInput`'s `s = sqrt(reserveIn*reserveOut*targetN/targetD) - reserveIn`) arbitrarily larger than this fixed budget by pre-seeding the V2 pair with an extreme ratio (e.g., a very large amount of `TOKEN` matched against a very small amount of `LT`) — both assets are freely obtainable by any unprivileged actor: `TOKEN` via ordinary curve buys through `Zap.buy`, and `LT` via BounceTech's public `mint`. Because the swap is explicitly capped (`_swapBudget`) and the deposit leg (`_routerDepositAndDispose`) simply deposits whatever remains at the ratio the pool is *actually* at after the capped swap — not the cached curve-close ratio (`tokensForLP`/`ltFromPair`) — the graduated LP can be permanently seeded at a materially wrong price. The code's own comment on `_swapBudget` states the 1% reserve exists only to avoid bricking `addLiquidity`/`LPLock.recordLock`, explicitly trading off ratio-correctness for non-bricking on "catastrophic pre-seeds beyond our budget capacity" [1](#0-0) .

Because the attacker's own LP tokens from the pre-seed are already resident in the pool (`totalSupply() != 0`, which is exactly what routes execution into Regime 3), the mispriced deposit dilutes/enriches the attacker's existing LP position at the expense of the freshly minted LP that gets locked to `LPLock` for the protocol/creator/holders, and skews the price new post-graduation traders transact at on HyperSwap.

### Impact Explanation
This is a permissionless, capital-bounded manipulation of the one-shot LP seeding that `LPLock.recordLock` cannot skip or correct [5](#0-4) . The result is an LP seeded away from the curve-close price — value is transferred from the newly-locked LP (and thus from the protocol/creator/community that the lock is meant to protect) to the attacker's own pre-existing LP shares, and post-graduation HyperSwap trades execute at an incorrect price relative to the token's actual curve-close valuation. This is a concrete, permanent economic loss for LP/creator/trader funds, matching the "LP seeded away from the curve close price" impact class explicitly in scope.

### Likelihood Explanation
Requires an attacker to (a) accumulate a `TOKEN` position via ordinary curve buys, (b) mint a comparatively small `LT` amount via BounceTech, (c) permissionlessly create/pre-seed the `TOKEN/LT` HyperSwap V2 pair via `pair.mint()` before `finalizeGraduation` runs, sized so that the required rebalance swap exceeds Bonding's bounded LT/TOKEN inventory for that graduation. Since `finalizeGraduation` is permissionless and has no freshness/staleness gate and no upper bound on how skewed a pre-existing pre-seed can be, an attacker with capital and knowledge of the graduation's cached `(tokensForLP, ltFromPair)` values (both public via `pendingGraduation`) can size the attack deterministically. This makes the attack technically straightforward for a well-capitalized unprivileged actor, though it requires up-front capital that is only partially recoverable, placing likelihood at Medium.

### Recommendation
When the computed no-fee swap `s` would need to exceed the available `maxSwap` budget to reach the target ratio, do not proceed with a partial swap + ratio-mismatched deposit. Instead, either (a) revert/defer `finalizeGraduation` for that token until additional protective LT/TOKEN inventory is available, or (b) fall back unconditionally to `_seedDirectMint`-style behavior that overpowers the pre-seed by minting strictly at the cached curve-close ratio and burning/sweeping 100% of any leftover attacker-controlled reserves rather than depositing a partially-corrected, still-skewed balance via `router.addLiquidity`. Additionally, consider bounding how large a pre-existing pool's reserves may be relative to `tokensForLP`/`ltFromPair` before allowing the Regime 3 partial-rebalance path at all.

### Proof of Concept
1. Attacker buys a large amount of `TOKEN` on the curve via `Zap.buy` prior to the token's `triggerGraduation`/curve sellout.
2. Attacker mints a small amount of the corresponding `LT` via BounceTech's public `mint`.
3. Attacker calls `IUniswapV2Factory.createPair(token, lt)` (or lets it be created) and then transfers a large `TOKEN` amount + a disproportionately small `LT` amount into that pair and calls `pair.mint(attacker)`, establishing `totalSupply() != 0` at a hostile ratio.
4. Once the token graduates (`triggerGraduation` fires phase 1, freezing curve trading and caching `pendingGraduation.tokensForLP` / `ltFromPair`), anyone calls `finalizeGraduation(token)`.
5. `_seedUniswapV2Direct` sees `totalSupply() != 0`, enters Regime 3 (`_seedRebalancing`). The needed corrective swap (`_noFeeSwapInput`) exceeds `_swapBudget(inventory)` because the attacker sized the pre-seed imbalance deliberately large relative to Bonding's fixed, bounded LT/TOKEN inventory for this graduation.
6. The swap is capped at the budget, and `_routerDepositAndDispose` deposits the remaining `(remToken, remLT)` via `router.addLiquidity(..., 1, 1, lpLock_, ...)` at the still-skewed post-swap ratio, seeding `LPLock`'s locked LP at a price far from curve-close, while the attacker's own pre-existing LP shares in the pool capture the mispricing.

### Citations

**File:** packages/contracts/src/Bonding.sol (L30-36)
```text
///      curve sellout), two-phase graduation split (phase 1 inline in the
///      threshold-crossing buy, phase 2 permissionless and big-block), dynamic
///      LP seeding (zero-gap between curve close and LP open), and
///      brick-resistance against hostile pre-seeds of the post-grad pair. The
///      most subtle code paths are `_enterGraduating`, `finalizeGraduation`,
///      and `_prepareGraduationLiquidity` — natspec on each function below
///      contains the rationale.
```

**File:** packages/contracts/src/Bonding.sol (L1132-1233)
```text
    /// @dev LP-seeding into the HyperSwap pair, hardened against hostile
    ///      pre-seeds. Three regimes:
    ///
    ///        1. **No LP minted yet — `totalSupply == 0` (~99% of
    ///           graduations).** A pristine empty pair, or a dust pre-seed
    ///           (`transfer(pair, dust) + sync()` leaves `reserves > 0` but
    ///           `totalSupply == 0`). Direct mint at exactly
    ///           `(tokensForLP, ltFromPair)` — V2's first-liquidity branch
    ///           makes those amounts the sole price input, so the pool opens
    ///           at the curve-close ratio and any dust becomes reserves with
    ///           no LP claim.
    ///        2. **Pure-donation pre-seed.** Attacker `transfer`'d to the
    ///           pair without `mint` (balance > 0, reserves == 0).
    ///           `pair.skim(address(this))` pulls the donation into
    ///           `Bonding`; path then collapses to (1). Donated TOKEN is
    ///           burned alongside the empty-pair mint; donated LT is
    ///           handled by `finalizeGraduation`'s post-bookend
    ///           `_sweepLTToOwner` (which uses `protectedLT` snapshotted
    ///           BEFORE skim, so the donation is correctly classified as
    ///           rebalance residue rather than concurrent-graduation
    ///           escrow). NEVER routed to `LPLock` — `LPLock` has no
    ///           rescue path in v1, so anything that lands there is
    ///           permanently stuck.
    ///        3. **Mint pre-seed.** Attacker called `pair.mint` against a
    ///           self-funded seed, baking a hostile (TOKEN, LT) ratio into
    ///           the pool. Without intervention `pair.mint(lpLock)`'s
    ///           `min(amount0·S/r0, amount1·S/r1)` formula would (a) open
    ///           the LP off curve-close-price and (b) donate the larger arm
    ///           to the attacker's pre-existing LP. We rebalance via a
    ///           direct `pair.swap` toward the curve-close ratio, then
    ///           deposit the remaining inventory via the router's
    ///           `quote()`-based `addLiquidity` — which only pulls the
    ///           optimal amounts at the post-swap ratio, so neither side
    ///           becomes a `min()` donation. Off-ratio TOKEN remainder is
    ///           burned; off-ratio LT remainder is auto-swept to the owner
    ///           by `finalizeGraduation`'s post-bookend (see its natspec).
    ///           When the seed is small enough that the fee-charging swap
    ///           quote rounds to zero, no swap can move the ratio — but the
    ///           reserves are then negligible against this graduation's
    ///           inventory, so we fall back to the regime-1 direct mint
    ///           (`_seedDirectMint`) and open at the cached ratio anyway.
    ///           The captured LP share is bounded by
    ///           `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`,
    ///           which vanishes for any seed that small.
    ///
    ///      Brick resistance: the rebalance swap input is capped at our
    ///      per-side budget; a swap whose fee-charging `getAmountOut` would
    ///      round to zero (which would otherwise revert `pair.swap` with
    ///      `INSUFFICIENT_OUTPUT_AMOUNT`) is replaced by the direct-mint
    ///      fallback; the deposit uses `addLiquidity(min=1, min=1)`; and the
    ///      empty/donation regimes don't touch the router or `pair.swap`. So
    ///      a hostile pre-seed of any shape cannot DoS `finalizeGraduation`.
    ///
    ///      Asymmetric router usage: **the rebalance swap is direct-to-pair
    ///      (`pair.swap`), not router-mediated.** HyperSwap mainnet's V2
    ///      router replaces every canonical swap function with FoT-only
    ///      variants that take a non-standard `referrer` argument (selectors
    ///      `ac3893ba` / `b4822be3` / `52aa4c22`).
    ///      `Zap._swapOnUniswapV2` already uses `pair.swap` for the
    ///      same reason; matching the pattern keeps both in sync and
    ///      removes a HyperSwap-specific footgun. The deposit leg DOES
    ///      use `router.addLiquidity` because that function IS canonical
    ///      V2 on HyperSwap (verified selector `e8e33700`) and the
    ///      router's `quote()`-based optimal-split logic is non-trivial
    ///      to safely reimplement.
    ///
    ///      Phase 1 is unchanged (the rebalance fires only in phase 2
    ///      when reserves are non-zero), so the small-block gas budget
    ///      is preserved.
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
```

**File:** packages/contracts/src/Bonding.sol (L1297-1349)
```text
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
```

**File:** packages/contracts/src/Bonding.sol (L1356-1378)
```text
    /// @dev Cap the rebalance swap at 99% of the available side's budget,
    ///      so the subsequent `addLiquidity` always has a non-zero amount
    ///      of BOTH sides to deposit. Without this, an extreme hostile
    ///      pre-seed (massively imbalanced reserves) drives the
    ///      unconstrained `_noFeeSwapInput` past our per-side budget,
    ///      `_pairRebalance` clamps to the full budget, and the swap
    ///      consumes 100% of one side. `_routerDepositAndDispose` then
    ///      skips `addLiquidity` (`remToken == 0` or `remLT == 0`),
    ///      `finalizeGraduation` returns `liquidity = 0`, and
    ///      `LPLock.recordLock(...)` records a zero-sized lock — the
    ///      attacker's pre-existing LP becomes 100% of the pool. Reserving
    ///      1% guarantees the deposit leg always lands AND mints non-zero
    ///      LP at the post-swap ratio. The 1% comes off the swap, not the
    ///      deposit — for any realistic pre-seed `s_unconstrained` is
    ///      orders of magnitude below `maxSwap`, so the cap doesn't bind
    ///      and behaviour is unchanged. It only kicks in for catastrophic
    ///      pre-seeds beyond our budget capacity, where the alternative
    ///      is bricking.
    function _swapBudget(
        uint256 budget
    ) internal pure returns (uint256) {
        return (budget * 99) / 100;
    }
```

**File:** packages/contracts/src/Bonding.sol (L1449-1473)
```text
    function _routerDepositAndDispose(
        address tokenAddress,
        address lt,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        BondingStorage storage $ = _s();
        address routerAddr = $.uniswapV2Router;
        address lpLock_ = $.lpLock;
        uint256 remToken = IERC20(tokenAddress).balanceOf(address(this));
        // Subtract `protectedLT` (LT that doesn't belong to this graduation
        // — concurrent escrows or stray dust, snapshotted at the top of
        // `finalizeGraduation`) so the deposit allowance can never pull
        // another graduation's earmark or accidentally absorb dust into a
        // locked LP.
        uint256 ltBal = IERC20(lt).balanceOf(address(this));
        uint256 remLT = ltBal > protectedLT ? ltBal - protectedLT : 0;

        if (remToken > 0 && remLT > 0) {
            IERC20(tokenAddress).forceApprove(routerAddr, remToken);
            IERC20(lt).forceApprove(routerAddr, remLT);
            (,, liquidity) = IUniswapV2Router02(routerAddr)
                .addLiquidity(tokenAddress, lt, remToken, remLT, 1, 1, lpLock_, block.timestamp);
            IERC20(tokenAddress).forceApprove(routerAddr, 0);
            IERC20(lt).forceApprove(routerAddr, 0);
        }
```
