### Title
Hostile HyperSwap V2 pre-seed can outsize `_pairRebalance`'s budget-capped defense, permanently locking the graduated LP away from the curve-close price - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The SHIDO_exp2 report's bug class is a *cross-venue price mismatch*: an attacker manipulates one representation of value (a fee-on-transfer pool, then a lock/claim conversion) so that a downstream swap settles at a price divorced from the fair rate, and pockets the difference. alt.fun's structural analog is the two-phase graduation flow in `Bonding.sol`, where a HyperSwap V2 TOKEN/LT pair that an attacker can pre-seed *before* `finalizeGraduation` runs is only defended by a rebalance swap whose budget is capped to Bonding's own (small, threshold-bounded) curve inventory — not to the size of the hostile pre-seed. A well-funded attacker can pre-seed the pair with a ratio the rebalance cannot fully correct, so the LP that Bonding deposits at the end of `_routerDepositAndDispose` opens materially off the curve-close price, letting the attacker's own (unlocked) LP position capture a disproportionate share of the curve-raised LT and the 250M reserved tokens.

### Finding Description
`finalizeGraduation` (`packages/contracts/src/Bonding.sol:1000-1034`) hands off to `_seedUniswapV2Direct` (`Bonding.sol:1201-1234`), which — when the HyperSwap pair already has LP supply (`totalSupply() != 0`, "Regime 3") — calls `_seedRebalancing` (`Bonding.sol:1279-1354`).

`_seedRebalancing` measures how far the live pool ratio is from the cached curve-close target `(tokensForLP, ltFromPair)` and, when the imbalance is above a tiny `DIRECT_MINT_PRESEED_BPS` (1 bp) band, tries to correct it with a single direct-to-pair swap via `_pairRebalance` (`Bonding.sol:1414-1429`), sized by `_noFeeSwapInput` (`Bonding.sol:1507-1522`) and hard-capped by `_swapBudget`: [1](#0-0) 

`_swapBudget` caps the correction swap at 99% of *Bonding's own* available inventory — `IERC20(tokenAddress).balanceOf(address(this))` or `_ltSwapInventory(lt, protectedLT)` (`Bonding.sol:1316-1349`, `1383-1389`). That inventory is intrinsically small: `tokensForLP ≤ LP_RESERVE` (250M tokens, `Bonding.sol:67`) and `ltFromPair` is the LT raised by the curve, which is bounded by the graduation threshold (`VIRTUAL_LIQUIDITY_USD = 3000 ether`, peaking near `3×` at sell-out, i.e. ≈ `$9K`, per `Bonding.sol:50-61`).

If an attacker pre-seeds the HyperSwap V2 pair (permissionless — `IUniswapV2Factory.createPair` / `IUniswapV2Router02.addLiquidity` are public, and `_ensureUniswapV2Pair` at `Bonding.sol:1121-1130` simply reuses whatever pair already exists) with reserves whose imbalance, in absolute LT/token terms, exceeds what a ≤$9K-equivalent-LT / ≤250M-token swap budget can move, `_pairRebalance`'s single capped swap cannot bring the pool back to the curve-close ratio. There is no retry, no revert-and-abort, and no fallback to a *safe* failure mode in this branch (the direct-mint fallback in `Bonding.sol:1330-1332` / `1346-1348` only fires when `_pairRebalance` returns `false`, i.e. when the *computed* no-fee swap size is zero — not when the swap executes but is simply too small relative to the pre-seed). The mismatched-ratio pool is then handed to `_routerDepositAndDispose` (`Bonding.sol:1449-1486`), which deposits Bonding's remaining inventory via `router.addLiquidity(..., 1, 1, lpLock_, ...)` at whatever ratio the pool is left at — `min=1` intentionally disables any slippage protection here (`Bonding.sol:1437-1444`), so the deposit always lands, at a price the attacker chose.

Only the *newly minted* liquidity from this deposit is passed to `LPLock.recordLock` (`Bonding.sol:1031`); the attacker's own, earlier self-funded LP position from their pre-seed `addLiquidity`/`mint` call is never locked and can be withdrawn immediately.

### Impact Explanation
This directly produces "an LP seeded away from the curve close price" backed by real assets: the deposit that lands in the mispriced pool is funded by the curve-raised LT (real trader capital) and the 250M reserved tokens (`tokensForLP`, capped at `LP_RESERVE`) that `Bonding` parks between phase 1 and phase 2 (`Bonding.sol:1073-1096`). Because the resulting public pool price is skewed toward the attacker's chosen ratio, and the attacker holds a large unlocked LP share from their own pre-seed, they can withdraw their LP immediately post-graduation to claim a disproportionate share of the just-deposited real assets, and/or arbitrage the mispriced pool against fair value — extracting value that belongs to curve buyers/creator/protocol. This is a concrete theft vector against LP funds, not merely a cosmetic pricing issue.

### Likelihood Explanation
Requires only unprivileged, permissionless actions: minting LT via BounceTech's public `mint()` (bounded only by attacker's USDC), buying curve tokens via `Zap.buy` (bounded by curve economics but purchasable with enough capital), and calling `IUniswapV2Factory.createPair` / `addLiquidity` on HyperSwap before `finalizeGraduation` runs. Since the correction budget is capped near the graduation threshold (~$9K-equivalent LT, ≤250M tokens), an attacker with capital moderately larger than that threshold can reliably outsize the defense on any given launch, especially since `finalizeGraduation` is permissionless with "no freshness timestamp / staleness gate" (per the code's own natspec, `Bonding.sol:995-999`), giving the attacker an unbounded window to pre-seed before a keeper (or anyone) calls it.

### Recommendation
Make the Regime-3 defense fail safe rather than fail open when the rebalance budget cannot bring the pool within a bounded tolerance of the curve-close ratio: after `_pairRebalance`, re-check the resulting pool ratio against `(tokensForLP, ltFromPair)` and, if still outside an acceptable band, skip the router deposit (`_routerDepositAndDispose`) entirely and instead escrow Bonding's remaining inventory for a permissioned/owner-driven recovery path, rather than depositing at `min=1,1` into a still-mispriced pool. Alternatively, size the rebalance budget relative to the *pre-seed's* reserves (not solely Bonding's own inventory) so a large hostile pre-seed cannot categorically evade correction.

### Proof of Concept
Conceptually mirrors the SHIDO_exp2 flash-loan/price-mismatch pattern, adapted to alt.fun's graduation flow:
1. Attacker identifies a curve token nearing (or forces, via `triggerGraduation`) graduation.
2. Before `finalizeGraduation` is called, attacker: (a) mints a large amount of the token's LT via BounceTech `mint()` with USDC; (b) buys a meaningful share of the curve's TOKEN via `Zap.buy`; (c) calls `IUniswapV2Factory.createPair(token, lt)` then `IUniswapV2Router02.addLiquidity(token, lt, largeTokenAmt, largeLtAmt, ...)` seeding a ratio far from the curve's current price, sized so the imbalance in absolute LT/token terms exceeds `LP_RESERVE` (250M tokens) / `~$9K`-equivalent LT.
3. Anyone calls `Bonding.finalizeGraduation(token)`. `_seedRebalancing`'s `_pairRebalance` swap, capped by `_swapBudget` to Bonding's own inventory, cannot correct the ratio; `_routerDepositAndDispose` deposits at the still-skewed ratio with `min=1,1`.
4. Attacker withdraws their own (unlocked) pre-seed LP tokens and/or trades against the mispriced pool, extracting value funded by the curve-raised LT and reserved 250M tokens.

Exact reproduction (attacker-controlled pre-seed sizing thresholds, precise profit accounting) requires a Foundry fork test against a real `Factory`/`Bonding`/`Router` deployment plus a BounceTech LT and HyperSwap V2 fork, which is beyond static review — this should be validated with a concrete Foundry PoC before remediation. [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1374-1378)
```text
    function _swapBudget(
        uint256 budget
    ) internal pure returns (uint256) {
        return (budget * 99) / 100;
    }
```

**File:** packages/contracts/src/Bonding.sol (L1449-1486)
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

        // Burn off-ratio TOKEN remainder (`Bonding` is the Token owner).
        // Hostile pre-seeds reduce circulating supply by the attacker's
        // wasted-side share, net positive for honest holders.
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
        // LT remainder is third-party — we cannot burn it. It stays in
        // this contract until `finalizeGraduation`'s post-bookend sweeps
        // it to the owner. Honest graduations never reach this code path,
        // so the residue is zero outside attack scenarios.
    }
```
