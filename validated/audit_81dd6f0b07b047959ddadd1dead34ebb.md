## Title
Hostile-mint pre-seed can drive `finalizeGraduation`'s LP deposit to a zero-liquidity mint, permanently bricking graduation and freezing curve-raised LT + `LP_RESERVE` tokens — ([File: packages/contracts/src/Bonding.sol], [File: packages/contracts/src/LPLock.sol])

### Summary
CVE‑2020‑10761 is a class of bug where a spec-compliant request that lands exactly on a boundary/size condition triggers an unhandled assertion failure that crashes/DoSes the service. `alt.fun`'s two-phase graduation has an analogous boundary: `Bonding.finalizeGraduation`'s LP-seeding math (`_seedRebalancing` → `_pairRebalance` → `_routerDepositAndDispose`) is *documented* to rely on a 1% budget reservation to guarantee a non-zero LP mint against a hostile pre-seeded HyperSwap V2 pair, but that guarantee is not enforced by any on-chain check. A sufficiently skewed hostile pre-seed (a permissionless, unprivileged front-run) can still drive the final `addLiquidity`/`pair.mint` call to compute `liquidity == 0`. `LPLock.recordLock` explicitly reverts on `amount == 0` (`ZeroAmount`), and `finalizeGraduation`'s cached `pendingGraduation` state never changes between retries, so the revert repeats forever — permanently freezing the token's `ltFromPair` (curve-raised LT) and `tokensForLP`/`LP_RESERVE` allocation inside `Bonding`, with no rescue path.

### Finding Description
`Bonding.finalizeGraduation` [1](#0-0)  is permissionless and calls `_seedUniswapV2Direct`, whose "Regime 3" branch handles a pre-existing hostile-minted HyperSwap V2 pair by rebalancing via a direct `pair.swap` and then depositing the remaining inventory through the V2 router's `addLiquidity` [2](#0-1) .

The rebalance swap is intentionally capped at 99% of the available per-side budget via `_swapBudget`, and the natspec on that function states the 1% reservation is what "guarantees the deposit leg always lands AND mints non-zero LP at the post-swap ratio" [3](#0-2) . That comment itself concedes the failure mode it is trying to prevent: without the cap, `_routerDepositAndDispose` skips `addLiquidity` when `remToken == 0 || remLT == 0`, `finalizeGraduation` ends up with `liquidity = 0`, and the natspec says this "records a zero-sized lock" via `LPLock.recordLock`.

But `LPLock.recordLock` does not silently record a zero-sized lock — it explicitly reverts: [4](#0-3) 
```solidity
function recordLock(address token, address lpPair, uint256 amount) external {
    ...
    if (amount == 0) revert ZeroAmount();
    ...
}
```

The 99%/1% split only bounds the *swap* input; it provides no bound on the deposit-side V2 mint math itself. Uniswap-V2-style `mint()` computes `liquidity = min(amount0 * totalSupply / reserve0, amount1 * totalSupply / reserve1)` (mirrored exactly in the test mock at [5](#0-4) , which itself `require(liquidity > 0, ...)`). An attacker who front-runs `factory.createPair` and self-funds a `pair.mint(attacker)` at an extremely skewed ratio (as already described as the core threat model in `AGENTS.md` [6](#0-5) ) controls both `reserve0/reserve1` and the resulting pre-existing `totalSupply`. Because `_pairRebalance`'s swap is capped by Bonding's *own* finite curve-raised LT / token inventory (`_ltSwapInventory`, `IERC20(tokenAddress).balanceOf(address(this))`) [7](#0-6) , a sufficiently extreme attacker-chosen skew leaves the post-swap pool far enough from the deposit's on-ratio amounts that the router's `pair.mint` liquidity computation floors to `0` (or, in the degenerate case, one side of `remToken`/`remLT` truncates to `0` before the deposit call is even attempted).

Once this happens, `finalizeGraduation` reverts. Because `pendingGraduation[token]` is pinned at the end of phase 1 and never recomputed [8](#0-7) , and the pre-seeded HyperSwap pair's hostile reserves are also static, every subsequent call to `finalizeGraduation` reproduces the exact same `liquidity == 0` outcome and reverts identically. The token is stuck in `Lifecycle.Graduating` permanently — trading is already frozen at that point — and `Bonding` permanently holds the curve-raised `ltFromPair` LT and the `tokensForLP`/`LP_RESERVE` token allocation with no admin override (`LPLock` has no rescue path by design, and `Bonding` has no owner escape hatch for a bricked graduation).

### Impact Explanation
This is a permanent freeze of trader/creator/LP funds: the real LT raised by every buyer on the bonding curve for that token, plus the 250M `LP_RESERVE` tokens earmarked for the LP, become permanently unreachable — no claim, sell, or graduation path exists once `finalizeGraduation` is stuck reverting. This satisfies the "permanent freezing of trader, creator or LP funds" acceptance bar, and is reachable purely through permissionless transactions (`factory.createPair`, `IERC20.transfer`, `pair.mint`, and the normal curve buy that trips the graduation trigger) — no privileged role is required.

### Likelihood Explanation
The attack requires the attacker to self-fund the hostile mint pre-seed at a specific skew — capital-intensive but not privileged, and the `alt.fun` team has already built (and heavily documented) defenses for less-extreme versions of exactly this pre-seed attack class, indicating it is considered a live, in-scope threat. The specific boundary condition here (deposit-side liquidity flooring to zero despite the 99%/1% swap-budget mitigation) is not covered by any of the listed regression suites (`GraduationInvariants.t.sol`, `TwoPhaseGraduation.t.sol`, `NoFeeSwapInput.t.sol`), and the dedicated end-to-end hostile-pre-seed suite (`HostilePreSeed.t.sol`) was explicitly removed post-deployment per the `AGENTS.md` notes [9](#0-8) , so this exact boundary is currently untested.

### Recommendation
Add an explicit floor/guard before calling `LPLock.recordLock` in `finalizeGraduation`: if the computed `liquidity` (or `remToken`/`remLT`) would be zero, fall back to the `_seedDirectMint` path (which does not depend on the router's proportional-split math and always mints against the cached `(tokensForLP, ltFromPair)` directly), the same way `_pairRebalance` already falls back to `_seedDirectMint` when the swap itself rounds to zero. This closes the gap between the documented intent ("always mints non-zero LP") and the actual enforced guarantee.

### Proof of Concept
1. Attacker calls `factory.createPair(token, lt)` on HyperSwap V2 before phase 1 of graduation completes (or even before the token launches, since the pair address is deterministic).
2. Attacker accumulates a large, disproportionate imbalance of `token` (e.g., by buying deep into the curve or acquiring via other means) versus `lt`, then `transfer`s both to the pair and calls `pair.mint(attacker)`, setting `reserve0`, `reserve1`, and `totalSupply` at an extreme skew relative to what the eventual `tokensForLP`/`ltFromPair` graduation amounts will be.
3. The curve graduates normally (`Bonding.buy` crosses the USD or supply trigger, `_enterGraduating` caches `tokensForLP`/`ltFromPair`).
4. Anyone calls `Bonding.finalizeGraduation(token)`. `_seedRebalancing`'s capped rebalance swap (bounded by Bonding's own finite LT/token inventory) cannot fully correct the extreme pre-seed skew; the subsequent `_routerDepositAndDispose` → `router.addLiquidity` → `pair.mint` computes `liquidity == 0` (or `remToken`/`remLT` truncates to `0`).
5. `LPLock.recordLock(token, pair, 0)` reverts with `ZeroAmount`. `finalizeGraduation` reverts. Since `pendingGraduation[token]` and the hostile pair reserves are both static, every retry reproduces the same revert, permanently trapping the curve-raised LT and `LP_RESERVE` tokens in `Bonding`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L934-953)
```text
    /// @dev Phase 1: drain curve, cache LP-bound amounts, freeze trading. Runs
    ///      inline at end of the threshold-crossing buy. Pinning `tokensForLP`
    ///      and `ltFromPair` here (at the last curve price) is what preserves
    ///      the zero-gap invariant across the tx split.
    function _enterGraduating(
        address tokenAddress
    ) internal {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        info.lifecycle = Lifecycle.Graduating;

        (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) =
            _prepareGraduationLiquidity(tokenAddress);

        $.pendingGraduation[tokenAddress] = PendingGraduation({
            tokensForLP: tokensForLP, ltFromPair: ltFromPair, lpBurned: lpBurned, unsoldBurned: unsoldBurned
        });

        emit TokenGraduating(tokenAddress, tokensForLP, ltFromPair, lpBurned, unsoldBurned);
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

**File:** packages/contracts/src/LPLock.sol (L70-85)
```text
    function recordLock(
        address token,
        address lpPair,
        uint256 amount
    ) external {
        LPLockStorage storage $ = _s();
        if (!$.isLocker[msg.sender]) revert NotAuthorized();
        if (lpPair == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        // `lockedAt` is the one-shot sentinel: it is always set to a non-zero
        // timestamp on the first lock, so the guard holds for any `amount`.
        if ($.locks[token].lockedAt != 0) revert AlreadyLocked();
        if (IERC20(lpPair).balanceOf(address(this)) < amount) revert InsufficientLPBalance();
        $.locks[token] = LockInfo({lpPair: lpPair, amount: amount, lockedAt: block.timestamp});
        emit LPLocked(token, lpPair, amount);
    }
```

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L45-71)
```text
    function mint(
        address to
    ) external returns (uint256 liquidity) {
        uint112 reserve0 = _reserve0;
        uint112 reserve1 = _reserve1;

        uint256 balance0 = IERC20(token0).balanceOf(address(this));
        uint256 balance1 = IERC20(token1).balanceOf(address(this));
        uint256 amount0 = balance0 - reserve0;
        uint256 amount1 = balance1 - reserve1;

        uint256 totalSupply_ = totalSupply();
        if (totalSupply_ == 0) {
            liquidity = _sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY;
            _mint(DEAD, MINIMUM_LIQUIDITY);
        } else {
            uint256 liquidity0 = (amount0 * totalSupply_) / reserve0;
            uint256 liquidity1 = (amount1 * totalSupply_) / reserve1;
            liquidity = liquidity0 < liquidity1 ? liquidity0 : liquidity1;
        }
        require(liquidity > 0, "MockPair: INSUFFICIENT_LIQUIDITY_MINTED");

        _mint(to, liquidity);

        _reserve0 = uint112(balance0);
        _reserve1 = uint112(balance1);
    }
```

**File:** packages/contracts/AGENTS.md (L132-149)
```markdown
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

**File:** packages/contracts/AGENTS.md (L223-229)
```markdown
### Tests you MUST re-run if you change any of this

- `test/NoFeeSwapInput.t.sol` — 9 deterministic + 2 fuzz tests on the load-bearing math (degenerate inputs, monotonicity, cap-at-budget, closed-form correctness, overflow safety, the round-down-to-zero input shape that motivated the precheck).
- `test/TwoPhaseGraduation.t.sol` — brick-resistance + phase-1-fits-in-small-block tests, plus the hostile-pre-seed open-at-cached-ratio tests (`test_hostilePreSeed_*`) covering both the dust direct-mint fallback and the meaningful-reserve swap path, must still pass.
- `test/GraduationInvariants.t.sol` — zero-gap, supply conservation, parabola cap. Honest-path properties unchanged by the defense.

The dedicated end-to-end hostile-pre-seed integration suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons after deployment — the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties are no longer enforced by automated tests. If you change any of the graduation / rebalance / deposit code paths, consider re-deriving these properties manually and / or adding targeted regressions for whatever you touch.
```
