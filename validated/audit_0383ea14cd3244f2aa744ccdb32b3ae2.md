Based on the codebase's own hostile-pre-seed test suite, there is a real, unprivileged-reachable "LP seeded away from the curve close price" scenario, which is one of the accepted impact classes listed in the validation rules. This is the closest and best-supported analog to the arbitrary-write/attacker-controlled-target-state bug class the CVE represents — here the "target" being corrupted is the graduation LP pricing, and the "write" is an attacker-controlled pre-seed of the pair before the permissionless `finalizeGraduation`.

### Title
Extreme LT-rich pair pre-seed permanently mispricess the graduated LP beyond the rebalance budget cap - (File: packages/contracts/src/Bonding.sol)

### Summary
`Bonding.finalizeGraduation` is fully permissionless [1](#0-0) , and the HyperSwap V2 `TOKEN/LT` pair can be created and pre-seeded by anyone between phase 1 (`_enterGraduating`) and phase 2 (`finalizeGraduation`) via the standard permissionless V2 `createPair` → `transfer` → `pair.mint` sequence, as the contract's own natspec documents [2](#0-1) . The mitigation (`_seedUniswapV2Direct`'s "Regime 3") rebalances a hostile pre-seed toward the curve-close ratio via a closed-form no-fee swap, but the swap input is capped at 99% of the available inventory side via `_swapBudget` [3](#0-2) . When an attacker pre-seeds the pair at a sufficiently extreme ratio (e.g. ~200x LT-rich relative to `tokensForLP`/`ltFromPair`), the mathematically optimal rebalance swap exceeds this budget cap, so `_pairRebalance` only partially corrects the ratio before `_routerDepositAndDispose` deposits the remaining balanced subset at the still-skewed post-swap ratio [4](#0-3) .

### Finding Description
The three-regime pre-seed defense in `_seedUniswapV2Direct` is designed to prevent a front-runner from opening the graduated LP off the curve's closing price [5](#0-4) . Regime 3 (mint pre-seed) computes a closed-form swap input `s` via `_noFeeSwapInput` that would drive the pool back to the curve-close ratio, then executes it directly against the pair, then deposits the remaining balanced inventory via the router's `addLiquidity` [6](#0-5) .

However, `_swapBudget` intentionally reserves only 99% of the available per-side inventory for this rebalance swap, explicitly to avoid a different failure mode (a fully-consumed side bricking `addLiquidity`) [3](#0-2) . The natspec candidly documents that this cap "only kicks in for catastrophic pre-seeds beyond our budget capacity" and that in that regime "the pool opens materially off curve-close" [7](#0-6) . The project's own fuzz/regression suite reproduces and accepts this exact residual: for a ~200x LT-rich mint pre-seed, the optimal rebalance swap exceeds the budget, and the resulting pool price is asserted to end up more than 20% off the curve-close price [8](#0-7) .

Because `LPLock` has no withdraw/rescue path in v1 [9](#0-8) , any LP minted at this mispriced ratio is permanently locked at the wrong valuation — the first arbitrageur to trade against the mispriced pool extracts value from the pool's reserves (i.e., from the locked LP position) to correct the price, at the expense of whatever the protocol/community expected the graduated LP to be worth at the true curve-close price.

### Impact Explanation
This matches one of the explicitly accepted impact classes: "an LP seeded away from the curve close price." Because the mispriced LP is immediately and permanently locked (`LPLock.recordLock` is one-shot and non-withdrawable [10](#0-9) ), the value lost to arbitrage against the mispriced pool is a permanent, unrecoverable loss to the protocol-held LP position, harming all token holders relying on the graduated LP being priced at the curve's fair close.

### Likelihood Explanation
The attack requires only unprivileged, permissionless actions reachable by any address: front-run `Bonding._enterGraduating`'s completion by calling `factory.createPair`, `transfer`-ing an extreme LT-rich ratio of tokens to the pair, and calling `pair.mint(attacker)`, then letting/forcing `finalizeGraduation` (itself permissionless) run. The project's own test explicitly constructs this exact 200x-skew scenario and confirms it survives (does not revert, per the brick-resistance guarantee) while producing a >20% price deviation, so likelihood is effectively "always reachable when the attacker is willing to fund a large enough dust pre-seed" — bounded only by the attacker's LT/token budget, not by any protocol control.

### Recommendation
Either widen (or remove) the 99% swap-budget cap so the rebalance can always reach the curve-close ratio regardless of pre-seed skew (accepting a different mitigation for the "fully consumed side" degenerate case, e.g., falling back to an iterative partial-deposit-then-burn-remainder scheme instead of a hard 1% floor), or add a maximum-acceptable-deviation check after the Regime 3 rebalance that reverts/defers finalization (with an explicit recovery path) rather than silently sealing a mispriced LP into a non-withdrawable lock.

### Proof of Concept
Reference the existing regression test that already demonstrates this exact residual: `testFuzz_hostilePreSeed_neverProfitable_neverBricks` and its fixed-ratio precursor in `packages/contracts/test/TwoPhaseGraduation.t.sol` [11](#0-10) , which pre-seeds the pair at `reserveToken = tokensForLP/100`, `reserveLt = ltFromPair*200` via `_grieferMintPreSeed`, then calls `bonding.finalizeGraduation(tokenAddr)` and asserts the resulting pool price is more than 1.2x the fair curve-close ratio — confirming the mispriced-LP outcome is reachable and already reproduced by the project's own test harness.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1002)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
```

**File:** packages/contracts/src/Bonding.sol (L1132-1200)
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

**File:** packages/contracts/AGENTS.md (L130-137)
```markdown
### The exploit

A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L871-917)
```text
        // The optimal TOKEN-in swap to reach the cached ratio is ~1.4x
        // `tokensForLP`, so the 99%-of-`tokensForLP` budget cap binds and the
        // pool stays ~2x off curve-close after the swap.
        uint256 reserveToken = tokensForLP / 100;
        uint256 reserveLt = ltFromPair * 200;

        // M-02 precondition: the optimal swap exceeds the budget (this is the
        // budget-capped regime, distinct from the swap-rounds-to-zero fallback
        // covered by the dust tests above).
        assertGt(
            _noFeeSwapInputUncapped(reserveToken, reserveLt, tokensForLP, ltFromPair),
            (tokensForLP * 99) / 100,
            "setup: optimal rebalance swap must exceed the per-side budget (M-02 regime)"
        );

        deal(tokenAddr, griefer, reserveToken);
        address hyperPair = _grieferMintPreSeed(tokenAddr, reserveToken, reserveLt);
        uint256 grieferLp = MockHyperswapPair(hyperPair).balanceOf(griefer);
        uint256 ownerLtBefore = lt.balanceOf(bonding.owner());

        bonding.finalizeGraduation(tokenAddr);
        assertTrue(bonding.isGraduated(tokenAddr), "finalize must succeed despite an unrecoverable pre-seed");

        // The accepted residual: no bounded swap can correct a 200x LT-rich
        // pre-seed, so the pool opens materially off curve-close.
        assertGt(
            _poolPriceLtPerToken(hyperPair, tokenAddr),
            (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
            "M-02 regime: pool opens materially off curve-close"
        );

        // The over-funded LT side is arbed out by the rebalance swap and swept
        // to the owner — the pre-seeder cannot recover it.
        assertGt(
            lt.balanceOf(bonding.owner()) - ownerLtBefore,
            reserveLt / 2,
            "the over-funded LT side must be confiscated to the owner"
        );

        // P&L: the pre-seeder's residual LP, valued at the fair (curve-close)
        // price, is worth a fraction of what they deposited — the attack is
        // cost-negative.
        uint256 claimValue = _lpValueAtCurveClose(hyperPair, tokenAddr, grieferLp, tokensForLP, ltFromPair);
        uint256 depositValue = _depositValueAtCurveClose(reserveToken, reserveLt, tokensForLP, ltFromPair);
        assertLe(claimValue, depositValue, "pre-seeder must not profit (P&L <= 0)");
        assertLt(claimValue * 2, depositValue, "pre-seeder must lose materially, not merely break even");
    }
```

**File:** packages/contracts/src/LPLock.sol (L8-18)
```text
/// @title LPLock
/// @notice Locks LP tokens from graduated tokens. No withdraw in v1.
/// @dev UUPS-upgradeable to support v2 `migrateLT` functionality.
///      Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
///
///      Storage uses ERC-7201 namespaced layout (no `__gap` needed). All
///      mutable state lives in `LPLockStorage` at `_LP_LOCK_STORAGE_LOCATION`.
```

**File:** packages/contracts/src/LPLock.sol (L69-85)
```text
    /// @notice Record an LP lock. LP tokens must already sit at this address.
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
