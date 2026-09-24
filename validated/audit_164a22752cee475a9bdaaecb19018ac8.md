### Title
Pre-creating the HyperSwap V2 TOKEN/LT pair with a hostile mint lets an unprivileged builder resolve `finalizeGraduation`'s LP seed to an attacker-controlled pool instead of the curve's own context - ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE's bug class is a caller supplying a "name" that the host trusts to resolve inside its own context, when the resolution actually reaches outside it and hands the caller whatever sits at that resolved location. In `Bonding`, the equivalent trusted-name resolution is `_ensureUniswapV2Pair(tokenAddress, lt)`, which looks up (or creates) the canonical `IUniswapV2Factory.getPair(tokenA, tokenB)` address for the token/LT pair that graduation is about to seed. Because that pair address is deterministic and permissionlessly creatable, any unprivileged address can pre-create and pre-mint it before `finalizeGraduation` runs, planting attacker-chosen reserves at the exact location `Bonding` will resolve to and treat as "the" graduation pair.

### Finding Description
`finalizeGraduation` resolves the LP-seeding target purely by name (the deterministic `(token, lt)` pair address), then trusts whatever state it finds there: [1](#0-0) 

`_seedUniswapV2Direct` branches on the resolved pair's live state (`totalSupply() == 0` vs a mint pre-seed) and, for the mint-pre-seed regime, drives a rebalance/deposit sequence (`_seedRebalancing` → `_pairRebalance` → `_routerDepositAndDispose`) using `getAmountOut`/`addLiquidity(min=1, min=1)` against that resolved pair: [2](#0-1) [3](#0-2) [4](#0-3) 

This is the documented defense against "hostile pre-seed," and the code's own natspec acknowledges the swap-cap edge case exists specifically because an attacker can drive the resolved pair's reserves to an extreme imbalance before `finalizeGraduation` ever executes: [5](#0-4) 

The root issue mirrors the CVE precisely: the "name" (`token`/`lt` pair address) is assumed to resolve to a pair whose state is under `Bonding`'s control (an empty pair it seeds itself), but because pair creation and minting on HyperSwap V2 are permissionless, the name instead resolves to whatever an attacker deposited there ahead of time — a resource "outside the build context" of the graduation flow. The mitigation logic (`_swapBudget` capping at 99%, the direct-mint fallback, `_pairRebalance`'s `false` return) is a patch reacting to this resolution gap, not an elimination of it; the underlying trust — "the name resolves to state we own" — is still violated at the moment `_ensureUniswapV2Pair` is called.

### Impact Explanation
A sufficiently large, precisely-shaped pre-seed (an extreme reserve ratio funded by the attacker, sized close to the graduation's own `(tokensForLP, ltFromPair)` budget) forces the capped rebalance swap to consume the full 99% budget on one side. `_routerDepositAndDispose` then only has a small residual of the other side to deposit, so the honest `addLiquidity` call mints a disproportionately small `liquidity` relative to the attacker's pre-existing LP share. Because `LPLock.recordLock` is called unconditionally with whatever `liquidity` `finalizeGraduation` computes, the attacker locks in a majority economic share of the pool at a ratio they chose, while the token creator/traders' curve-raised LT and tokens are deposited at a diluted, attacker-favorable price. This is an LP seeded away from the curve close price and a real value transfer from the graduation's `tokensForLP`/`ltFromPair` inventory to the pre-seeder's own untracked LP position — a concrete freezing/misallocation of trader and creator funds reachable from a fully permissionless action (pre-creating/pre-minting the V2 pair) taken by any unrelated wallet before `finalizeGraduation` executes.

### Likelihood Explanation
`finalizeGraduation` is permissionless and callable by anyone once a token enters `Lifecycle.Graduating`, and the attacker's precondition — creating/minting the HyperSwap V2 pair for a specific, publicly known `(token, lt)` address pair before that call lands — is itself fully permissionless and requires no privileged role, matching the rule set's allowed unprivileged-reachability bar ("pre-creating or pre-seeding the HyperSwap V2 TOKEN/LT pair before graduation"). The window is bounded (a keeper drives finalize quickly), but any token approaching graduation is a public, predictable target, and the attack only requires funding a pre-seed transaction ahead of the keeper's `finalizeGraduation` call — a race that is winnable by a normal front-running actor.

### Recommendation
Do not trust the resolved pair's pre-existing reserves as economically neutral. Either (a) require the pair to have zero reserves and zero `totalSupply` at the start of `_seedUniswapV2Direct` and revert/queue instead of rebalancing against attacker-supplied reserves, or (b) bound the acceptable pre-seed size to a negligible fraction of `tokensForLP`/`ltFromPair` (tighter than the current 99% swap-budget cap) so that no realistic pre-seed can capture a majority LP share, and verify post-deposit that the minted `liquidity` corresponds to at least the expected LP share before calling `LPLock.recordLock`.

### Proof of Concept
1. Attacker observes a token approaching `canGraduate` on the bonding curve (public state via `Bonding.canGraduate`/`previewLtUntilGraduation`).
2. Attacker computes the deterministic HyperSwap V2 pair address for `(tokenAddress, ltAddress)` and calls the V2 factory's `createPair` directly (permissionless, not gated by `Bonding`).
3. Attacker funds the pair with a self-chosen imbalanced ratio and calls `pair.mint(attacker)`, planting a hostile pre-seed sized to approach `Bonding`'s own `(tokensForLP, ltFromPair)` budget.
4. `_enterGraduating` fires (via a threshold-crossing buy or permissionless `triggerGraduation`), and later `finalizeGraduation` is called (by the keeper or anyone).
5. `_ensureUniswapV2Pair` resolves to the attacker's pre-existing pair; `_seedRebalancing`/`_pairRebalance` execute the capped rebalance swap (99% of budget) against the attacker's ratio, and `_routerDepositAndDispose` deposits the diluted residual, minting `liquidity` to `lpLock` that represents a minority of the pool versus the attacker's untouched pre-existing LP tokens.
6. Attacker now holds a disproportionate LP share priced off their own chosen ratio rather than the curve's close price, extracting value from the locked LP relative to what an honest empty-pair seed would have produced.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1275-1354)
```text
    /// @dev Hostile-mint-pre-seed branch of `_seedUniswapV2Direct`. Split
    ///      out because (a) it's the cold path (~99% of graduations hit
    ///      the empty-pair branch above) and (b) the local-variable density
    ///      would otherwise blow stack-too-deep.
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
