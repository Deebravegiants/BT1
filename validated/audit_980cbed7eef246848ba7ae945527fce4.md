### Title
Permanent DoS of graduation when the hostile-pre-seed rebalance leaves `remToken == 0 || remLT == 0` — `LPLock.recordLock` bricks `finalizeGraduation` and locks all curve-raised LT/tokens forever - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2016-3991 is a "zero tiles" edge case in `tiffcrop`'s `loadImage`: an unhandled zero-sized input drives the function into an out-of-bounds write instead of a safe abort. The analogous bug class here is a zero-amount edge case that is not defensively handled at the point of consumption, except here the consequence is not memory corruption but a hard, permanent DoS: `_routerDepositAndDispose` can legitimately compute `remToken == 0` or `remLT == 0` after a hostile-pre-seed rebalance, in which case it skips `addLiquidity` entirely and returns `liquidity = 0` [1](#0-0) . `finalizeGraduation` then forwards this `liquidity` straight into `LPLock.recordLock`, which explicitly reverts on `amount == 0` [2](#0-1) , permanently reverting the one and only `finalizeGraduation` call path.

### Finding Description
`finalizeGraduation` is a permissionless, one-shot phase-2 call: it seeds the HyperSwap V2 pair via `_seedUniswapV2Direct`, then unconditionally calls `LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity)` [3](#0-2) . There is no code path in `finalizeGraduation` that skips or retries `recordLock` — it is a hard prerequisite for flipping `lifecycle: Graduating → Graduated`.

`_seedRebalancing` (the hostile-mint-pre-seed regime) attempts to rebalance the attacker-skewed pair via `_pairRebalance`, capped by `_swapBudget` at 99% of the available inventory precisely to guarantee the post-swap deposit leg always has a non-zero amount on both sides — the contract's own comment documents this exact failure mode: *"Without this, an extreme hostile pre-seed... drives the swap [past budget], `_routerDepositAndDispose` then skips `addLiquidity` (`remToken == 0` or `remLT == 0`), `finalizeGraduation` returns `liquidity = 0`, and `LPLock.recordLock(...)` records a zero-sized lock — the attacker's pre-existing LP becomes 100% of the pool"* [4](#0-3) .

However, `LPLock.recordLock` does not "record a zero-sized lock" as the comment assumes — it explicitly reverts with `ZeroAmount` when `amount == 0` [5](#0-4) . This means the documented mitigation's fallback behavior is actually worse than described: rather than "silently" letting the attacker capture 100% of a tiny pool, the transaction reverts entirely, and because `finalizeGraduation` has no alternate branch or recovery path once `_seedUniswapV2Direct` returns `liquidity == 0`, the token is stuck in `Lifecycle.Graduating` forever. No function exists to re-attempt with different parameters, to bypass `recordLock`, or to unwind phase 1 — `pendingGraduation[token]` and the drained curve LT/tokens sitting in `Bonding` become permanently unreachable, since `Lifecycle.Graduating` freezes trading (no `buy`/`sell`) and only `finalizeGraduation` can move the lifecycle forward.

The `_swapBudget` 99% cap is intended to prevent this exact scenario for "extreme" pre-seeds, but the guard is a probabilistic clamp, not a mathematical guarantee against `remToken == 0`/`remLT == 0` in the deposit leg — that leg's actual amounts depend on the router's `quote()`-based optimal split of whatever balances happen to remain after the swap, the fee-adjusted `_pairRebalance` output, and integer rounding across `_noFeeSwapInput`. An attacker who front-runs with a sufficiently pathological reserve ratio and dust-level `remToken`/`remLT` inputs (not necessarily hitting the literal 100%-consumption case the comment describes, but any combination that leaves the router's `quote()` split rounding one side to zero) can still land on `liquidity == 0`.

### Impact Explanation
This is a permanent freezing of funds: once a token enters `Lifecycle.Graduating` via the threshold-crossing buy (`_enterGraduating`), all of the curve's raised LT (`ltFromPair`) and 250M reserved tokens (`LP_RESERVE` minus any burn) sit in `Bonding` awaiting `finalizeGraduation`. If `finalizeGraduation` reverts unconditionally due to `LPLock.recordLock`'s `ZeroAmount` guard, that LT and those tokens — plus every trader's position that was frozen when trading stopped — are permanently stuck, with no owner-only rescue path (the codebase explicitly states `LPLock` has "no withdraw in v1" and `Bonding` itself has no admin escape hatch for a stuck `Graduating` token other than `finalizeGraduation`). This satisfies the "permanent freezing of trader, creator or LP funds" bar in the validation rules.

### Likelihood Explanation
Reaching the vulnerable branch requires only unprivileged, permissionless transactions: (1) front-run `factory.createPair(token, lt)`, (2) `transfer` dust token/LT into the pair and `pair.mint(attacker)` to create a hostile-ratio pre-seed (Regime 3), (3) wait for/trigger the threshold-crossing buy that fires `_enterGraduating`, then (4) call the permissionless `finalizeGraduation`. The attacker fully controls the pre-seed ratio and amounts, so they can search off-chain for a ratio that survives the `_swapBudget` 99% cap yet still drives the router's `addLiquidity` optimal split (or the `_pairRebalance` output) to zero on one side. This is a griefing attack cheap enough (dust-level token/LT amounts, as already demonstrated by the "1 wei + 1 LT" pre-seed cost cited in the codebase's own threat model) to be economically viable against any target token before its graduating buy lands.

### Recommendation
`_routerDepositAndDispose` (and by extension `_seedRebalancing`/`_seedUniswapV2Direct`) must guarantee `liquidity > 0` before `finalizeGraduation` reaches `LPLock.recordLock`, or `finalizeGraduation` must handle a `liquidity == 0` result without reverting the whole transaction (e.g., fall back to `_seedDirectMint` whenever the router-based deposit would leave `remToken == 0 || remLT == 0`, mirroring the existing dust-preseed fallback used elsewhere in `_seedRebalancing`). Alternatively, add an explicit "below-direct-mint-threshold" check ahead of the router deposit leg so the code never depends on the router's `quote()` split rounding favorably, since the current `_swapBudget` 99% cap only bounds the swap's own consumption and does not bound the deposit leg's rounding behavior.

### Proof of Concept
1. Attacker calls `HyperSwapV2Factory.createPair(token, lt)` before phase 1 fires (front-running the anticipated threshold-crossing buy, or immediately after `TokenGraduating` is emitted and before `finalizeGraduation` is called, since phase 2 is a separate permissionless tx).
2. Attacker transfers a carefully chosen dust `tokenAmount` and `ltAmount` to the pair at a ratio/scale designed so that, after `_pairRebalance`'s swap consumes up to 99% of the attacker-controllable budget (`_swapBudget`), the residual `remToken`/`remLT` computed in `_routerDepositAndDispose` is nonzero in `IERC20.balanceOf` terms but the HyperSwap router's `addLiquidity(..., 1, 1, ...)` optimal-split logic (`quote()`-based) still returns `liquidity == 0` due to integer-rounding at the resulting reserve ratio, or alternatively engineers `remToken == 0`/`remLT == 0` directly by exhausting one side in the rebalance swap.
3. Attacker calls `pair.mint(attacker)` to lock in the hostile ratio.
4. Once the target token graduates (phase 1 `_enterGraduating` fires from a normal buy, since the attacker does not need to influence this), anyone calls `Bonding.finalizeGraduation(tokenAddress)`.
5. `_seedUniswapV2Direct` → `_seedRebalancing` → `_routerDepositAndDispose` returns `liquidity == 0`.
6. `finalizeGraduation` calls `LPLock.recordLock(tokenAddress, lpPair, 0)`, which reverts with `LPLock.ZeroAmount()` [5](#0-4) .
7. Every subsequent call to `finalizeGraduation(tokenAddress)` reverts identically (the pre-seed state and cached `pendingGraduation` values are unchanged), permanently freezing the token in `Lifecycle.Graduating` along with all curve-raised LT and reserved tokens held by `Bonding`.

Note: I was unable to fully trace `_noFeeSwapInput`'s exact rounding boundaries within the available context to construct the precise numeric pre-seed ratio that triggers `liquidity == 0` without exceeding the 99% swap-budget cap (the file content beyond line 1500 covering `_noFeeSwapInput`'s full implementation was not returned by the available searches); a background engineering session with full repository access would be needed to derive concrete PoC numbers and add a Foundry test reproducing the exact revert.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1022-1033)
```text
        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
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

**File:** packages/contracts/src/Bonding.sol (L1466-1473)
```text
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
