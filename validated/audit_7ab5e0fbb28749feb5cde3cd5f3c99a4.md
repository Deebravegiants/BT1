## Analog Found

### Title
Permissionless HyperSwap pre-seed can overflow `_noFeeSwapInput`'s discriminant and permanently brick `finalizeGraduation` - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The MongoDB report describes a large, adversarially-shaped input (a document) that overflows internal accounting during a critical operation (oplog replication), stalling the system until it crashes. The structural analog in alt.fun is `Bonding._noFeeSwapInput`, the hostile-pre-seed rebalance math run inside the permissionless `finalizeGraduation` path. An attacker who front-runs graduation by pre-creating the HyperSwap V2 pair and minting a skewed-ratio LP into it (the documented "Regime 3 mint pre-seed" attack, [1](#0-0) ) can size the pre-seed reserves such that `_noFeeSwapInput`'s discriminant overflows `uint256`, causing `Math.mulDiv` to revert unconditionally on every future call — permanently bricking `finalizeGraduation` for that token.

### Finding Description
`_noFeeSwapInput` computes the closed-form rebalance swap as:
```
uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
uint256 newIn = Math.sqrt(product);
``` [2](#0-1) 

`reserveIn`/`reserveOut` come directly from `IUniswapV2Pair(pair).getReserves()` on the attacker-influenceable HyperSwap pair (uint112-bounded, up to `type(uint112).max`), and `targetN`/`targetD` are `(ltFromPair, tokensForLP)` or `(tokensForLP, ltFromPair)` depending on skew direction — both taken straight from `_seedRebalancing` without any bound check on the *ratio* between them: [3](#0-2) .

The code's own test suite documents the overflow condition explicitly: with reserves near `uint112.max` and a target ratio far from 1:1 (i.e. `targetD` small relative to `targetN`), the discriminant `reserveIn * reserveOut * targetN / targetD` exceeds `2^256` and `Math.mulDiv` panics: [4](#0-3) . The natspec on `_noFeeSwapInput` itself acknowledges the precondition is caller-enforced, not internally guarded: "Call sites must keep that invariant... Constructed adversarial inputs that violate this would `revert` rather than silently truncate" [5](#0-4) .

Critically, `targetD` is not bounded away from small values: when the pool is LT-rich, `targetD = ltFromPair`, the actual real LT raised by the curve — this can be arbitrarily small in wei terms for a token that graduates via the supply trigger (full sellout) rather than the USD trigger, especially against a BounceTech LT with a high per-unit exchange rate [6](#0-5) . An attacker who front-runs `finalizeGraduation` with `pair.mint()` at a sufficiently large, skewed token/LT ratio can drive the discriminant past `2^256`, and this pre-seed shape is permanent — every subsequent call to `finalizeGraduation` re-reads the same attacker-set reserves and reverts identically.

### Impact Explanation
`finalizeGraduation` has no other code path once `_seedRebalancing`'s rebalance branch is entered (Regime 3), because the direct-mint fallback (`_seedDirectMint`) only fires when the pre-seed is *below* the `DIRECT_MINT_PRESEED_BPS` band on both sides [7](#0-6)  — a large, deliberately-sized pre-seed sits above that band on at least one side, so it always reaches `_pairRebalance` → `_noFeeSwapInput`. Since the revert is unconditional and deterministic against the fixed on-chain reserves the attacker set, `finalizeGraduation` reverts forever. This permanently freezes the token in `Lifecycle.Graduating`: the curve-raised LT (drained into `Bonding` at phase 1) and the 250M LP-reserve tokens parked on `Bonding` per the two-phase design [8](#0-7)  can never be locked into an LP or otherwise released — a permanent freeze of creator/trader/protocol funds, directly satisfying the brick-resistance property the team explicitly ranks as its top security invariant ("a brick locks every holder in `Graduating` forever" [9](#0-8) ).

### Likelihood Explanation
The attack requires no privileged role — any address can call `factory.createPair`, transfer TOKEN/LT to the new pair, and call `pair.mint(attacker)` before `finalizeGraduation` runs, exactly as documented for the existing pre-seed defense [10](#0-9) . The economic cost scales with how large a reserve pair the attacker must fund to force the discriminant past `2^256`; this cost drops sharply against tokens that graduate with a small `ltFromPair` (supply-trigger graduations, or curves on highly-appreciated LTs), which the protocol's own dual-trigger design permits by construction. This is a real, if capital-gated, DoS surface that the code comments concede is only "unrealistic... but mathematically possible" rather than structurally prevented.

### Recommendation
Add an explicit bound/guard in `_noFeeSwapInput` (or at its call sites in `_seedRebalancing`) that caps the discriminant or falls back to `_seedDirectMint` whenever `Math.mulDiv` would overflow, instead of letting the panic propagate out of `finalizeGraduation`. A `try/catch`-free approach — e.g. pre-checking `reserveIn * reserveOut` against `type(uint256).max / targetN * targetD` before calling `Math.mulDiv`, and routing to the direct-mint fallback on failure — would preserve the brick-resistance invariant the rest of the pre-seed defense already relies on.

### Proof of Concept
1. Launch a token normally via `Zap.createToken`; let it trade until it is eligible to graduate via the supply trigger (`IPair.tokenBalance() == 0`) with a small real `ltFromPair` (e.g. because the reserve LT has a high `exchangeRate()`, so few LT wei were needed to fully buy the curve).
2. Once `_enterGraduating` caches `(tokensForLP, ltFromPair)` with `ltFromPair` small, front-run `finalizeGraduation`:
   - `factory.createPair(token, lt)`
   - Acquire and `transfer` large, skewed TOKEN and LT balances into the new pair such that `reserveToken * ltFromPair` and `reserveLT * tokensForLP` diverge and `reserveIn * reserveOut * targetN / targetD > 2^256` (sized per the boundary demonstrated in `test_overflowSafety_atRealisticMax`, [11](#0-10) ).
   - Call `pair.mint(attacker)`.
3. Call `Bonding.finalizeGraduation(token)`. It reaches `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`, where `Math.mulDiv` panics with `UNDER_OVERFLOW`, reverting the whole transaction.
4. Every subsequent call to `finalizeGraduation(token)` reverts identically against the same pre-seeded reserves — the token is permanently stuck in `Lifecycle.Graduating`, and the curve-raised LT plus the 250M reserve tokens held on `Bonding` are unrecoverable.

### Citations

**File:** packages/contracts/AGENTS.md (L130-149)
```markdown
### The exploit

A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

When our `pair.mint(lpLock)` runs in phase 2 against this non-empty pair, V2's mint formula picks up the existing reserves:

```
liquidity = min(amount0 · totalSupply / reserve0, amount1 · totalSupply / reserve1)
```

The `min(...)` arm whose denominator is bigger relative to its numerator wins, and the OTHER arm's "excess" deposit is donated pro-rata to existing LP holders — i.e. to the attacker. Two harms:

- **Wrong opening price.** Post-mint reserves are `(R_attacker + T_a, R_attacker + T_b)`, so the LP opens at `(R_a + T_a) / (R_b + T_b)`, NOT at the curve close `T_a / T_b`. A `$15` LT pre-seed at 50% off curve close opens the pool ~454 bps off.
- **LP capture.** The wasted-side excess goes to the attacker's LP claim. A `1 wei + 1 LT` pre-seed (~`$1` attack budget) captures ~34 bps of LP.

A cheaper variant skips step 3 entirely: `transfer(pair, dust) + pair.sync()` forces the stored reserves to the dust ratio without minting any LP, leaving the pair at `reserves > 0 && totalSupply == 0`. Regime 1 below covers both shapes by keying on supply rather than reserves.
```

**File:** packages/contracts/AGENTS.md (L176-182)
```markdown
#### Regime 3 — mint pre-seed (the actual exploit)

Attacker called `pair.mint(attacker)` against a self-funded dust seed. Reserves are non-zero at a hostile ratio. We:

1. **Compute the swap input** that would drive the pool ratio back to the curve-close ratio under the no-fee constant-product model: `s = sqrt(reserveIn · reserveOut · targetN / targetD) − reserveIn`, capped at our per-side budget. Implementation in `_noFeeSwapInput`. Closed-form via OZ `Math.sqrt + Math.mulDiv`; no binary search, no convergence loop.
2. **Execute the swap directly on the pair** via `pair.swap(amount0Out, amount1Out, address(this), "")`. We read the output from the pair's own fee-aware `getAmountOut` quote and pass it as the output. **Bypasses the router** — HyperSwap's V2 router has no canonical `swapExactTokensForTokens` (see "HyperSwap Router non-standard ABI" above). Same direct-to-pair pattern Zap uses for post-grad user swaps. Implementation in `_pairRebalance`.
3. **Deposit the remaining inventory** via `router.addLiquidity(rest, 1, 1, lpLock, ...)`. The router's `quote()`-based optimal split deposits only the matched-ratio subset; neither side becomes a `min()` donation. Off-ratio remainder stays in `Bonding`. The router's `addLiquidity` IS canonical V2 on HyperSwap (verified selector `0xe8e33700`), so this leg is safe to keep on the router and gets the `quote()` math for free.
```

**File:** packages/contracts/AGENTS.md (L191-200)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:

- **Regime 1/2 don't touch the router.** Even if the V2 router is misbehaving, the empty + donation paths run on direct pair calls.
- **`_pairRebalance` falls back to a direct mint when no swap can run.** `_noFeeSwapInput` may return `s == 0`, or the pair's fee-charging `getAmountOut(s)` may round to zero, against a pre-seed whose swap-output side is dust — `pair.swap` would otherwise revert with `INSUFFICIENT_OUTPUT_AMOUNT`. In either case `_pairRebalance` returns `false`, and `_seedRebalancing` overpowers the dust with a direct `transfer + pair.mint` at the cached `tokensForLP / ltFromPair` ratio (`_seedDirectMint`), opening the pool on-ratio. This is safe specifically because the swap only rounds to zero when the reserves are negligible against this graduation's inventory: the V2 `min()` donation to the attacker's pre-existing LP is then bounded by `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`, which vanishe ... (truncated)
- **`_routerDepositAndDispose` uses `min0=1, min1=1`.** Slippage protection on `addLiquidity` exists to defend against a third party moving the pool ratio between quote and execution; here we set the ratio ourselves in `_pairRebalance` in the same atomic tx, so there's no third party to defend against. The `=1` (rather than `=0`) trips V2's degenerate-ratio guard so the call can't silently land at near-zero.
- **No external dependency on the router slot being correct post-deploy.** `uniswapV2Router` is set at `initialize` time alongside `uniswapV2Factory` and is rejected if zero. There's no live setter — rotation requires a UUPS upgrade so the change is visible on-chain ahead of any in-flight graduation.

Tested end-to-end by the brick-resistance regression tests in `test/TwoPhaseGraduation.t.sol` (notably `test_brick_resistance_frontRun_dust_seed`).
```

**File:** packages/contracts/src/Bonding.sol (L656-695)
```text
    /// @notice Dual graduation triggers: USD (real LT raised × exchangeRate ≥
    ///         threshold) or supply (all curve tokens sold).
    /// @dev    USD trigger: uses STORED `assetReserve` minus the launch-time
    ///         virtual LT reserve (recovered as `Pair.k() / TOTAL_SUPPLY`,
    ///         see `_launchTimeVirtualLtReserve`). Donations to the pair
    ///         move only the live ERC20 balance, not the stored reserve, so
    ///         they are excluded from the threshold.
    ///
    ///         `exchangeRate()` is a view that doesn't settle the LT's
    ///         accrued streaming fee (only mint / redeem / agent checkpoints
    ///         do), so the USD leg can read marginally high and trip the
    ///         threshold a touch early. Bounded by the pending fee,
    ///         one-directional, and the same accepted drift class as the
    ///         launch snapshot (`_deployAndSeed`); the inline post-buy path
    ///         is unaffected (`Zap.buy`'s `mint` checkpoints in the same tx)
    ///         and LP seeding never reads the rate, so the pool still opens
    ///         at the exact curve-close price.
    ///
    ///         Supply trigger: uses live `IPair.tokenBalance()`. This IS an
    ///         `IERC20.balanceOf` read but is donation-resistant in the
    ///         opposite direction — token donations can only INCREASE the
    ///         balance, never satisfy "== 0", and the only path that drains
    ///         tokens out of the pair is the curve buy flow. Donated tokens
    ///         are unconditionally burned by `_prepareGraduationLiquidity`.
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```

**File:** packages/contracts/src/Bonding.sol (L1000-1034)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();

        address lt = info.ltAddress;
        PendingGraduation memory p = $.pendingGraduation[tokenAddress];

        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;

        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
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

**File:** packages/contracts/src/Bonding.sol (L1316-1349)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1498-1506)
```text
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

**File:** packages/contracts/test/NoFeeSwapInput.t.sol (L161-183)
```text
    /// @notice Stress at realistic ceiling: V2 uint112 reserves combined
    ///         with the target-ratio bounds the call site actually
    ///         produces. `targetN` and `targetD` come from `tokensForLP`
    ///         and `ltFromPair` (or vice versa), both bounded above by
    ///         `Token.TOTAL_SUPPLY` (1B * 1e18 ≈ 2^90) in any sensible
    ///         BounceTech LT × token combination, so the discriminant
    ///         `reserveIn * reserveOut * targetN / targetD` stays inside
    ///         uint256 even at the extremes that real graduations can
    ///         actually produce.
    ///
    ///         (Note: `_noFeeSwapInput` would revert under the OZ `mulDiv`
    ///         512-bit-intermediate guard if the intermediate result
    ///         exceeded uint256, e.g. with arbitrary uint128 target ratios
    ///         — but no real call site can construct such inputs because
    ///         `tokensForLP` and `ltFromPair` are bounded by token supply.)
    function test_overflowSafety_atRealisticMax() public view {
        uint256 maxReserve = type(uint112).max;
        uint256 totalSupply = 1_000_000_000 ether; // ~2^90, the largest plausible target
        // Discriminant: 2^224 * 2^90 / 1 = 2^314 — overflows uint256, so
        // pin targetD high enough to bring result back within range.
        // 2^224 * 2^90 / 2^90 = 2^224, fits.
        harness.exposed_noFeeSwapInput(maxReserve, maxReserve, totalSupply, totalSupply, type(uint256).max);
    }
```
