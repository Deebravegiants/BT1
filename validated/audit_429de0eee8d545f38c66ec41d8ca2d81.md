The bounded fuzz test only exercises `seedMultiple` up to 1000 with one side pinned at exactly `tokensForLP`/`ltFromPair` — it does not test the scenario where `tokensForLP` or `ltFromPair` themselves are tiny (dust-sized), which is the actual precondition for the zero-liquidity brick. This is a real gap, not a proven exploit, so I'm presenting it as a finding with appropriately scoped confidence.

### Title
Griefer-forced zero-liquidity deposit causes `LPLock.recordLock` to revert, permanently bricking `finalizeGraduation` and freezing curve-raised funds - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._routerDepositAndDispose` only calls the HyperSwap router's `addLiquidity` when both `remToken > 0 && remLT > 0`; otherwise `liquidity` stays `0` [1](#0-0) . `finalizeGraduation` unconditionally forwards this `liquidity` value into `LPLock.recordLock(tokenAddress, lpPair, liquidity)` [2](#0-1) , and `LPLock.recordLock` explicitly reverts with `ZeroAmount()` when `amount == 0` [3](#0-2) . Since `finalizeGraduation` is the only path out of `Lifecycle.Graduating` and is meant to be brick-proof by design (`_seedUniswapV2Direct` MUST never revert under any pre-seed shape), a griefer who can force `liquidity == 0` turns a documented "never reverts" invariant into a hard, permanent revert.

### Finding Description
The `_swapBudget` function's own natspec documents this exact failure mode as a known risk that the 99%-swap-cap is supposed to prevent: *"Without this, an extreme hostile pre-seed... drives the unconstrained `_noFeeSwapInput` past our per-side budget, `_pairRebalance` clamps to the full budget, and the swap consumes 100% of one side. `_routerDepositAndDispose` then skips `addLiquidity` (`remToken == 0` or `remLT == 0`), `finalizeGraduation` returns `liquidity = 0`, and `LPLock.recordLock(...)` records a zero-sized lock"* [4](#0-3) .

That comment was written when `LPLock.recordLock` presumably tolerated a zero amount, but the current implementation explicitly guards against it with `if (amount == 0) revert ZeroAmount();` [5](#0-4) . The 1% reservation in `_swapBudget` reduces but does not eliminate the chance of `remToken` or `remLT` rounding to `0`, particularly when:
- `tokensForLP` or `ltFromPair` are themselves tiny. `tokensForLP` is derived as `(ltFromPair * tokenReserve) / assetReserve` [6](#0-5)  and can be small for tokens that graduate via the supply trigger at a near-zero exchange rate (as exercised by `test_inv_supplyTrigger_belowUsdThreshold`), or on the last capped buy (`test_inv_overflowCap_refundsLt`).
- A griefer front-runs `finalizeGraduation` by creating the HyperSwap pair and minting an extreme hostile pre-seed ratio (as in the `M-02`/`testFuzz_hostilePreSeed_neverProfitable_neverBricks` regime), driving `_pairRebalance`'s swap to consume the full 99% budget of the dust-sized side, leaving `1%` of a tiny integer, which truncates to `0` in `_routerDepositAndDispose`.

Because the existing regression coverage (`testFuzz_hostilePreSeed_neverProfitable_neverBricks`) pins one side of the pre-seed at exactly the honest `tokensForLP`/`ltFromPair` value and only fuzzes a `seedMultiple` up to `1000`, it does not probe the dust-`tokensForLP`/dust-`ltFromPair` regime where the 1%-of-budget floor itself rounds to zero. This is the scenario the `_swapBudget` natspec itself calls out as the danger case, but the mitigation (reserving 1%) assumes the budget is large enough that 1% of it is still `≥ 1` — an assumption never proven code-side, and not covered by the fuzz bounds.

### Impact Explanation
If `liquidity == 0` is reached, `LPLock.recordLock` reverts, so `finalizeGraduation` reverts on every call, for every caller, forever — there is no retry path, no alternate finalize function, and no admin rescue (`LPLock` has no withdraw/rescue in v1, and `Bonding` holds no manual override for a token stuck in `Lifecycle.Graduating`). The token is permanently stuck between `Curve` and `Graduated`: trading is frozen (graduating disables `buy`/`sell`), and the entire curve-raised LT (`ltFromPair`, already pulled into `Bonding` via `Router.graduate` in `_prepareGraduationLiquidity`) plus the 250M `LP_RESERVE` tokens are permanently locked in the `Bonding` contract with no way to move them into the pool or back to traders. This is a permanent freezing of trader/creator funds, matching the CVE's assertion-failure/availability-crash class (an internal invariant firing unexpectedly and halting the system) mapped onto alt.fun's actual graduation state machine.

### Likelihood Explanation
The precondition (a token whose `ltFromPair`/`tokensForLP` graduate at a dust size, combined with a griefer's hostile mint pre-seed sized to exhaust the 99% swap budget) is a narrow but realistic edge case: the supply-trigger graduation path and the overflow-cap path both explicitly produce small `ltFromPair`/`tokensForLP` values (both have dedicated tests), and pre-seeding a HyperSwap pair before `finalizeGraduation` is permissionless and cheap (as extensively documented in the "HyperSwap Pre-Seed Defense" section, and already the basis of a fuzzed but incompletely-bounded regression test). No privileged role is required.

### Recommendation
Add a fallback in `finalizeGraduation`/`_routerDepositAndDispose` for the `liquidity == 0` case that does not go through `LPLock.recordLock`'s non-zero-amount guard — e.g., skip `recordLock` entirely (and instead sweep the residual dust to the owner or burn it) when `liquidity == 0`, so `finalizeGraduation` can still complete and flip the lifecycle to `Graduated`. Alternatively, extend `_swapBudget`/`_prepareGraduationLiquidity` with an explicit floor ensuring `tokensForLP`/`ltFromPair` (and hence the reserved 1%) can never round to zero, and add fuzz coverage that specifically drives `tokensForLP`/`ltFromPair` toward dust while pre-seeding at the extreme ratio, to close the gap in `testFuzz_hostilePreSeed_neverProfitable_neverBricks`.

### Proof of Concept
1. Launch a token and drive it to graduation via the supply-exhaustion trigger with `lt.setExchangeRate` crashed to a near-zero rate (as in `test_inv_supplyTrigger_belowUsdThreshold`), producing a small `ltFromPair` and correspondingly small `tokensForLP` in `pendingGraduation`.
2. Before calling `finalizeGraduation`, have a griefer call `hyperswapFactory.createPair(token, lt)`, then `transfer` a hostile ratio of `token`/`lt` sized so that the optimal rebalance swap for the dust-sized side would exceed the budget (mirroring `_grieferMintPreSeed` in `TwoPhaseGraduation.t.sol`), and call `pair.mint(griefer)`.
3. Call `bonding.finalizeGraduation(tokenAddr)`. Trace `_seedRebalancing` → `_pairRebalance` (consuming the full 99%-of-budget swap on the dust side) → `_routerDepositAndDispose`, where `remToken` or `remLT` truncates to `0`, yielding `liquidity == 0`.
4. Observe `LPLock.recordLock(tokenAddress, lpPair, 0)` revert with `ZeroAmount()`, causing `finalizeGraduation` to revert unconditionally on every subsequent call for that token.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1023-1031)
```text
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);
```

**File:** packages/contracts/src/Bonding.sol (L1084-1096)
```text
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
